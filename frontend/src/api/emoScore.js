import axios from './axios'

/**
 * 获取最新的情绪评估数据
 * @returns {Promise} 返回最新的情绪评估数据
 */
export const getLatestEmoScore = async () => {
  try {
    const response = await axios.get('/api/emo-score/latest')
    return response.data
  } catch (error) {
    // 如果是 404，说明还没有数据
    if (error.response && error.response.status === 404) {
      return null
    }
    throw error
  }
}

/**
 * 获取情绪评估历史列表
 * @param {string} source - 可选，筛选评估来源 (onboarding/session)
 * @returns {Promise} 返回评估历史列表
 */
export const getEmoScoreList = async (source = null) => {
  const params = source ? { source } : {}
  const response = await axios.get('/api/emo-score/list', { params })
  return response.data
}

/**
 * 创建新的情绪评估记录
 * @param {Object} data - 评估数据
 * @returns {Promise} 返回创建的评估记录
 */
export const createEmoScore = async (data) => {
  const response = await axios.post('/api/emo-score/', data)
  return response.data
}
