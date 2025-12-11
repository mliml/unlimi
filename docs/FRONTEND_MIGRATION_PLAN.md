# 前端 Agno 框架适配调整方案

**文档版本**: 1.0
**创建日期**: 2025-12-08
**后端迁移状态**: ✅ 已完成

---

## 📋 概述

本文档详细说明前端适配 Agno 框架后端的所有调整项。后端已完成从传统架构向 Agno Agent 框架的迁移，数据存储从业务表迁移到 Agno 本地存储（PostgreSQL `ai` schema）。

### 核心变化

1. **消息存储格式变化**: 从 `session_messages` 表 → Agno `runs` JSONB 格式
2. **用户记忆变化**: 从 `user_personas` 表 → Agno `memories` 表
3. **API 端点兼容**: 大部分端点无变化，仅数据格式微调

---

## ✅ 无需调整的部分

以下功能**无需前端修改**，后端已做兼容处理：

### 1. 会话管理 API

| API 端点 | 状态 | 说明 |
|---------|------|------|
| `GET /api/sessions/active` | ✅ 无需修改 | 返回格式不变 |
| `POST /api/sessions/start` | ✅ 无需修改 | 返回格式不变 |
| `GET /api/sessions/{id}` | ✅ 无需修改 | 返回格式不变 |
| `POST /api/sessions/{id}/post_message` | ✅ 无需修改 | 请求/响应格式不变 |
| `POST /api/sessions/{id}/end` | ✅ 无需修改 | 返回格式不变 |
| `GET /api/sessions/history` | ✅ 无需修改 | 返回格式不变 |

### 2. Onboarding API

| API 端点 | 状态 | 说明 |
|---------|------|------|
| `GET /api/onboarding/questions` | ✅ 无需修改 | 返回格式不变 |
| `POST /api/onboarding/submit` | ✅ 无需修改 | 请求/响应格式不变 |

### 3. 用户认证 API

| API 端点 | 状态 | 说明 |
|---------|------|------|
| `POST /api/auth/register` | ✅ 无需修改 | 返回格式不变 |
| `POST /api/auth/login` | ✅ 无需修改 | 返回格式不变 |
| `GET /api/me/overview` | ✅ 无需修改 | 返回格式不变 |

---

## 🔧 需要调整的部分

### 调整 1: 消息时间戳格式 ⚠️

**问题**: 后端 `get_session_messages` 返回的 `created_at` 是 Unix timestamp（整数），但前端期望 ISO 日期字符串。

**影响文件**:
- `frontend/src/pages/ConsultPage.vue` (line 84)
- `frontend/src/pages/HistoryPage.vue` (line 139)

#### 后端返回格式

```json
[
  {
    "id": 0,
    "sender": "user",
    "message": "你好",
    "created_at": 1733654719  // ⚠️ Unix timestamp (整数)
  },
  {
    "id": 1,
    "sender": "assistant",
    "message": "你好！很高兴见到你",
    "created_at": 1733654719
  }
]
```

#### 前端当前处理 (ConsultPage.vue:78-85)

```javascript
const backendMessages = response.data || []
messages.value = backendMessages.map(msg => ({
  id: msg.id,
  role: msg.sender === 'user' ? 'user' : 'assistant',
  content: msg.message,
  timestamp: msg.created_at  // ⚠️ 直接使用，需要转换
}))
```

#### 解决方案

**选项 A: 前端统一处理（推荐）**

修改 `ConsultPage.vue` 和 `HistoryPage.vue`:

```javascript
// ConsultPage.vue (line 78-85)
const backendMessages = response.data || []
messages.value = backendMessages.map(msg => ({
  id: msg.id,
  role: msg.sender === 'user' ? 'user' : 'assistant',
  content: msg.message,
  // 统一转换为 ISO 字符串
  timestamp: typeof msg.created_at === 'number'
    ? new Date(msg.created_at * 1000).toISOString()
    : msg.created_at
}))
```

```javascript
// HistoryPage.vue (line 134-140)
const currentMessages = computed(() => {
  return messages.value.map(msg => ({
    id: msg.id,
    role: msg.sender === 'user' ? 'user' : 'assistant',
    content: msg.message,
    // 统一转换为 ISO 字符串
    timestamp: typeof msg.created_at === 'number'
      ? new Date(msg.created_at * 1000).toISOString()
      : msg.created_at
  }))
})
```

**选项 B: 后端统一转换（备选）**

修改后端 `app/schemas/session_message.py`:

```python
class SessionMessageListItem(BaseModel):
    id: int
    sender: str
    message: str
    created_at: Union[datetime, int]  # 允许两种类型

    @validator('created_at', pre=True)
    def convert_timestamp(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v
```

**推荐**: 选项 A，前端处理更灵活，不需要修改后端代码。

---

### 调整 2: InsightsPage 用户画像数据源 ⭐

**问题**: InsightsPage 当前从 `/api/me/profile` 读取 `user_personas` 表数据，但迁移后应该使用 `/api/me/memories` 读取 Agno memories。

**影响文件**:
- `frontend/src/pages/InsightsPage.vue`
- `frontend/src/api/profile.js`

#### 当前实现

**InsightsPage.vue (line 164-182)**:
```javascript
const fetchProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await getUserProfile()  // ⚠️ 调用旧 API
    profileItems.value = data.profiles || []
  } catch (err) {
    console.error('Failed to fetch profile:', err)
    error.value = err.response?.data?.detail || '加载用户画像失败'
  } finally {
    loading.value = false
  }
}
```

**当前 API 返回格式 (`/api/me/profile`)**:
```json
{
  "profiles": [
    {
      "id": 1,
      "content": "用户感到疲惫",
      "confidence": "high",
      "source": "onboarding",
      "updated_at": "2025-12-08T12:00:00"
    }
  ]
}
```

#### 新的 API 返回格式

**新端点**: `GET /api/me/memories`

**返回格式**:
```json
[
  {
    "memory_id": "550e8400-e29b-41d4-a716-446655440000",
    "memory": "用户感到疲惫，希望解决心理问题",
    "topics": ["migration", "persona"],
    "created_at": "2025-12-08T12:00:00",
    "updated_at": "2025-12-08T12:00:00"
  }
]
```

#### 调整步骤

**步骤 1**: 添加新的 API 函数

修改 `frontend/src/api/profile.js`:

```javascript
import axios from './axios'

// 保留旧的 API（兼容性，可选）
export const getUserProfile = async () => {
  const response = await axios.get('/api/me/profile')
  return response.data
}

// ⭐ 新增：获取 Agno memories
export const getUserMemories = async () => {
  const response = await axios.get('/api/me/memories')
  return response.data  // 直接返回数组
}
```

**步骤 2**: 修改 InsightsPage.vue

修改 `frontend/src/pages/InsightsPage.vue`:

```javascript
// Line 156-157: 修改 import
import { ref, onMounted } from 'vue'
import { getUserMemories } from '@/api/profile'  // ⭐ 改用新 API

// Line 164-182: 修改数据获取逻辑
const fetchProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const memories = await getUserMemories()  // ⭐ 调用新 API
    console.log("API raw response:", memories)

    // ⭐ 转换 memories 格式为 profileItems 格式
    profileItems.value = memories.map(m => ({
      id: m.memory_id,  // 使用 memory_id 作为 id
      content: m.memory,  // memory 字段映射到 content
      confidence: 'high',  // Agno memories 暂无 confidence，默认为 high
      source: m.topics.includes('migration') ? 'clerk' : 'clerk',  // 根据 topics 判断
      updated_at: m.updated_at
    }))

    console.log("profileItems after set:", profileItems.value)

  } catch (err) {
    console.error('Failed to fetch memories:', err)
    error.value = err.response?.data?.detail || '加载用户画像失败'
  } finally {
    loading.value = false
  }
}
```

**步骤 3**: 调整 UI 显示逻辑（可选）

如果希望展示 `topics` 信息，可以修改模板:

```vue
<!-- InsightsPage.vue line 79-109 -->
<div v-else class="space-y-3">
  <p class="text-gray-600 mb-4">基于您的咨询记录，我们为您生成了个性化的用户画像。</p>
  <div
    v-for="item in profileItems"
    :key="item.id"
    class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-gray-800 font-medium">{{ item.content }}</p>
        <div class="flex items-center mt-2 space-x-3 text-sm text-gray-500">
          <span class="flex items-center">
            <span class="mr-1">来源:</span>
            <span class="font-medium">{{ getSourceLabel(item.source) }}</span>
          </span>
          <!-- ⭐ 新增：显示 topics -->
          <span v-if="item.topics && item.topics.length > 0" class="flex items-center">
            <span class="mr-1">标签:</span>
            <span class="font-medium">{{ item.topics.join(', ') }}</span>
          </span>
          <span class="flex items-center">
            <span class="mr-1">更新:</span>
            <span>{{ formatDate(item.updated_at) }}</span>
          </span>
        </div>
      </div>
      <span
        :class="[
          'ml-4 px-3 py-1 rounded-full text-xs font-medium',
          getConfidenceBadgeClass(item.confidence)
        ]"
      >
        {{ getConfidenceLabel(item.confidence) }}
      </span>
    </div>
  </div>
</div>
```

同时在转换逻辑中保留 `topics`:

```javascript
profileItems.value = memories.map(m => ({
  id: m.memory_id,
  content: m.memory,
  confidence: 'high',
  source: m.topics.includes('migration') ? 'clerk' : 'clerk',
  updated_at: m.updated_at,
  topics: m.topics  // ⭐ 新增：保留 topics
}))
```

---

## 📝 测试检查清单

### 基础功能测试

- [ ] **用户注册/登录**: 测试用户认证流程
- [ ] **Onboarding**: 测试初始问卷流程
- [ ] **开始会话**: 测试创建新会话
- [ ] **发送消息**: 测试对话功能，检查消息正确显示
- [ ] **查看消息历史**: 测试 ConsultPage 加载历史消息
- [ ] **结束会话**: 测试结束会话并生成总结
- [ ] **查看历史会话**: 测试 HistoryPage 显示过往会话列表
- [ ] **查看会话详情**: 测试 HistoryPage 显示消息、回顾、关键事件

### 新功能测试

- [ ] **用户画像 (InsightsPage)**:
  - 测试加载 Agno memories
  - 确认数据正确显示
  - 检查时间格式正确
  - 验证 topics 显示（如果实现）

### 时间格式测试

- [ ] **ConsultPage 消息时间**: 确认时间戳正确转换和显示
- [ ] **HistoryPage 消息时间**: 确认时间戳正确转换和显示
- [ ] **MessageList 组件**: 确认 formatTime 函数正常工作

---

## 🔄 迁移步骤建议

### 阶段 1: 时间格式修复（必须）

**优先级**: 🔴 高
**预计时间**: 30 分钟

1. 修改 `ConsultPage.vue` 的 `loadExistingSession` 函数
2. 修改 `HistoryPage.vue` 的 `currentMessages` computed 属性
3. 测试消息时间显示是否正常

### 阶段 2: 用户画像迁移（推荐）

**优先级**: 🟡 中
**预计时间**: 1 小时

1. 修改 `profile.js` 添加 `getUserMemories` 函数
2. 修改 `InsightsPage.vue` 调用新 API
3. 测试用户画像页面显示
4. （可选）添加 topics 显示

### 阶段 3: 全面测试（必须）

**优先级**: 🔴 高
**预计时间**: 2 小时

1. 按照测试检查清单逐项测试
2. 修复发现的问题
3. 验证所有功能正常

---

## 📊 数据格式对比

### 消息数据格式

#### 旧格式 (session_messages 表)
```json
{
  "id": 1,
  "sender": "user",
  "message": "你好",
  "created_at": "2025-12-08T12:00:00"  // ISO datetime 字符串
}
```

#### 新格式 (Agno runs)
```json
{
  "id": 0,
  "sender": "user",
  "message": "你好",
  "created_at": 1733654719  // Unix timestamp (秒)
}
```

**区别**: `created_at` 从 ISO 字符串变为 Unix timestamp

---

### 用户画像数据格式

#### 旧格式 (user_personas 表)
```json
{
  "profiles": [
    {
      "id": 1,
      "content": "用户感到疲惫",
      "confidence": "high",
      "source": "onboarding",
      "updated_at": "2025-12-08T12:00:00"
    }
  ]
}
```

#### 新格式 (Agno memories)
```json
[
  {
    "memory_id": "550e8400-e29b-41d4-a716-446655440000",
    "memory": "用户感到疲惫，希望解决心理问题",
    "topics": ["migration", "persona"],
    "created_at": "2025-12-08T12:00:00",
    "updated_at": "2025-12-08T12:00:00"
  }
]
```

**区别**:
- `id` (int) → `memory_id` (UUID string)
- `content` → `memory`
- 新增 `topics` (array)
- 新增 `created_at`
- 移除 `confidence` 和 `source` 字段

---

## 🛡️ 回退方案

如果新版本出现问题，可以暂时回退到旧 API：

### 临时回退步骤

1. **InsightsPage**: 将 `getUserMemories()` 改回 `getUserProfile()`
2. **后端**: 保留 `/api/me/profile` 端点（已保留，读取 `user_personas` 表）

### 注意事项

- 旧表 `user_personas` 和 `session_messages` 已迁移但**保留在数据库中**
- 可以在确认无问题后再删除旧表
- 建议运行 1-2 周后再删除旧表

---

## 🔗 相关文档

- [后端迁移完成报告](../backend/MIGRATION_COMPLETE.md)
- [Agno 框架技术指南](../backend/AGNO_GUIDE.md)
- [后端 API 变更文档](../backend/API_CHANGES.md)

---

## ❓ 常见问题

### Q1: 为什么消息的 `created_at` 是整数而不是日期字符串？

**A**: Agno 框架在 `runs` JSONB 字段中存储时间戳为 Unix timestamp（秒）。为了与 Agno 原生格式保持一致，后端直接返回整数。前端需要转换为 Date 对象或 ISO 字符串。

### Q2: 旧的用户画像数据会丢失吗？

**A**: 不会。旧的 `user_personas` 已迁移到 `agno_memories` 表。旧表也保留在数据库中作为备份。

### Q3: 如果前端不做调整会怎样？

**A**:
- **消息时间**: 可能显示为 Unix timestamp 数字，而非格式化的时间
- **用户画像**: 会继续显示旧表数据，但新生成的 memories 不会显示

### Q4: 必须立即完成调整吗？

**A**:
- **时间格式修复**: 建议尽快完成，影响用户体验
- **用户画像迁移**: 可以延后，但新 memories 不会显示在 InsightsPage

### Q5: 如何验证调整成功？

**A**:
1. 完成一次完整的咨询会话
2. 检查 ConsultPage 和 HistoryPage 的消息时间显示正确
3. 检查 InsightsPage 显示的是 Agno memories
4. 在 Chrome DevTools Network 中查看 API 响应格式

---

## 📞 技术支持

如有问题，请查看：
1. 后端日志: `backend/logs/app.log`
2. 浏览器控制台错误
3. Network 面板查看 API 响应

或联系后端开发团队。

---

**文档维护**: Backend Team
**最后更新**: 2025-12-08
