#!/usr/bin/env python3
"""
Gemini LLM提供商
支持Google Gemini API
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base_provider import BaseLLMProvider, LLMMessage, LLMResponse

class GeminiProvider(BaseLLMProvider):
    """Gemini LLM提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://generativelanguage.googleapis.com')
        self.model = config.get('model', 'gemini-pro')
        self.timeout = config.get('timeout', 60)
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
    
    def chat_completion_sync(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Gemini聊天完成API（同步版本）
        """
        try:
            # Gemini API需要特殊的消息格式
            contents = []
            system_instruction = ""
            
            for msg in messages:
                if msg.role == "system":
                    # Gemini将system消息作为systemInstruction
                    system_instruction += msg.content + "\n"
                else:
                    # Gemini使用"user"和"model"而不是"user"和"assistant"
                    role = "user" if msg.role == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg.content}]
                    })
            
            data = {
                "contents": contents,
                "generationConfig": {
                    "temperature": kwargs.get('temperature', self.temperature),
                    "maxOutputTokens": kwargs.get('max_tokens', self.max_tokens),
                }
            }
            
            # 如果有system消息，添加到请求中
            if system_instruction.strip():
                data["systemInstruction"] = {
                    "parts": [{"text": system_instruction.strip()}]
                }
            
            print(f"[GEMINI] 调用模型: {self.model}")
            print(f"[GEMINI] 消息数量: {len(contents)}")
            
            # 发送请求
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Gemini API错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 解析响应
            content = ""
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            content += part["text"]
            
            # Gemini的token使用情况
            usage_metadata = result.get('usageMetadata', {})
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": usage_metadata.get('promptTokenCount', 0),
                    "completion_tokens": usage_metadata.get('candidatesTokenCount', 0),
                    "total_tokens": usage_metadata.get('totalTokenCount', 0)
                },
                finish_reason=result.get('candidates', [{}])[0].get('finishReason', 'STOP') if result.get('candidates') else 'STOP'
            )
            
        except requests.exceptions.RequestException as e:
            print(f"[GEMINI] 网络请求失败: {e}")
            raise Exception(f"Gemini连接失败: {e}")
        except Exception as e:
            print(f"[GEMINI] 调用失败: {e}")
            raise
    
    async def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用Gemini聊天完成API（异步版本）
        """
        # 直接调用同步版本
        return self.chat_completion_sync(messages, **kwargs)
    
    def is_available(self) -> bool:
        """检查Gemini是否可用"""
        try:
            # 发送一个简单的测试请求
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            
            test_data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": "test"}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 1
                }
            }
            
            response = requests.post(
                url,
                json=test_data,
                timeout=10
            )
            
            return response.status_code in [200, 400]  # 400也算可用，只是参数问题
        except:
            return False
    
    def get_provider_name(self) -> str:
        return "Gemini"