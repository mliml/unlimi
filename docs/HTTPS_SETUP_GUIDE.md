# HTTPS 配置指南

本指南介绍如何为 UnLimi 项目配置 HTTPS 证书和自动续期。

---

## 📋 前置条件

在开始之前，请确保：

1. ✅ **域名已解析到服务器**
   - 域名：`www.unlimi.top`
   - A 记录指向服务器 IP：`207.148.69.40`
   - DNS 解析已生效（可通过 `ping www.unlimi.top` 测试）

2. ✅ **服务器防火墙开放端口**
   ```bash
   # 开放 HTTP 和 HTTPS 端口
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw reload
   ```

3. ✅ **项目已部署**
   - Docker 和 Docker Compose 已安装
   - 项目代码已克隆到服务器

---

## 🚀 首次配置 HTTPS

### 第一步：配置邮箱地址

编辑 `init-letsencrypt.sh` 脚本，修改邮箱地址：

```bash
vim init-letsencrypt.sh
```

找到这一行：
```bash
EMAIL="your-email@example.com"  # Replace with your email
```

修改为你的真实邮箱（用于接收证书过期提醒）：
```bash
EMAIL="your-email@example.com"  # 改成你的邮箱
```

### 第二步：运行初始化脚本

```bash
# 确保在项目根目录
cd /opt/unlimi

# 赋予执行权限
chmod +x init-letsencrypt.sh

# 运行初始化脚本
./init-letsencrypt.sh
```

脚本会自动执行以下操作：
1. 创建证书目录
2. 下载推荐的 TLS 参数
3. 创建临时证书启动 nginx
4. 向 Let's Encrypt 请求真实证书
5. 重新加载 nginx 使用真实证书

### 第三步：验证 HTTPS

```bash
# 检查证书状态
docker compose run --rm certbot certificates

# 访问网站测试
curl -I https://www.unlimi.top
```

浏览器访问 `https://www.unlimi.top`，应该看到：
- 🔒 绿色锁标志
- 证书有效期 90 天
- 自动重定向从 HTTP 到 HTTPS

---

## 🔄 自动续期

### 自动续期机制

系统已配置**自动续期**，无需手动操作：

- **Certbot 容器**：每 12 小时检查一次证书
- **证书有效期**：90 天
- **自动续期时机**：证书剩余 30 天时自动续期
- **Nginx 重载**：每 6 小时重载一次以应用新证书

### 检查续期状态

```bash
# 查看 Certbot 日志
docker compose logs certbot

# 手动测试续期（不会真正续期）
docker compose run --rm certbot renew --dry-run
```

### 手动续期

如果需要手动触发续期：

```bash
# 手动续期所有证书
docker compose run --rm certbot renew

# 续期后重载 nginx
docker compose exec frontend nginx -s reload
```

---

## 📁 证书文件位置

证书文件存储在宿主机的 `certbot` 目录：

```
unlimi/
├── certbot/
│   ├── conf/              # 证书配置
│   │   ├── live/
│   │   │   └── www.unlimi.top/
│   │   │       ├── fullchain.pem   # 完整证书链
│   │   │       ├── privkey.pem     # 私钥
│   │   │       ├── cert.pem        # 证书
│   │   │       └── chain.pem       # 中间证书
│   │   ├── archive/       # 证书历史版本
│   │   └── renewal/       # 续期配置
│   └── www/               # ACME 挑战文件
```

**重要提示**：
- ⚠️ `certbot/conf/` 目录包含私钥，需要妥善保管
- ⚠️ 不要将 `certbot/conf/` 提交到 Git（已在 `.gitignore` 中）
- ✅ 建议定期备份此目录

---

## 🔧 常见配置

### 添加多个域名

如果需要支持多个域名（如 `unlimi.top` 和 `www.unlimi.top`）：

1. 修改 `init-letsencrypt.sh`：
```bash
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d www.unlimi.top \
    -d unlimi.top  # 添加额外域名
```

2. 修改 `frontend/nginx.conf`：
```nginx
server {
    listen 443 ssl http2;
    server_name www.unlimi.top unlimi.top;  # 添加额外域名
    # ...
}
```

### 使用测试证书

首次配置时，可以使用 Let's Encrypt 的测试环境（避免触发速率限制）：

```bash
# 编辑 init-letsencrypt.sh
vim init-letsencrypt.sh

# 修改这一行
STAGING=1  # 改成 1 使用测试环境
```

测试成功后再改回 `STAGING=0` 获取正式证书。

---

## 🚨 故障排查

### 问题 1：证书请求失败

**错误信息**：
```
Challenge failed for domain www.unlimi.top
```

**解决方案**：
1. 检查域名解析是否正确：
```bash
ping www.unlimi.top
nslookup www.unlimi.top
```

2. 检查防火墙是否开放 80 端口：
```bash
ufw status
curl http://www.unlimi.top/.well-known/acme-challenge/test
```

3. 检查 nginx 是否正常运行：
```bash
docker compose ps frontend
docker compose logs frontend
```

### 问题 2：nginx 启动失败

**错误信息**：
```
nginx: [emerg] cannot load certificate
```

**解决方案**：
1. 检查证书文件是否存在：
```bash
ls -la certbot/conf/live/www.unlimi.top/
```

2. 重新运行初始化脚本：
```bash
./init-letsencrypt.sh
```

### 问题 3：自动续期失败

**错误信息**：
```
Cert not yet due for renewal
```

这不是错误！表示证书还没到续期时间（剩余 > 30 天）。

**检查续期配置**：
```bash
# 查看证书详情
docker compose run --rm certbot certificates

# 测试续期流程
docker compose run --rm certbot renew --dry-run
```

### 问题 4：浏览器显示证书不安全

**可能原因**：
1. 使用了测试证书（Staging）
2. 证书过期
3. 域名不匹配

**解决方案**：
```bash
# 检查证书状态
docker compose run --rm certbot certificates

# 重新获取证书
docker compose run --rm certbot delete --cert-name www.unlimi.top
./init-letsencrypt.sh
```

---

## 📊 证书信息

- **颁发机构**：Let's Encrypt
- **有效期**：90 天
- **自动续期**：证书剩余 30 天时
- **支持的协议**：TLS 1.2, TLS 1.3
- **加密套件**：HIGH（高强度加密）
- **HSTS**：已启用（1 年）

---

## 🔐 安全建议

1. **定期检查证书**
```bash
# 添加到 crontab
0 0 * * 0 cd /opt/unlimi && docker compose run --rm certbot certificates | mail -s "SSL Certificate Status" your-email@example.com
```

2. **备份证书**
```bash
# 定期备份证书目录
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz certbot/conf/
```

3. **监控续期日志**
```bash
# 查看最近的续期尝试
docker compose logs certbot --tail 100
```

4. **使用强密码**
   - 确保 `.env` 文件中的密码足够强
   - 不要在公开仓库中提交敏感信息

---

## 🔄 更新部署

### 标准部署（保留证书）

使用 `deploy.sh` 脚本更新代码时，证书**不会**被删除：

```bash
./deploy.sh
```

证书目录（`certbot/`）是持久化的，更新部署不会影响。

### 完全重建（保留证书）

即使使用 `redeploy.sh`，证书目录也在宿主机上，不会被删除：

```bash
./redeploy.sh
```

**注意**：如果手动删除了 `certbot/` 目录，需要重新运行 `init-letsencrypt.sh`。

---

## 📞 常见问题

**Q: Let's Encrypt 有速率限制吗？**
A: 是的，每个域名每周最多 5 次失败请求。建议先用 `STAGING=1` 测试。

**Q: 证书快过期会通知我吗？**
A: 会。Let's Encrypt 会向你的邮箱发送过期提醒（剩余 20 天、10 天、1 天）。

**Q: 可以使用通配符证书吗？**
A: 可以，但需要 DNS 验证而非 HTTP 验证。需要修改配置使用 `dns-01` 挑战。

**Q: 证书续期需要停机吗？**
A: 不需要。Certbot 使用 webroot 方式续期，服务持续运行。

**Q: 如何撤销证书？**
```bash
docker compose run --rm certbot revoke --cert-path /etc/letsencrypt/live/www.unlimi.top/cert.pem
```

---

## 📚 参考资源

- [Let's Encrypt 官方文档](https://letsencrypt.org/docs/)
- [Certbot 用户指南](https://certbot.eff.org/docs/)
- [Nginx SSL 配置最佳实践](https://ssl-config.mozilla.org/)
- [SSL Labs 测试工具](https://www.ssllabs.com/ssltest/)

---

## ✅ 配置清单

部署 HTTPS 完成后，请确认：

- [ ] 域名解析正确 (`ping www.unlimi.top`)
- [ ] 防火墙开放 80 和 443 端口
- [ ] 证书获取成功 (`docker compose run --rm certbot certificates`)
- [ ] HTTPS 访问正常 (`curl -I https://www.unlimi.top`)
- [ ] HTTP 自动重定向到 HTTPS
- [ ] 浏览器显示绿色锁标志
- [ ] 自动续期配置生效 (`docker compose logs certbot`)
- [ ] `.env` 文件中 `VITE_API_URL` 使用 HTTPS

---

**祝你部署顺利！** 🎉

如有问题，请查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 或提交 Issue。
