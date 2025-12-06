# -*- coding: utf-8 -*-
"""
@Time    : 2025/12/06
@Author  : ZhangShenao
@File    : mongodb_checkpointer.py
@Desc    : 基于 MongoDB 的自定义 Checkpointer 实现
"""

from typing import Any, Iterator, Optional, Sequence, Tuple
from contextlib import contextmanager
import pickle
from datetime import datetime, timezone

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
    get_checkpoint_id,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from pymongo import MongoClient, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection


class MongoDBSaver(BaseCheckpointSaver):
    """
    基于 MongoDB 的检查点存储器
    
    实现 BaseCheckpointSaver 接口，将检查点数据持久化到 MongoDB 中。
    支持同步操作，适用于 graph.invoke() 调用。
    
    使用示例:
        ```python
        from mongodb_checkpointer import MongoDBSaver
        
        # 创建 checkpointer
        checkpointer = MongoDBSaver.from_conn_string(
            "mongodb://localhost:27017",
            db_name="langgraph_checkpoints"
        )
        
        # 编译 graph
        graph = workflow.compile(checkpointer=checkpointer)
        ```
    """
    
    client: MongoClient
    db: Database
    checkpoints_collection: Collection
    writes_collection: Collection
    
    def __init__(
        self,
        client: MongoClient,
        db_name: str = "langgraph",
        *,
        serde: Optional[SerializerProtocol] = None,
    ):
        """
        初始化 MongoDB Checkpointer
        
        Args:
            client: MongoDB 客户端实例
            db_name: 数据库名称
            serde: 序列化器，默认使用 JsonPlusSerializer
        """
        super().__init__(serde=serde)
        self.client = client
        self.db = client[db_name]
        self.checkpoints_collection = self.db["checkpoints"]
        self.writes_collection = self.db["checkpoint_writes"]
        
        # 创建索引以提高查询性能
        self._setup_indexes()
    
    def _setup_indexes(self):
        """创建必要的数据库索引"""
        # 检查点集合索引
        self.checkpoints_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1), ("checkpoint_id", DESCENDING)],
            unique=True
        )
        self.checkpoints_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1)],
        )
        
        # 写入集合索引
        self.writes_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1), ("checkpoint_id", 1)],
        )
    
    @classmethod
    def from_conn_string(
        cls,
        conn_string: str,
        db_name: str = "langgraph",
        *,
        serde: Optional[SerializerProtocol] = None,
    ) -> "MongoDBSaver":
        """
        从连接字符串创建 MongoDBSaver 实例
        
        Args:
            conn_string: MongoDB 连接字符串，如 "mongodb://localhost:27017"
            db_name: 数据库名称
            serde: 序列化器
            
        Returns:
            MongoDBSaver 实例
        """
        client = MongoClient(conn_string)
        return cls(client, db_name, serde=serde)
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        try:
            yield self.db
        finally:
            pass  # MongoDB 客户端自动管理连接池
    
    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> bytes:
        """序列化检查点数据"""
        return self.serde.dumps_typed(checkpoint)
    
    def _deserialize_checkpoint(self, data: bytes) -> Checkpoint:
        """反序列化检查点数据"""
        return self.serde.loads_typed(data)
    
    def _serialize_metadata(self, metadata: CheckpointMetadata) -> bytes:
        """序列化元数据"""
        return self.serde.dumps_typed(metadata)
    
    def _deserialize_metadata(self, data: bytes) -> CheckpointMetadata:
        """反序列化元数据"""
        return self.serde.loads_typed(data)
    
    def _serialize_writes(self, writes: Sequence[Tuple[str, Any]]) -> bytes:
        """序列化待处理写入"""
        return self.serde.dumps_typed(writes)
    
    def _deserialize_writes(self, data: bytes) -> list[Tuple[str, Any]]:
        """反序列化待处理写入"""
        return self.serde.loads_typed(data)
    
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        获取检查点元组
        
        根据配置获取检查点，如果指定了 checkpoint_id 则获取特定检查点，
        否则获取该线程的最新检查点。
        
        Args:
            config: 运行配置，包含 thread_id 和可选的 checkpoint_id
            
        Returns:
            CheckpointTuple 或 None
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        # 构建查询条件
        query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
        }
        
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id
        
        # 查询检查点（按 checkpoint_id 降序，获取最新的）
        doc = self.checkpoints_collection.find_one(
            query,
            sort=[("checkpoint_id", DESCENDING)]
        )
        
        if not doc:
            return None
        
        # 反序列化数据
        checkpoint = self._deserialize_checkpoint(doc["checkpoint_data"])
        metadata = self._deserialize_metadata(doc["metadata_data"])
        
        # 获取待处理写入
        pending_writes = self._get_pending_writes(
            thread_id, checkpoint_ns, doc["checkpoint_id"]
        )
        
        # 构建配置
        checkpoint_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": doc["checkpoint_id"],
            }
        }
        
        # 构建父配置
        parent_config = None
        if doc.get("parent_checkpoint_id"):
            parent_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["parent_checkpoint_id"],
                }
            }
        
        return CheckpointTuple(
            config=checkpoint_config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
            pending_writes=pending_writes,
        )
    
    def _get_pending_writes(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str
    ) -> list[Tuple[str, str, Any]]:
        """获取待处理写入"""
        docs = self.writes_collection.find({
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        })
        
        writes = []
        for doc in docs:
            task_id = doc["task_id"]
            channel = doc["channel"]
            value = self.serde.loads_typed(doc["value_data"])
            writes.append((task_id, channel, value))
        
        return writes
    
    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """
        列出检查点历史
        
        按时间倒序返回匹配的检查点列表。
        
        Args:
            config: 运行配置
            filter: 过滤条件
            before: 在此检查点之前
            limit: 返回数量限制
            
        Yields:
            CheckpointTuple 对象
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        
        # 构建查询条件
        query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
        }
        
        # 添加 before 条件
        if before:
            before_checkpoint_id = get_checkpoint_id(before)
            if before_checkpoint_id:
                query["checkpoint_id"] = {"$lt": before_checkpoint_id}
        
        # 添加自定义过滤条件
        if filter:
            for key, value in filter.items():
                query[f"metadata.{key}"] = value
        
        # 执行查询
        cursor = self.checkpoints_collection.find(
            query,
            sort=[("checkpoint_id", DESCENDING)]
        )
        
        if limit:
            cursor = cursor.limit(limit)
        
        for doc in cursor:
            # 反序列化数据
            checkpoint = self._deserialize_checkpoint(doc["checkpoint_data"])
            metadata = self._deserialize_metadata(doc["metadata_data"])
            
            # 获取待处理写入
            pending_writes = self._get_pending_writes(
                thread_id, checkpoint_ns, doc["checkpoint_id"]
            )
            
            # 构建配置
            checkpoint_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["checkpoint_id"],
                }
            }
            
            # 构建父配置
            parent_config = None
            if doc.get("parent_checkpoint_id"):
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": doc["parent_checkpoint_id"],
                    }
                }
            
            yield CheckpointTuple(
                config=checkpoint_config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )
    
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """
        保存检查点
        
        将检查点及其元数据保存到 MongoDB。
        
        Args:
            config: 运行配置
            checkpoint: 检查点数据
            metadata: 检查点元数据
            new_versions: 新版本信息
            
        Returns:
            更新后的配置，包含新的 checkpoint_id
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = get_checkpoint_id(config)
        
        # 序列化数据
        checkpoint_data = self._serialize_checkpoint(checkpoint)
        metadata_data = self._serialize_metadata(metadata)
        
        # 保存到 MongoDB
        doc = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": parent_checkpoint_id,
            "checkpoint_data": checkpoint_data,
            "metadata_data": metadata_data,
            "metadata": dict(metadata) if metadata else {},
            "created_at": datetime.now(timezone.utc),
        }
        
        self.checkpoints_collection.update_one(
            {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            },
            {"$set": doc},
            upsert=True
        )
        
        # 返回新的配置
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }
    
    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """
        保存待处理写入
        
        当节点执行成功但后续节点失败时，保存成功节点的写入，
        以便恢复时不需要重新执行。
        
        Args:
            config: 运行配置
            writes: 写入列表，每项为 (channel, value) 元组
            task_id: 任务 ID
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        if not checkpoint_id:
            return
        
        # 保存每个写入
        for idx, (channel, value) in enumerate(writes):
            doc = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "idx": idx,
                "channel": channel,
                "value_data": self.serde.dumps_typed(value),
                "created_at": datetime.now(timezone.utc),
            }
            
            self.writes_collection.update_one(
                {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                    "task_id": task_id,
                    "idx": idx,
                },
                {"$set": doc},
                upsert=True
            )
    
    def delete_thread(self, thread_id: str) -> None:
        """
        删除线程的所有检查点
        
        Args:
            thread_id: 线程 ID
        """
        self.checkpoints_collection.delete_many({"thread_id": thread_id})
        self.writes_collection.delete_many({"thread_id": thread_id})
    
    def close(self) -> None:
        """关闭 MongoDB 连接"""
        self.client.close()


class AsyncMongoDBSaver(BaseCheckpointSaver):
    """
    基于 MongoDB 的异步检查点存储器
    
    使用 motor 异步驱动，支持 async/await 操作。
    适用于 graph.ainvoke() 调用。
    
    使用示例:
        ```python
        from mongodb_checkpointer import AsyncMongoDBSaver
        
        # 创建异步 checkpointer
        checkpointer = AsyncMongoDBSaver.from_conn_string(
            "mongodb://localhost:27017",
            db_name="langgraph_checkpoints"
        )
        
        # 编译 graph
        graph = workflow.compile(checkpointer=checkpointer)
        
        # 异步调用
        result = await graph.ainvoke(input_data, config=config)
        ```
    """
    
    def __init__(
        self,
        client,
        db_name: str = "langgraph",
        *,
        serde: Optional[SerializerProtocol] = None,
    ):
        """
        初始化异步 MongoDB Checkpointer
        
        Args:
            client: motor 异步 MongoDB 客户端实例
            db_name: 数据库名称
            serde: 序列化器
        """
        super().__init__(serde=serde)
        self.client = client
        self.db = client[db_name]
        self.checkpoints_collection = self.db["checkpoints"]
        self.writes_collection = self.db["checkpoint_writes"]
    
    @classmethod
    def from_conn_string(
        cls,
        conn_string: str,
        db_name: str = "langgraph",
        *,
        serde: Optional[SerializerProtocol] = None,
    ) -> "AsyncMongoDBSaver":
        """
        从连接字符串创建 AsyncMongoDBSaver 实例
        
        Args:
            conn_string: MongoDB 连接字符串
            db_name: 数据库名称
            serde: 序列化器
            
        Returns:
            AsyncMongoDBSaver 实例
        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError:
            raise ImportError(
                "motor 库未安装。请运行: pip install motor"
            )
        
        client = AsyncIOMotorClient(conn_string)
        return cls(client, db_name, serde=serde)
    
    async def setup(self) -> None:
        """创建必要的数据库索引"""
        await self.checkpoints_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1), ("checkpoint_id", DESCENDING)],
            unique=True
        )
        await self.checkpoints_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1)],
        )
        await self.writes_collection.create_index(
            [("thread_id", 1), ("checkpoint_ns", 1), ("checkpoint_id", 1)],
        )
    
    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """异步获取检查点元组"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
        }
        
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id
        
        doc = await self.checkpoints_collection.find_one(
            query,
            sort=[("checkpoint_id", DESCENDING)]
        )
        
        if not doc:
            return None
        
        checkpoint = self.serde.loads_typed(doc["checkpoint_data"])
        metadata = self.serde.loads_typed(doc["metadata_data"])
        
        pending_writes = await self._aget_pending_writes(
            thread_id, checkpoint_ns, doc["checkpoint_id"]
        )
        
        checkpoint_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": doc["checkpoint_id"],
            }
        }
        
        parent_config = None
        if doc.get("parent_checkpoint_id"):
            parent_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["parent_checkpoint_id"],
                }
            }
        
        return CheckpointTuple(
            config=checkpoint_config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
            pending_writes=pending_writes,
        )
    
    async def _aget_pending_writes(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str
    ) -> list[Tuple[str, str, Any]]:
        """异步获取待处理写入"""
        cursor = self.writes_collection.find({
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        })
        
        writes = []
        async for doc in cursor:
            task_id = doc["task_id"]
            channel = doc["channel"]
            value = self.serde.loads_typed(doc["value_data"])
            writes.append((task_id, channel, value))
        
        return writes
    
    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ):
        """异步列出检查点历史"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        
        query = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
        }
        
        if before:
            before_checkpoint_id = get_checkpoint_id(before)
            if before_checkpoint_id:
                query["checkpoint_id"] = {"$lt": before_checkpoint_id}
        
        if filter:
            for key, value in filter.items():
                query[f"metadata.{key}"] = value
        
        cursor = self.checkpoints_collection.find(
            query,
            sort=[("checkpoint_id", DESCENDING)]
        )
        
        if limit:
            cursor = cursor.limit(limit)
        
        async for doc in cursor:
            checkpoint = self.serde.loads_typed(doc["checkpoint_data"])
            metadata = self.serde.loads_typed(doc["metadata_data"])
            
            pending_writes = await self._aget_pending_writes(
                thread_id, checkpoint_ns, doc["checkpoint_id"]
            )
            
            checkpoint_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["checkpoint_id"],
                }
            }
            
            parent_config = None
            if doc.get("parent_checkpoint_id"):
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": doc["parent_checkpoint_id"],
                    }
                }
            
            yield CheckpointTuple(
                config=checkpoint_config,
                checkpoint=checkpoint,
                metadata=metadata,
                parent_config=parent_config,
                pending_writes=pending_writes,
            )
    
    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """异步保存检查点"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = get_checkpoint_id(config)
        
        checkpoint_data = self.serde.dumps_typed(checkpoint)
        metadata_data = self.serde.dumps_typed(metadata)
        
        doc = {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
            "parent_checkpoint_id": parent_checkpoint_id,
            "checkpoint_data": checkpoint_data,
            "metadata_data": metadata_data,
            "metadata": dict(metadata) if metadata else {},
            "created_at": datetime.now(timezone.utc),
        }
        
        await self.checkpoints_collection.update_one(
            {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            },
            {"$set": doc},
            upsert=True
        )
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }
    
    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """异步保存待处理写入"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        
        if not checkpoint_id:
            return
        
        for idx, (channel, value) in enumerate(writes):
            doc = {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "idx": idx,
                "channel": channel,
                "value_data": self.serde.dumps_typed(value),
                "created_at": datetime.now(timezone.utc),
            }
            
            await self.writes_collection.update_one(
                {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                    "task_id": task_id,
                    "idx": idx,
                },
                {"$set": doc},
                upsert=True
            )
    
    # 同步方法的实现（回退到异步）
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """同步获取检查点（不推荐使用）"""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.aget_tuple(config))
    
    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """同步列出检查点（不推荐使用）"""
        import asyncio
        
        async def collect():
            results = []
            async for item in self.alist(config, filter=filter, before=before, limit=limit):
                results.append(item)
            return results
        
        results = asyncio.get_event_loop().run_until_complete(collect())
        return iter(results)
    
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        """同步保存检查点（不推荐使用）"""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.aput(config, checkpoint, metadata, new_versions)
        )
    
    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """同步保存待处理写入（不推荐使用）"""
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            self.aput_writes(config, writes, task_id)
        )
    
    async def adelete_thread(self, thread_id: str) -> None:
        """异步删除线程的所有检查点"""
        await self.checkpoints_collection.delete_many({"thread_id": thread_id})
        await self.writes_collection.delete_many({"thread_id": thread_id})
    
    def close(self) -> None:
        """关闭 MongoDB 连接"""
        self.client.close()

