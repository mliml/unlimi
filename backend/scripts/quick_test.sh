#!/bin/bash
# 快速测试脚本 - 测试 Agno 集成后的核心功能

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}AI Therapy Backend - 快速测试${NC}"
echo -e "${GREEN}====================================${NC}\n"

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ] && ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "${RED}错误：OPENAI_API_KEY 未设置${NC}"
    echo "请在 .env 文件中设置你的 OpenAI API key"
    exit 1
fi

BASE_URL="http://localhost:8000/api"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="Test123456"

echo -e "${YELLOW}测试邮箱: $TEST_EMAIL${NC}\n"

# 1. 注册用户
echo -e "${GREEN}1. 注册新用户...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

echo "$REGISTER_RESPONSE" | jq '.'

# 2. 登录获取 token
echo -e "\n${GREEN}2. 登录获取 token...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}登录失败！${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Token 获取成功${NC}"

# 3. Onboarding
echo -e "\n${GREEN}3. 测试 Onboarding API...${NC}"
echo "3.1 获取问题..."
curl -s -X GET "$BASE_URL/onboarding/questions" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n3.2 提交答案（ClerkAgent 生成 UserContext）..."
ONBOARDING_RESPONSE=$(curl -s -X POST "$BASE_URL/onboarding/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": 1, "answer": "我想改善焦虑情绪，学会更好地管理压力"},
      {"question_id": 2, "answer": "工作压力很大，经常感到疲惫和不安"},
      {"question_id": 3, "answer": "温柔、支持型，能够倾听我的感受"}
    ]
  }')

echo "$ONBOARDING_RESPONSE" | jq '.'

SUCCESS=$(echo "$ONBOARDING_RESPONSE" | jq -r '.success')
if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✓ Onboarding 完成${NC}"
else
    echo -e "${RED}✗ Onboarding 失败${NC}"
    exit 1
fi

# 4. 创建会话
echo -e "\n${GREEN}4. 创建新会话...${NC}"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions/start" \
  -H "Authorization: Bearer $TOKEN")

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# 5. 发送消息
echo -e "\n${GREEN}5. 发送消息（TherapistAgent 回复）...${NC}"
echo "5.1 第一条消息..."
MSG1=$(curl -s -X POST "$BASE_URL/sessions/$SESSION_ID/post_message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，我今天感觉很焦虑，不知道该怎么办"}')

echo "$MSG1" | jq -r '.reply'

echo -e "\n5.2 第二条消息..."
MSG2=$(curl -s -X POST "$BASE_URL/sessions/$SESSION_ID/post_message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "主要是工作上的事情，老板给的压力特别大"}')

echo "$MSG2" | jq -r '.reply'

# 6. 获取消息历史
echo -e "\n${GREEN}6. 获取会话消息历史...${NC}"
MESSAGES=$(curl -s -X GET "$BASE_URL/sessions/$SESSION_ID/get_messages" \
  -H "Authorization: Bearer $TOKEN")

MESSAGE_COUNT=$(echo "$MESSAGES" | jq 'length')
echo -e "${GREEN}✓ 共 $MESSAGE_COUNT 条消息${NC}"
echo "$MESSAGES" | jq '.[].message' | head -10

# 7. 结束会话
echo -e "\n${GREEN}7. 结束会话（ClerkAgent 生成总结）...${NC}"
END_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions/$SESSION_ID/end" \
  -H "Authorization: Bearer $TOKEN")

echo "$END_RESPONSE" | jq '.'

# 8. 获取用户 memories
echo -e "\n${GREEN}8. 获取用户 Memories...${NC}"
MEMORIES=$(curl -s -X GET "$BASE_URL/users/me/memories" \
  -H "Authorization: Bearer $TOKEN")

MEMORY_COUNT=$(echo "$MEMORIES" | jq 'length')
echo -e "${GREEN}✓ 共 $MEMORY_COUNT 个 memories${NC}"

if [ "$MEMORY_COUNT" -gt 0 ]; then
    echo "$MEMORIES" | jq '.[0:3]'  # 显示前 3 个
fi

# 9. 检查会话历史
echo -e "\n${GREEN}9. 检查会话历史...${NC}"
HISTORY=$(curl -s -X GET "$BASE_URL/sessions/history" \
  -H "Authorization: Bearer $TOKEN")

echo "$HISTORY" | jq '.'

# 总结
echo -e "\n${GREEN}====================================${NC}"
echo -e "${GREEN}✓ 所有测试完成！${NC}"
echo -e "${GREEN}====================================${NC}"
echo -e "\n测试账号信息："
echo -e "  Email: ${YELLOW}$TEST_EMAIL${NC}"
echo -e "  Password: ${YELLOW}$TEST_PASSWORD${NC}"
echo -e "  Session ID: ${YELLOW}$SESSION_ID${NC}"
