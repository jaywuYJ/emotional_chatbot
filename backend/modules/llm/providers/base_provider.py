#!/usr/bin/env python3
"""
LLM提供商基类
定义统一的接口，支持不同的LLM服务
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMMessage:
    """统一的消息格式"""
    role: str  # system, user, assistant
    content: str

@dataclass
class LLMResponse:
    """统一的响应格式"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', 'default')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 1000)
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            LLMResponse: 统一的响应格式
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass
    
    def format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """将统一消息格式转换为API格式"""
        return [{"role": msg.role, "content": msg.content} for msg in messages]