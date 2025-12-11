import apiClient from './axios'

// ============ 文件型 Prompt 管理 ============

/**
 * 获取所有文件型 prompts（4个）
 * 返回: onboarding, clerk, clerk_over, therapist-general
 */
export const getFilePrompts = async () => {
  const response = await apiClient.get('/api/admin/prompts/files')
  return response.data
}

/**
 * 更新单个文件型 prompt
 * @param {string} key - prompt key (onboarding, clerk, clerk_over, therapist-general)
 * @param {string} content - 新的 prompt 内容
 */
export const updateFilePrompt = async (key, content) => {
  const response = await apiClient.put(`/api/admin/prompts/files/${key}`, { content })
  return response.data
}

// ============ 治疗师 Prompt 管理 ============

/**
 * 获取所有治疗师列表（用于选择器）
 * 返回简化版信息（不包含 prompt）
 */
export const getTherapists = async () => {
  const response = await apiClient.get('/api/therapists')
  return response.data
}

/**
 * 获取治疗师详细信息（包含 prompt）
 * @param {string} id - 治疗师 ID
 */
export const getTherapist = async (id) => {
  const response = await apiClient.get(`/api/therapists/${id}`)
  return response.data
}

/**
 * 更新治疗师 prompt
 * @param {string} id - 治疗师 ID
 * @param {string} prompt - 新的 prompt 内容
 */
export const updateTherapistPrompt = async (id, prompt) => {
  const response = await apiClient.patch(`/api/therapists/${id}`, { prompt })
  return response.data
}

// ============ 旧版 API（已废弃）============

/**
 * @deprecated 使用 getFilePrompts() 代替
 */
export const getPrompts = async () => {
  throw new Error('This API is deprecated. Use getFilePrompts() instead.')
}

/**
 * @deprecated 使用 updateFilePrompt() 代替
 */
export const updatePrompts = async (prompts) => {
  throw new Error('This API is deprecated. Use updateFilePrompt() instead.')
}

// ============ Session 配置管理 ============

/**
 * 获取 Session 时间和轮数控制配置
 * 返回: { suggested_duration_minutes, suggested_turns, reminder_interval }
 */
export const getSessionConfig = async () => {
  const response = await apiClient.get('/api/admin/session-config')
  return response.data
}

/**
 * 更新 Session 时间和轮数控制配置
 * @param {Object} config - 配置对象
 * @param {number} config.suggested_duration_minutes - 建议咨询时长（分钟）
 * @param {number} config.suggested_turns - 建议对话轮数
 * @param {number} config.reminder_interval - 提示间隔（轮）
 */
export const updateSessionConfig = async (config) => {
  const response = await apiClient.put('/api/admin/session-config', config)
  return response.data
}

// ============ 邀请码管理 ============

/**
 * 获取所有邀请码列表
 * 返回: { codes: [ { id, code, is_universal, is_used, used_by_email, used_at, created_at } ] }
 */
export const getInvitationCodes = async () => {
  const response = await apiClient.get('/api/admin/invitation-codes')
  return response.data
}

/**
 * 生成新的邀请码
 * 返回: { id, code, is_universal, is_used, used_by_email, used_at, created_at }
 */
export const createInvitationCode = async () => {
  const response = await apiClient.post('/api/admin/invitation-codes')
  return response.data
}

/**
 * 删除邀请码
 * @param {number} codeId - 邀请码 ID
 */
export const deleteInvitationCodeById = async (codeId) => {
  const response = await apiClient.delete(`/api/admin/invitation-codes/${codeId}`)
  return response.data
}
