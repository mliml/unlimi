# Admin 提示词管理 API 文档

## 📋 概览

管理后台的提示词配置功能，支持两种类型的 prompt 管理：
1. **文件型 Prompt**: 存储在 YAML 文件中的系统提示词（4个）
2. **治疗师 Prompt**: 存储在数据库中的治疗师专属提示词（2个）

---

## 🎯 Tab 结构设计

| Tab Key | Tab 名称 | 数据源 | 获取 API | 更新 API |
|---------|---------|--------|---------|---------|
| `onboarding` | Onboarding | 文件 | `GET /api/admin/prompts/files` | `PUT /api/admin/prompts/files/onboarding` |
| `clerk` | Clerk | 文件 | `GET /api/admin/prompts/files` | `PUT /api/admin/prompts/files/clerk` |
| `clerk_over` | Clerk Over | 文件 | `GET /api/admin/prompts/files` | `PUT /api/admin/prompts/files/clerk_over` |
| `therapist-general` | Therapist General | 文件 | `GET /api/admin/prompts/files` | `PUT /api/admin/prompts/files/therapist-general` |
| `therapist-person` | Therapist Person | 数据库 | 先 `GET /api/therapists` 后 `GET /api/therapists/{id}` | `PATCH /api/therapists/{id}` |

---

## 🔌 API 详细说明

### 一、文件型 Prompt 管理

#### 1. GET `/api/admin/prompts/files` - 获取所有文件型 prompts

**请求：**
```bash
GET /api/admin/prompts/files
```

**响应：**
```json
{
    "prompts": [
        {
            "key": "onboarding",
            "display_name": "Onboarding",
            "content": "你是一位专业的心理咨询引导助手...",
            "file_path": "onboarding_instructions.yaml"
        },
        {
            "key": "clerk",
            "display_name": "Clerk",
            "content": "...",
            "file_path": "clerk_base_instructions.yaml"
        },
        {
            "key": "clerk_over",
            "display_name": "Clerk Over",
            "content": "...",
            "file_path": "clerk_session_over_prompt.yaml"
        },
        {
            "key": "therapist-general",
            "display_name": "Therapist General",
            "content": "...",
            "file_path": "therapist_base_instructions.yaml"
        }
    ]
}
```

**说明：**
- 一次性返回所有 4 个文件型 prompts
- `content` 字段包含完整的 prompt 文本
- 前端可缓存此响应，减少重复请求

---

#### 2. PUT `/api/admin/prompts/files/{key}` - 更新文件型 prompt

**请求：**
```bash
PUT /api/admin/prompts/files/onboarding
Content-Type: application/json

{
    "content": "更新后的 prompt 内容..."
}
```

**响应：**
```json
{
    "success": true,
    "message": "Successfully updated prompt: onboarding",
    "prompt": {
        "key": "onboarding",
        "display_name": "Onboarding",
        "content": "更新后的 prompt 内容...",
        "file_path": "onboarding_instructions.yaml"
    }
}
```

**支持的 key：**
- `onboarding`
- `clerk`
- `clerk_over`
- `therapist-general`

**错误响应：**
```json
// 400 Bad Request - 无效的 key
{
    "detail": "Invalid prompt key: xxx. Valid keys: onboarding, clerk, clerk_over, therapist-general"
}

// 400 Bad Request - 空内容
{
    "detail": "content field is required and cannot be empty"
}

// 500 Internal Server Error - 更新失败
{
    "detail": "Failed to update prompt: onboarding"
}
```

**说明：**
- 更新会自动备份原文件到 `app/config/prompts/backups/` 目录
- 只更新 YAML 文件中的 `system_prompt` 字段，保持 `metadata` 不变
- 更新后会自动清除 PromptLoader 缓存

---

### 二、治疗师 Prompt 管理

#### 3. GET `/api/therapists` - 获取治疗师列表

**请求：**
```bash
GET /api/therapists
```

**响应：**
```json
[
    {
        "id": "01",
        "name": "Dora",
        "age": 35,
        "info": "35岁女性咨询师，精神分析流派"
    },
    {
        "id": "02",
        "name": "Jakkie",
        "age": 38,
        "info": "38岁男性咨询师，人本主义+格式塔流派"
    }
]
```

**说明：**
- 返回简化版信息，**不包含 prompt 字段**
- 用于前端选择器显示：`{id} - {name}`
- 需要 Bearer Token 认证

---

#### 4. GET `/api/therapists/{id}` - 获取治疗师详细信息

**请求：**
```bash
GET /api/therapists/01
```

**响应：**
```json
{
    "id": "01",
    "name": "Dora",
    "age": 35,
    "info": "35岁女性咨询师，精神分析流派",
    "prompt": "你是 Dora，一位35岁的女性咨询师...",
    "created_at": "2025-12-11T00:20:35",
    "updated_at": "2025-12-11T00:20:35"
}
```

**说明：**
- 返回完整信息，**包含 prompt 字段**
- `prompt` 可能为空字符串
- 用于加载治疗师的专属 prompt

---

#### 5. PATCH `/api/therapists/{id}` - 更新治疗师信息

**请求：**
```bash
PATCH /api/therapists/01
Content-Type: application/json

{
    "prompt": "你是 Dora，一位精神分析流派的咨询师..."
}
```

**响应：**
```json
{
    "id": "01",
    "name": "Dora",
    "age": 35,
    "info": "35岁女性咨询师，精神分析流派",
    "prompt": "你是 Dora，一位精神分析流派的咨询师...",
    "created_at": "2025-12-11T00:20:35",
    "updated_at": "2025-12-11T10:00:00"
}
```

**说明：**
- 可以只更新 `prompt` 字段
- 也支持更新其他字段：`name`, `age`, `info`
- `prompt` 允许空字符串
- `updated_at` 自动更新

**错误响应：**
```json
// 404 Not Found
{
    "detail": "Therapist not found"
}
```

---

## 🖥️ 前端实现示例

### 页面初始化

```typescript
// 1. 加载文件型 prompts（用于前 4 个 tab）
const filePromptsResponse = await fetch('/api/admin/prompts/files')
const filePromptsData = await filePromptsResponse.json()
const filePrompts = filePromptsData.prompts

// 2. 加载治疗师列表（用于选择器）
const therapistsResponse = await fetch('/api/therapists', {
    headers: { 'Authorization': `Bearer ${token}` }
})
const therapists = await therapistsResponse.json()

// 缓存数据
setState({ filePrompts, therapists })
```

### Tab 切换逻辑

```typescript
function onTabChange(tabKey: string) {
    if (tabKey === 'therapist-person') {
        // 治疗师 Prompt tab
        setShowTherapistSelector(true)

        // 默认选择第一个治疗师
        const firstTherapist = therapists[0]
        setSelectedTherapistId(firstTherapist.id)

        // 加载该治疗师的完整信息（包含 prompt）
        loadTherapistPrompt(firstTherapist.id)
    } else {
        // 文件型 Prompt tab
        setShowTherapistSelector(false)

        // 从缓存中找到对应的 prompt
        const prompt = filePrompts.find(p => p.key === tabKey)
        setCurrentPrompt(prompt.content)
    }
}
```

### 加载治疗师 Prompt

```typescript
async function loadTherapistPrompt(therapistId: string) {
    const response = await fetch(`/api/therapists/${therapistId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    const therapist = await response.json()

    setCurrentPrompt(therapist.prompt || '')  // 处理空 prompt
}
```

### 治疗师选择器变化

```typescript
function onTherapistChange(therapistId: string) {
    setSelectedTherapistId(therapistId)
    loadTherapistPrompt(therapistId)
}
```

### 保存文件型 Prompt

```typescript
async function saveFilePrompt(key: string, content: string) {
    const response = await fetch(`/api/admin/prompts/files/${key}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content })
    })

    if (response.ok) {
        const result = await response.json()
        message.success(result.message)

        // 更新缓存
        const index = filePrompts.findIndex(p => p.key === key)
        filePrompts[index] = result.prompt
    } else {
        const error = await response.json()
        message.error(error.detail)
    }
}
```

### 保存治疗师 Prompt

```typescript
async function saveTherapistPrompt(therapistId: string, prompt: string) {
    const response = await fetch(`/api/therapists/${therapistId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ prompt })
    })

    if (response.ok) {
        const result = await response.json()
        message.success('保存成功')

        // 可选：更新治疗师列表缓存
        const index = therapists.findIndex(t => t.id === therapistId)
        if (index >= 0) {
            // 注意：therapists 列表中不包含 prompt，无需更新
        }
    } else {
        const error = await response.json()
        message.error(error.detail)
    }
}
```

---

## 🧪 测试命令

### 测试文件型 Prompt API

```bash
# 1. 获取所有文件型 prompts
curl -X GET "http://localhost:8000/api/admin/prompts/files"

# 2. 更新 onboarding prompt
curl -X PUT "http://localhost:8000/api/admin/prompts/files/onboarding" \
  -H "Content-Type: application/json" \
  -d '{"content": "新的 onboarding prompt 内容..."}'

# 3. 更新 clerk prompt
curl -X PUT "http://localhost:8000/api/admin/prompts/files/clerk" \
  -H "Content-Type: application/json" \
  -d '{"content": "新的 clerk prompt..."}'

# 4. 测试无效的 key（应返回 400）
curl -X PUT "http://localhost:8000/api/admin/prompts/files/invalid_key" \
  -H "Content-Type: application/json" \
  -d '{"content": "test"}'
```

### 测试治疗师 Prompt API

```bash
# 先获取 token
TOKEN="your_bearer_token_here"

# 1. 获取治疗师列表
curl -X GET "http://localhost:8000/api/therapists" \
  -H "Authorization: Bearer $TOKEN"

# 2. 获取治疗师 01 的详细信息（包含 prompt）
curl -X GET "http://localhost:8000/api/therapists/01" \
  -H "Authorization: Bearer $TOKEN"

# 3. 更新治疗师 01 的 prompt
curl -X PATCH "http://localhost:8000/api/therapists/01" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你是 Dora，一位精神分析流派的咨询师..."}'

# 4. 更新治疗师 02 的 prompt（允许空字符串）
curl -X PATCH "http://localhost:8000/api/therapists/02" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'
```

---

## 📂 文件结构

### 修改的文件

```
backend/
├── app/
│   ├── services/
│   │   └── prompt_manager.py           # ✏️ 更新配置，新增3个方法
│   ├── schemas/
│   │   └── admin.py                    # ✏️ 新增文件型 prompt schemas
│   └── api/routes/
│       └── admin.py                    # ✏️ 完全重写，删除旧接口，添加新接口
│
├── app/config/prompts/
│   ├── onboarding_instructions.yaml    # ✅ 已存在
│   ├── clerk_base_instructions.yaml    # ✅ 已存在
│   ├── clerk_session_over_prompt.yaml  # ✅ 已存在
│   └── therapist_base_instructions.yaml # ✅ 已存在
│
└── API_PROMPTS_MANAGEMENT.md           # ✨ 新增文档
```

### YAML 文件结构

```yaml
# 所有 prompt 文件都遵循此格式
system_prompt: |
  实际的 prompt 内容...
  多行文本...

metadata:
  description: "提示词描述"
  model: "gpt-4"
  temperature: 0.7
```

**重要：** 更新时只修改 `system_prompt` 字段，`metadata` 保持不变。

---

## ⚠️ 注意事项

### 1. 文件备份机制

每次更新文件型 prompt 时，会自动备份到：
```
app/config/prompts/backups/onboarding_instructions_20251211_100000.yaml
```

### 2. 缓存清理

更新文件型 prompt 后，会自动调用：
```python
prompt_loader.reload()
```
确保新配置立即生效。

### 3. 空 Prompt 处理

- **文件型 Prompt**: 不允许空内容（返回 400）
- **治疗师 Prompt**: 允许空字符串（默认值）

### 4. 权限控制

当前所有接口**暂不处理**权限控制，未来可以添加：
```python
@router.put("/prompts/files/{key}")
async def update_file_prompt(
    prompt_key: str,
    request: FilePromptUpdateRequest,
    current_user: User = Depends(require_admin)  # 添加管理员验证
):
    ...
```

### 5. 并发安全

- 文件更新使用先备份再写入的策略
- 数据库更新使用事务
- 建议未来添加乐观锁（version 字段）

---

## ✅ 已废弃的接口

以下接口已被删除：

| 旧接口 | 状态 | 替代方案 |
|--------|------|---------|
| `GET /api/admin/prompts` | ❌ 已删除 | 使用 `GET /api/admin/prompts/files` |
| `PUT /api/admin/prompts` | ❌ 已删除 | 使用 `PUT /api/admin/prompts/files/{key}` |

---

## 🎯 前端 Tab 实现总结

```
Tab 1: Onboarding
  → 加载: filePrompts.find(p => p.key === 'onboarding')
  → 保存: PUT /api/admin/prompts/files/onboarding

Tab 2: Clerk
  → 加载: filePrompts.find(p => p.key === 'clerk')
  → 保存: PUT /api/admin/prompts/files/clerk

Tab 3: Clerk Over
  → 加载: filePrompts.find(p => p.key === 'clerk_over')
  → 保存: PUT /api/admin/prompts/files/clerk_over

Tab 4: Therapist General
  → 加载: filePrompts.find(p => p.key === 'therapist-general')
  → 保存: PUT /api/admin/prompts/files/therapist-general

Tab 5: Therapist Person
  → 显示选择器: therapists (from GET /api/therapists)
  → 选择治疗师: GET /api/therapists/{id}
  → 保存: PATCH /api/therapists/{id}
```

---

生成时间: 2025-12-11
版本: v1.0
