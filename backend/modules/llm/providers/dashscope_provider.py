#!/usr/bin/env python3
"""
阿里云通义千问DashScope提供商
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse

class DashScopeProvider(BaseLLMProvider):
    """阿里云通义千问DashScope提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = config.get('model', 'qwen-plus')
        self.timeout = config.get('timeout', 30)
        
        if not self.api_key:
            raise ValueError("DashScope API密钥未配置")
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用DashScope聊天完成API
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求数据
            api_messages = self.format_messages(messages)
            
            data = {
                "model": self.model,
                "messages": api_messages,
                "temperature": kwargs.get('temperature', self.temperature),
                "max_tokens": kwargs.get('max_tokens', self.max_tokens)
            }
            
            # 支持工具调用
            tools = kwargs.get('tools')
            if tools:
                data['tools'] = tools
                data['tool_choice'] = kwargs.get('tool_choice', 'auto')
            
            print(f"[DASHSCOPE] 调用模型: {self.model}")
            print(f"[DASHSCOPE] 消息数量: {len(api_messages)}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"DashScope API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            choice = result['choices'][0]
            message = choice['message']
            
            return LLMResponse(
                content=message.get('content', ''),
                model=result.get('model', self.model),
                usage=result.get('usage', {}),
                finish_reason=choice.get('finish_reason', 'stop')
            )
            
        except requests.exceptions.RequestException as e:
            print(f"[DASHSCOPE] 网络请求失败: {e}")
            raise Exception(f"DashScope API连接失败: {e}")
        except Exception as e:
            print(f"[DASHSCOPE] 调用失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查DashScope API是否可用"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            # DashScope没有models端点，直接测试聊天接口
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=test_data, 
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "DashScope"