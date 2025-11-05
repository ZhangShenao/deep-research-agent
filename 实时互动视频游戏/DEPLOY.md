# Linux服务器部署指南

本文档提供在Linux服务器上部署实时互动视频游戏的完整步骤。

## 目录

1. [安装Docker](#1-安装docker)
2. [配置项目](#2-配置项目)
3. [构建和运行Docker容器](#3-构建和运行docker容器)
4. [配置Nginx反向代理](#4-配置nginx反向代理)
5. [验证部署](#5-验证部署)

---

## 1. 安装Docker

### 1.1 更新系统包

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.2 安装必要的依赖

```bash
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

### 1.3 添加Docker官方GPG密钥

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### 1.4 设置Docker仓库

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 1.5 安装Docker Engine

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
```

### 1.6 验证Docker安装

```bash
sudo docker --version
sudo docker run hello-world
```

### 1.7 将当前用户添加到docker组（可选，避免每次使用sudo）

```bash
sudo usermod -aG docker $USER
newgrp docker
```

**注意：** 添加用户到docker组后，需要重新登录或使用 `newgrp docker` 使更改生效。

### 1.8 配置Docker开机自启

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## 2. 配置项目

### 2.1 克隆或上传项目到服务器

```bash
# 如果使用git
git clone <your-repo-url>
cd realtime-video-game

# 或者直接上传项目文件到服务器
```

### 2.2 创建环境变量文件

在项目根目录创建 `.env` 文件：

```bash
cd 实时互动视频游戏
nano .env
```

添加以下内容：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API配置（用于Sora2）
OPENAI_API_KEY=your_openai_api_key_here

# Gemini API配置（可选，用于封面图生成）
GEMINI_API_KEY=your_gemini_api_key_here
```

**重要：** 请替换为你的实际API密钥。

### 2.3 确保数据目录权限

```bash
mkdir -p data
chmod 755 data
```

---

## 3. 构建和运行Docker容器

### 3.1 构建Docker镜像

```bash
# 进入项目目录
cd 实时互动视频游戏

# 构建镜像
docker build -t realtime-video-game:latest .
```

### 3.2 运行容器

```bash
# 运行容器（使用.env文件）
docker run -d \
  --name realtime-video-game \
  --restart unless-stopped \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  realtime-video-game:latest
```

**或者手动指定环境变量：**

```bash
docker run -d \
  --name realtime-video-game \
  --restart unless-stopped \
  -p 8501:8501 \
  -e DEEPSEEK_API_KEY=your_deepseek_api_key \
  -e DEEPSEEK_BASE_URL=https://api.deepseek.com \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e GEMINI_API_KEY=your_gemini_api_key \
  -v $(pwd)/data:/app/data \
  realtime-video-game:latest
```

### 3.3 常用Docker命令

```bash
# 查看容器状态
docker ps | grep realtime-video-game

# 查看日志
docker logs -f realtime-video-game

# 停止容器
docker stop realtime-video-game

# 启动容器
docker start realtime-video-game

# 重启容器
docker restart realtime-video-game

# 删除容器
docker rm realtime-video-game

# 删除镜像
docker rmi realtime-video-game:latest
```

---

## 4. 配置Nginx反向代理

### 4.1 安装Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### 4.2 复制Nginx配置文件

```bash
sudo cp nginx.conf /etc/nginx/sites-available/realtime-video-game
```

### 4.3 编辑配置文件

```bash
sudo nano /etc/nginx/sites-available/realtime-video-game
```

修改以下内容：
- `server_name`: 改为你的域名或IP地址
- 如果使用IP地址，可以改为 `server_name _;`

### 4.4 创建软链接启用站点

```bash
sudo ln -s /etc/nginx/sites-available/realtime-video-game /etc/nginx/sites-enabled/
```

### 4.5 测试Nginx配置

```bash
sudo nginx -t
```

### 4.6 重启Nginx

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 4.7 配置防火墙（如果使用UFW）

```bash
# 允许HTTP和HTTPS
sudo ufw allow 'Nginx Full'

# 或者只允许HTTP
sudo ufw allow 'Nginx HTTP'
```

---

## 5. 验证部署

### 5.1 检查Docker容器状态

```bash
docker ps | grep realtime-video-game
```

应该看到容器正在运行。

### 5.2 检查应用日志

```bash
docker logs realtime-video-game
```

### 5.3 检查应用健康状态

```bash
curl http://localhost:8501/_stcore/health
```

应该返回 `{"status":"ok"}` 或类似响应。

### 5.4 访问应用

在浏览器中访问：
- 直接访问：`http://your-server-ip:8501`
- 通过Nginx代理：`http://your-domain.com/realtime-video-game/`

### 5.5 常见问题排查

#### 问题1：容器无法启动

```bash
# 查看详细日志
docker logs realtime-video-game

# 检查容器状态
docker ps -a | grep realtime-video-game

# 检查环境变量是否正确
docker exec realtime-video-game env | grep API_KEY

# 如果容器不存在，检查镜像是否构建成功
docker images | grep realtime-video-game
```

#### 问题2：Nginx 502 Bad Gateway

```bash
# 检查应用是否运行
docker ps | grep realtime-video-game

# 检查端口是否正确
netstat -tlnp | grep 8501

# 检查Nginx错误日志
sudo tail -f /var/log/nginx/realtime-video-game-error.log
```

#### 问题3：无法访问应用

```bash
# 检查防火墙
sudo ufw status

# 检查Nginx配置
sudo nginx -t

# 检查Nginx访问日志
sudo tail -f /var/log/nginx/realtime-video-game-access.log
```

---

## 6. 维护和更新

### 6.1 更新应用

```bash
# 停止并删除旧容器
docker stop realtime-video-game
docker rm realtime-video-game

# 拉取最新代码（如果使用git）
git pull

# 重新构建镜像
docker build -t realtime-video-game:latest .

# 启动新容器
docker run -d \
  --name realtime-video-game \
  --restart unless-stopped \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  realtime-video-game:latest
```

### 6.2 查看资源使用

```bash
docker stats realtime-video-game
```

### 6.3 备份数据

```bash
# 备份data目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### 6.4 清理旧镜像和容器

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理所有停止的容器
docker container prune -f
```

---

## 7. 安全建议

1. **使用HTTPS**：配置SSL证书，启用HTTPS访问
2. **防火墙**：只开放必要的端口（80, 443）
3. **API密钥安全**：不要将 `.env` 文件提交到版本控制系统
4. **定期更新**：保持系统和Docker镜像更新
5. **访问控制**：考虑添加Nginx基本认证或IP白名单

---

## 8. 性能优化

1. **增加容器资源限制**：使用 `docker run` 时添加 `--memory` 和 `--cpus` 参数限制资源
2. **使用Nginx缓存**：对静态资源启用缓存
3. **监控日志**：定期检查日志文件大小
4. **数据库优化**：如果未来需要数据库，考虑使用外部数据库

示例：限制容器内存和CPU使用
```bash
docker run -d \
  --name realtime-video-game \
  --restart unless-stopped \
  --memory="2g" \
  --cpus="2.0" \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  realtime-video-game:latest
```

---

## 联系和支持

如有问题，请查看项目README或提交Issue。

