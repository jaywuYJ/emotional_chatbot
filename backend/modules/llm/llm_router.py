#!/usr/bin/env python3
"""
LLM路由器
自动选择可用的LLM提供商，支持故障转移
"""

import os
from typing import Dict, List, Any, Optional, Type
from .providers.base_provider import BaseLLMProvider, LLMMessage, LLMResponse
from .providers.ollama_provider import OllamaProvider
from .providers.openai_provider import OpenAIProvider
from .providers.dashscope_provider import DashScopeProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.claude_provider import ClaudeProvider
from .providers.gemini_provider import GeminiProvider
from .providers.siliconflow_provider import SiliconFlowProvider

class LLMRouter:
    """LLM路由器，管理多个LLM提供商"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config_from_env()
        self.providers: List[BaseLLMProvider] = []
        self.current_provider: Optional[BaseLLMProvider] = None
        
        # 初始化提供商
        self._initialize_providers()
        
        # 选择可用的提供商
        self._select_provider()
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            'providers': {
                'siliconflow': {
                    'enabled': bool(os.getenv('SILICONFLOW_API_KEY')),
                    'api_key': os.getenv('SILICONFLOW_API_KEY'),
                    'base_url': os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1'),
                    'model': os.getenv('SILICONFLOW_MODEL', 'Qwen/Qwen2.5-7B-Instruct'),
                    'temperature': float(os.getenv('SILICONFLOW_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('SILICONFLOW_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('SILICONFLOW_PRIORITY', '1'))  # 优先级最高
                },
                'deepseek': {
                    'enabled': bool(os.getenv('DEEPSEEK_API_KEY')),
                    'api_key': os.getenv('DEEPSEEK_API_KEY'),
                    'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
                    'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                    'temperature': float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('DEEPSEEK_PRIORITY', '2'))
                },
                'claude': {
                    'enabled': bool(os.getenv('CLAUDE_API_KEY')),
                    'api_key': os.getenv('CLAUDE_API_KEY'),
                    'base_url': os.getenv('CLAUDE_BASE_URL', 'https://api.anthropic.com'),
                    'model': os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307'),
                    'temperature': float(os.getenv('CLAUDE_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('CLAUDE_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('CLAUDE_PRIORITY', '3'))
                },
                'gemini': {
                    'enabled': bool(os.getenv('GEMINI_API_KEY')),
                    'api_key': os.getenv('GEMINI_API_KEY'),
                    'base_url': os.getenv('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com'),
                    'model': os.getenv('GEMINI_MODEL', 'gemini-pro'),
                    'temperature': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('GEMINI_PRIORITY', '4'))
                },
                'ollama': {
                    'enabled': os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true',
                    'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
                    'model': os.getenv('OLLAMA_MODEL', 'qwen2.5:8b'),
                    'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('OLLAMA_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('OLLAMA_PRIORITY', '5'))  # 降低优先级
                },
                'dashscope': {
                    'enabled': bool(os.getenv('LLM_API_KEY') or os.getenv('DASHSCOPE_API_KEY')),
                    'api_key': os.getenv('LLM_API_KEY') or os.getenv('DASHSCOPE_API_KEY'),
                    'base_url': os.getenv('LLM_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                    'model': os.getenv('DEFAULT_MODEL', 'qwen-plus'),
                    'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('DASHSCOPE_PRIORITY', '6'))
                },
                'openai': {
                    'enabled': bool(os.getenv('OPENAI_API_KEY')),
                    'api_key': os.getenv('OPENAI_API_KEY'),
                    'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
                    'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
                    'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '2000')),
                    'priority': int(os.getenv('OPENAI_PRIORITY', '7'))
                }
            }
        }
    
    def _initialize_providers(self):
        """初始化所有启用的提供商"""
        provider_classes = {
            'siliconflow': SiliconFlowProvider,
            'deepseek': DeepSeekProvider,
            'claude': ClaudeProvider,
            'gemini': GeminiProvider,
            'ollama': OllamaProvider,
            'dashscope': DashScopeProvider,
            'openai': OpenAIProvider
        }
        
        provider_configs = []
        
        for name, provider_class in provider_classes.items():
            config = self.config['providers'].get(name, {})
            if not config.get('enabled', False):
                print(f"[ROUTER] {name} 提供商未启用")
                continue
            
            try:
                provider = provider_class(config)
                provider_configs.append((config.get('priority', 999), provider))
                print(f"[ROUTER] {name} 提供商初始化成功")
            except Exception as e:
                print(f"[ROUTER] {name} 提供商初始化失败: {e}")
        
        # 按优先级排序
        provider_configs.sort(key=lambda x: x[0])
        self.providers = [provider for _, provider in provider_configs]
    
    def _select_provider(self):
        """选择可用的提供商"""
        for provider in self.providers:
            try:
                if provider.is_available():
                    self.current_provider = provider
                    print(f"[ROUTER] 选择提供商: {provider.get_provider_name()}")
                    return
                else:
                    print(f"[ROUTER] {provider.get_provider_name()} 不可用")
            except Exception as e:
                print(f"[ROUTER] 检查 {provider.get_provider_name()} 可用性失败: {e}")
        
        if not self.current_provider:
            print("[ROUTER] ⚠️  没有可用的LLM提供商，将使用fallback模式")
    
    def chat_completion(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        聊天完成（同步版本），支持故障转移
        """
        if not self.current_provider:
            raise Exception("没有可用的LLM提供商")
        
        # 尝试当前提供商
        try:
            # 检查提供商是否有同步方法
            if hasattr(self.current_provider, 'chat_completion_sync'):
                return self.current_provider.chat_completion_sync(messages, **kwargs)
            else:
                # 使用异步方法的同步包装
                import asyncio
                return asyncio.run(self.current_provider.chat_completion(messages, **kwargs))
        except Exception as e:
            print(f"[ROUTER] {self.current_provider.get_provider_name()} 调用失败: {e}")
            
            # 尝试故障转移
            for provider in self.providers:
                if provider == self.current_provider:
                    continue
                
                try:
                    if provider.is_available():
                        print(f"[ROUTER] 故障转移到: {provider.get_provider_name()}")
                        
                        if hasattr(provider, 'chat_completion_sync'):
                            result = provider.chat_completion_sync(messages, **kwargs)
                        else:
                            import asyncio
                            result = asyncio.run(provider.chat_completion(messages, **kwargs))
                        
                        self.current_provider = provider  # 更新当前提供商
                        return result
                except Exception as fallback_error:
                    print(f"[ROUTER] 故障转移失败 {provider.get_provider_name()}: {fallback_error}")
            
            # 所有提供商都失败
            raise Exception(f"所有LLM提供商都不可用，最后错误: {e}")
    
    async def chat_completion_async(
        self, 
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        聊天完成（异步版本），支持故障转移
        """
        if not self.current_provider:
            raise Exception("没有可用的LLM提供商")
        
        # 尝试当前提供商
        try:
            return await self.current_provider.chat_completion(messages, **kwargs)
        except Exception as e:
            print(f"[ROUTER] {self.current_provider.get_provider_name()} 调用失败: {e}")
            
            # 尝试故障转移
            for provider in self.providers:
                if provider == self.current_provider:
                    continue
                
                try:
                    if provider.is_available():
                        print(f"[ROUTER] 故障转移到: {provider.get_provider_name()}")
                        result = await provider.chat_completion(messages, **kwargs)
                        self.current_provider = provider  # 更新当前提供商
                        return result
                except Exception as fallback_error:
                    print(f"[ROUTER] 故障转移失败 {provider.get_provider_name()}: {fallback_error}")
            
            # 所有提供商都失败
            raise Exception(f"所有LLM提供商都不可用，最后错误: {e}")
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        if not self.current_provider:
            return {"name": "None", "available": False}
        
        return {
            "name": self.current_provider.get_provider_name(),
            "model": self.current_provider.model,
            "available": True
        }
    
    def list_available_providers(self) -> List[Dict[str, Any]]:
        """列出所有可用的提供商"""
        result = []
        for provider in self.providers:
            try:
                available = provider.is_available()
                result.append({
                    "name": provider.get_provider_name(),
                    "model": provider.model,
                    "available": available
                })
            except Exception as e:
                result.append({
                    "name": provider.get_provider_name(),
                    "model": provider.model,
                    "available": False,
                    "error": str(e)
                })
        return result
    
    def switch_provider(self, provider_name: str) -> bool:
        """手动切换提供商"""
        for provider in self.providers:
            if provider.get_provider_name().lower() == provider_name.lower():
                try:
                    if provider.is_available():
                        self.current_provider = provider
                        print(f"[ROUTER] 手动切换到: {provider.get_provider_name()}")
                        return True
                    else:
                        print(f"[ROUTER] {provider_name} 不可用")
                        return False
                except Exception as e:
                    print(f"[ROUTER] 切换到 {provider_name} 失败: {e}")
                    return False
        
        print(f"[ROUTER] 未找到提供商: {provider_name}")
        return False