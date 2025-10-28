# 启动SearXNG容器（使用官方镜像）

``` shell
docker run -d --name searxng \
--cap-drop ALL \
--cap-add CHOWN \
--cap-add SETGID \
--cap-add SETUID \
--log-driver json-file \
--log-opt max-size=1m \
--log-opt max-file=1 \
-p 18080:8080 \
-v /Users/zsa/apps/searxng/data:/etc/searxng:rw \
searxng/searxng:latest
```

访问本地地址：http://localhost:18080/
