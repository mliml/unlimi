# UnLimi 生产环境部署指南

## 📋 部署前检查清单

### 1. 服务器要求
- [ ] Ubuntu 20.04+ 或类似 Linux 发行版
- [ ] 已安装 Docker 和 Docker Compose
- [ ] 开放端口 80 (HTTP) 和 443 (HTTPS)
- [ ] 域名已解析到服务器 IP

### 2. 代码准备
- [ ] 已提交所有本地更改到 Git
- [ ] 已推送到远程仓库（main 分支）

### 3. 配置文件
- [ ] 已创建并配置 `.env` 文件
- [ ] 已配置 SSL 证书（或准备获取 Let's Encrypt 证书）

---

## 🚀 部署步骤

### 步骤 1: 提交并推送代码

在**本地**运行：

```bash
cd /Users/mliml/Web/unlimi

# 检查当前状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "feat: refactor frontend into landing and app"

# 推送到远程
git push origin main
```

### 步骤 2: 登录服务器

```bash
# SSH 登录到你的服务器
ssh your-username@your-server-ip
```

### 步骤 3: 拉取最新代码

在**服务器**上运行：

```bash
cd /path/to/unlimi

# 拉取最新代码
git pull origin main
```

### 步骤 4: 检查配置文件

```bash
# 确保 .env 文件存在且配置正确
cat .env

# 如果不存在，从示例创建
cp .env.example .env
nano .env  # 编辑配置
```

**重要配置项：**
```bash
DB_PASSWORD=your_secure_db_password
SECRET_KEY=your_very_long_secret_key
OPENAI_API_KEY=sk-your-openai-api-key
VITE_API_URL=https://www.unlimi.top
```

### 步骤 5: 首次部署（如果需要 SSL 证书）

如果这是首次部署且需要获取 SSL 证书：

```bash
# 运行 Let's Encrypt 初始化脚本
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh
```

### 步骤 6: 执行部署

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

部署脚本会自动：
1. ✅ 验证配置
2. ✅ 构建 Backend 镜像
3. ✅ 构建 Frontend 镜像（包含 landing 和 app）
4. ✅ 重启所有服务
5. ✅ 显示服务状态

### 步骤 7: 验证部署

部署完成后，验证以下内容：

```bash
# 检查所有容器状态
docker compose ps

# 查看日志
docker compose logs -f frontend
docker compose logs -f backend

# 检查 Nginx 配置
docker compose exec frontend nginx -t
```

**浏览器测试：**
- [ ] https://www.unlimi.top/ (Landing Page)
- [ ] https://www.unlimi.top/auth/login (登录页)
- [ ] https://www.unlimi.top/auth/register (注册页)
- [ ] https://www.unlimi.top/app/overview (主应用)

---

## 🔧 常见问题排查

### 问题 1: 容器启动失败

```bash
# 查看详细日志
docker compose logs frontend
docker compose logs backend

# 重新构建并启动
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 问题 2: SSL 证书问题

```bash
# 检查证书状态
docker compose exec certbot certbot certificates

# 手动更新证书
docker compose exec certbot certbot renew
```

### 问题 3: 数据库连接失败

```bash
# 检查数据库容器
docker compose logs postgres

# 检查数据库连接
docker compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

### 问题 4: 前端页面 404

```bash
# 检查 nginx 容器中的文件
docker compose exec frontend ls -la /usr/share/nginx/html/landing
docker compose exec frontend ls -la /usr/share/nginx/html/app

# 检查 nginx 配置
docker compose exec frontend cat /etc/nginx/conf.d/default.conf
```

---

## 📊 监控和维护

### 查看日志

```bash
# 实时查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f postgres

# 查看最近 100 行日志
docker compose logs --tail 100 backend
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart frontend
docker compose restart backend
```

### 停止服务

```bash
# 停止所有服务（保留数据）
docker compose down

# 停止并删除所有数据（危险操作！）
docker compose down -v
```

---

## 🔄 后续更新部署

当你有代码更新时：

```bash
# 在本地提交并推送
git add .
git commit -m "your commit message"
git push origin main

# 在服务器上运行
cd /path/to/unlimi
./deploy.sh
```

---

## 📝 重要提醒

1. **数据备份**：定期备份数据库
   ```bash
   docker compose exec postgres pg_dump -U unlimi_user unlimi > backup_$(date +%Y%m%d).sql
   ```

2. **SSL 证书自动更新**：certbot 容器会每 12 小时检查一次证书更新

3. **日志清理**：定期清理 Docker 日志
   ```bash
   docker system prune -a
   ```

4. **安全性**：
   - 定期更新 `.env` 中的密钥
   - 确保服务器防火墙配置正确
   - 只开放必要的端口（80, 443, 22）

---

## 🆘 紧急回滚

如果部署出现严重问题需要回滚：

```bash
# 切换到上一个稳定版本
git log  # 查看提交历史
git checkout <previous-commit-hash>

# 重新部署
./deploy.sh

# 恢复到最新
git checkout main
```
