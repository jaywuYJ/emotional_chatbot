#!/usr/bin/env python3
"""
Ollama本地LLM提供商
支持本地部署的Ollama模型
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse

class OllamaProvider(BaseLLMProvider):
    """Ollama本地LLM提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'qwen2.5:8b')
        self.timeout = config.get('timeout', 60)
    
    def chat_completion_sync(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Ollama聊天完成API（同步版本）
        """
        try:
            # 构建请求数据
            api_messages = self.format_messages(messages)
            
            data = {
                "model": self.model,
                "messages": api_messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.temperature),
                    "num_predict": kwargs.get('max_tokens', self.max_tokens),
                }
            }
            
            print(f"[OLLAMA] 调用模型: {self.model}")
            print(f"[OLLAMA] 消息数量: {len(api_messages)}")
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 解析响应
            content = result.get('message', {}).get('content', '')
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": result.get('prompt_eval_count', 0),
                    "completion_tokens": result.get('eval_count', 0),
                    "total_tokens": result.get('prompt_eval_count', 0) + result.get('eval_count', 0)
                },
                finish_reason=result.get('done_reason', 'stop')
            )
            
        except requests.exceptions.RequestException as e:
            print(f"[OLLAMA] 网络请求失败: {e}")
            raise Exception(f"Ollama连接失败: {e}")
        except Exception as e:
            print(f"[OLLAMA] 调用失败: {e}")
            raise
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Ollama聊天完成API（异步版本）
        """
        # 直接调用同步版本
        return self.chat_completion_sync(messages, **kwargs)
    
    def is_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "Ollama"
    
    def list_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []