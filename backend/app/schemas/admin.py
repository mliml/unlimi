"""
Admin API Schemas

管理后台相关的数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# ============ 提示词配置相关 ============

class PromptMetadata(BaseModel):
    """提示词元数据"""
    description: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    version: Optional[str] = None


class PromptConfig(BaseModel):
    """单个提示词配置"""
    name: str = Field(..., description="提示词名称，如 clerk_onboarding_prompt")
    display_name: str = Field(..., description="显示名称，如 Clerk - 问卷分析提示词")
    file_path: str = Field(..., description="YAML 文件路径")
    content: str = Field(..., description="提示词内容")
    metadata: PromptMetadata = Field(default_factory=PromptMetadata, description="元数据")


class PromptsListResponse(BaseModel):
    """获取提示词列表的响应"""
    prompts: List[PromptConfig] = Field(..., description="提示词配置列表")


class PromptUpdateItem(BaseModel):
    """单个提示词更新项"""
    name: str = Field(..., description="提示词名称")
    content: str = Field(..., min_length=1, description="提示词内容，不能为空")
    metadata: Optional[Dict] = Field(default=None, description="元数据（可选）")


class PromptsUpdateRequest(BaseModel):
    """批量更新提示词的请求"""
    prompts: List[PromptUpdateItem] = Field(..., min_items=1, description="要更新的提示词列表")


class PromptsUpdateResponse(BaseModel):
    """批量更新提示词的响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    updated_count: int = Field(..., description="成功更新的数量")
    failed_count: int = Field(default=0, description="失败的数量")


# ============ 文件型 Prompt（新版）============

class FilePromptItem(BaseModel):
    """单个文件型 prompt"""
    key: str = Field(..., description="Prompt key (onboarding, clerk, clerk_over, therapist-general)")
    display_name: str = Field(..., description="显示名称")
    content: str = Field(..., description="Prompt 内容")
    file_path: str = Field(..., description="YAML 文件路径")


class FilePromptsResponse(BaseModel):
    """获取所有文件型 prompts 响应"""
    prompts: List[FilePromptItem] = Field(..., description="文件型 prompt 列表")


class FilePromptUpdateRequest(BaseModel):
    """更新文件型 prompt 请求"""
    content: str = Field(..., min_length=1, description="新的 prompt 内容，不能为空")


class FilePromptUpdateResponse(BaseModel):
    """更新文件型 prompt 响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    prompt: FilePromptItem = Field(..., description="更新后的 prompt 信息")


# ============ Session 配置相关 ============

class SessionConfigResponse(BaseModel):
    """获取 Session 配置的响应"""
    suggested_duration_minutes: int = Field(..., description="建议咨询时长（分钟）")
    suggested_turns: int = Field(..., description="建议对话轮数")
    reminder_interval: int = Field(..., description="超时后每N轮提示一次")


class SessionConfigUpdateRequest(BaseModel):
    """更新 Session 配置的请求"""
    suggested_duration_minutes: int = Field(..., ge=1, le=120, description="建议咨询时长（分钟），1-120")
    suggested_turns: int = Field(..., ge=1, le=200, description="建议对话轮数，1-200")
    reminder_interval: int = Field(..., ge=1, le=10, description="提示间隔（轮），1-10")


class SessionConfigUpdateResponse(BaseModel):
    """更新 Session 配置的响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    config: SessionConfigResponse = Field(..., description="更新后的配置")
