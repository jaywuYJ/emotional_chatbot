#!/usr/bin/env python3
"""
Claude LLM提供商
支持Anthropic Claude API
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse

class ClaudeProvider(BaseLLMProvider):
    """Claude LLM提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.anthropic.com')
        self.model = config.get('model', 'claude-3-haiku-20240307')
        self.timeout = config.get('timeout', 60)
        
        if not self.api_key:
            raise ValueError("Claude API key is required")
    
    def chat_completion_sync(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Claude聊天完成API（同步版本）
        """
        try:
            # Claude API需要特殊的消息格式
            api_messages = []
            system_message = ""
            
            for msg in messages:
                if msg.role == "system":
                    # Claude将system消息单独处理
                    system_message += msg.content + "\n"
                else:
                    api_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            data = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": kwargs.get('max_tokens', self.max_tokens),
                "temperature": kwargs.get('temperature', self.temperature)
            }
            
            # 如果有system消息，添加到请求中
            if system_message.strip():
                data["system"] = system_message.strip()
            
            print(f"[CLAUDE] 调用模型: {self.model}")
            print(f"[CLAUDE] 消息数量: {len(api_messages)}")
            
            # 发送请求
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/messages",
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Claude API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 解析响应
            content = ""
            if "content" in result and result["content"]:
                # Claude返回的content是一个数组
                for item in result["content"]:
                    if item.get("type") == "text":
                        content += item.get("text", "")
            
            usage = result.get('usage', {})
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": usage.get('input_tokens', 0),
                    "completion_tokens": usage.get('output_tokens', 0),
                    "total_tokens": usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                },
                finish_reason=result.get('stop_reason', 'stop')
            )
            
        except requests.exceptions.RequestException as e:
            print(f"[CLAUDE] 网络请求失败: {e}")
            raise Exception(f"Claude连接失败: {e}")
        except Exception as e:
            print(f"[CLAUDE] 调用失败: {e}")
            raise
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Claude聊天完成API（异步版本）
        """
        # 直接调用同步版本
        return self.chat_completion_sync(messages, **kwargs)
    
    def is_available(self) -> bool:
        """检查Claude是否可用"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # 发送一个简单的测试请求
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            response = requests.post(
                f"{self.base_url}/v1/messages",
                json=test_data,
                headers=headers,
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400也算可用，只是参数问题
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "Claude"