#!/usr/bin/env python3
"""
DeepSeek LLM提供商
支持DeepSeek API
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = config.get('model', 'deepseek-chat')
        self.timeout = config.get('timeout', 60)
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
    
    def chat_completion_sync(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用DeepSeek聊天完成API（同步版本）
        """
        try:
            # 构建请求数据
            api_messages = self.format_messages(messages)
            
            data = {
                "model": self.model,
                "messages": api_messages,
                "temperature": kwargs.get('temperature', self.temperature),
                "max_tokens": kwargs.get('max_tokens', self.max_tokens),
                "stream": False
            }
            
            print(f"[DEEPSEEK] 调用模型: {self.model}")
            print(f"[DEEPSEEK] 消息数量: {len(api_messages)}")
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 解析响应
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": usage.get('total_tokens', 0)
                },
                finish_reason=choice.get('finish_reason', 'stop')
            )
            
        except requests.exceptions.RequestException as e:
            print(f"[DEEPSEEK] 网络请求失败: {e}")
            raise Exception(f"DeepSeek连接失败: {e}")
        except Exception as e:
            print(f"[DEEPSEEK] 调用失败: {e}")
            raise
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用DeepSeek聊天完成API（异步版本）
        """
        # 直接调用同步版本
        return self.chat_completion_sync(messages, **kwargs)
    
    def is_available(self) -> bool:
        """检查DeepSeek是否可用"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送一个简单的测试请求
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=test_data,
                headers=headers,
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400也算可用，只是参数问题
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "DeepSeek"