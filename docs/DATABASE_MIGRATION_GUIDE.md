# 数据库迁移指南 (Alembic)

## 📌 核心原则

- **唯一真理来源**: 模型定义 (`backend/app/db/models/*.py`)
- **执行途径**: Alembic 迁移文件 (`backend/alembic/versions/*.py`)
- **禁止操作**: 永远不要使用 `Base.metadata.create_all()`

---

## 🔄 标准工作流程

### 1. 添加/修改数据库字段

```bash
# 1. 修改模型文件
vim backend/app/db/models/user.py
# 添加新字段: phone = Column(String, nullable=True)

# 2. 生成迁移文件
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "add phone field to users"

# 3. 检查生成的迁移文件
cat alembic/versions/[新生成的文件].py
# 确认 upgrade() 和 downgrade() 正确

# 4. 应用迁移
alembic upgrade head

# 5. 测试功能
# 启动应用，测试新字段

# 6. 提交到 Git
git add app/db/models/user.py alembic/versions/*.py
git commit -m "feat: add phone field to users"
git push
```

### 2. 拉取代码后更新数据库

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 应用新的迁移
cd backend
source venv/bin/activate
alembic upgrade head

# 3. 重启应用
```

### 3. 检查迁移状态

```bash
cd backend
source venv/bin/activate

# 查看当前数据库版本
alembic current

# 查看所有迁移历史
alembic history

# 查看待应用的迁移
alembic heads
```

---

## ⚠️ 常见问题

### Q1: 本地数据库结构和服务器不一致怎么办？

**方案 A: 无重要数据（推荐）**
```bash
# 删除本地数据库
# PostgreSQL:
dropdb unlimi_local
createdb unlimi_local

# SQLite:
rm backend/app.db

# 重新应用所有迁移
alembic upgrade head
```

**方案 B: 有重要数据**
```bash
# 1. 备份数据
pg_dump unlimi_local > backup.sql

# 2. 删除并重建数据库
dropdb unlimi_local
createdb unlimi_local
alembic upgrade head

# 3. 手动导入需要的数据
psql unlimi_local < backup_filtered.sql
```

### Q2: autogenerate 没有检测到我的修改？

**可能原因：**
- Alembic 的 `env.py` 没有导入你的模型
- 模型文件语法错误

**解决方法：**
```python
# 检查 backend/alembic/env.py
from app.db.models import (
    User,
    Session,
    # ... 确保所有模型都被导入
)
```

### Q3: 迁移文件冲突（多人开发）

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 如果有迁移冲突，查看所有 heads
alembic heads

# 3. 合并多个 heads（如果有多个分支）
alembic merge [revision1] [revision2] -m "merge migrations"

# 4. 应用迁移
alembic upgrade head
```

### Q4: 需要回滚迁移

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade [revision_id]

# 回滚所有迁移
alembic downgrade base
```

---

## 🚫 禁止操作

### ❌ 不要使用 create_all()
```python
# ❌ 错误
from app.db.database import Base, engine
Base.metadata.create_all(bind=engine)

# ✅ 正确
# 使用 alembic upgrade head
```

### ❌ 不要手动编写完整的迁移文件
```bash
# ❌ 错误
alembic revision -m "my changes"
# 然后手动写 upgrade() 函数

# ✅ 正确
alembic revision --autogenerate -m "my changes"
# 然后审查自动生成的代码
```

### ❌ 不要直接在数据库中修改表结构
```sql
-- ❌ 不要在 pgAdmin 或 psql 中直接执行
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- ✅ 应该修改模型，然后生成迁移
```

### ❌ 不要跳过迁移文件的 Git 提交
```bash
# ❌ 错误
git add app/db/models/user.py
git commit -m "add phone field"
# 忘记提交 alembic/versions/*.py

# ✅ 正确
git add app/db/models/user.py alembic/versions/*.py
git commit -m "feat: add phone field to users"
```

---

## 📚 最佳实践

### 1. 迁移消息命名规范
```bash
# 添加功能
alembic revision --autogenerate -m "add phone and address fields to users"

# 修改字段
alembic revision --autogenerate -m "change email field to unique in users"

# 删除功能
alembic revision --autogenerate -m "remove deprecated fields from sessions"

# 修复问题
alembic revision --autogenerate -m "fix foreign key constraint in user_contexts"
```

### 2. 审查自动生成的迁移

Alembic 的 `--autogenerate` 不是 100% 准确，需要人工审查：

```python
# 检查这些内容：
# ✅ 表名、字段名是否正确
# ✅ 数据类型是否匹配
# ✅ nullable、default、unique 等约束是否正确
# ✅ 外键关系是否正确
# ✅ 索引是否需要
# ✅ downgrade() 函数是否能正确回滚
```

### 3. 测试迁移

```bash
# 测试升级
alembic upgrade head

# 测试回滚
alembic downgrade -1

# 再次升级确认
alembic upgrade head
```

### 4. 生产环境部署

在 `docker-compose.yml` 中已配置：
```yaml
backend:
  command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

这确保每次容器启动时自动应用最新迁移。

---

## 🎯 快速参考

| 操作 | 命令 |
|------|------|
| 生成迁移 | `alembic revision --autogenerate -m "message"` |
| 应用迁移 | `alembic upgrade head` |
| 回滚一次 | `alembic downgrade -1` |
| 查看当前版本 | `alembic current` |
| 查看历史 | `alembic history` |
| 查看待应用 | `alembic heads` |
| 回滚所有 | `alembic downgrade base` |

---

## 📞 遇到问题？

1. 查看 Alembic 日志输出
2. 检查 `alembic/env.py` 是否导入了所有模型
3. 确认数据库连接配置正确 (`DATABASE_URL`)
4. 查看 [Alembic 官方文档](https://alembic.sqlalchemy.org/)
