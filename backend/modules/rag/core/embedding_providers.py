#!/usr/bin/env python3
"""
Embedding 提供商管理器
支持多种 embedding 模型提供商
"""

import os
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

from backend.logging_config import get_logger
from config import Config

logger = get_logger(__name__)

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain.embeddings.base import Embeddings
except ImportError as e:
    logger.warning(f"部分 embedding 依赖未安装: {e}")
    # 创建基础类以避免导入错误
    class Embeddings:
        pass
    
    class OpenAIEmbeddings:
        pass
    
    class OllamaEmbeddings:
        pass


class BaseEmbeddingProvider(ABC):
    """Embedding 提供商基类"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """获取 embedding 实例"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding 提供商"""
    
    def get_embeddings(self) -> Embeddings:
        """获取 OpenAI embedding 实例"""
        try:
            return OpenAIEmbeddings(
                model=self.model,
                openai_api_key=self.api_key,
                openai_api_base=self.base_url
            )
        except Exception as e:
            logger.error(f"创建 OpenAI embedding 失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查 OpenAI 提供商是否可用"""
        return bool(self.api_key)


class SiliconFlowEmbeddingProvider(BaseEmbeddingProvider):
    """SiliconFlow Embedding 提供商（使用 OpenAI 兼容接口）"""
    
    def get_embeddings(self) -> Embeddings:
        """获取 SiliconFlow embedding 实例"""
        try:
            return OpenAIEmbeddings(
                model=self.model,
                openai_api_key=self.api_key,
                openai_api_base=self.base_url
            )
        except Exception as e:
            logger.error(f"创建 SiliconFlow embedding 失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查 SiliconFlow 提供商是否可用"""
        return bool(self.api_key and self.base_url)


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama 本地 Embedding 提供商"""
    
    def get_embeddings(self) -> Embeddings:
        """获取 Ollama embedding 实例"""
        try:
            return OllamaEmbeddings(
                model=self.model,
                base_url=self.base_url or "http://localhost:11434"
            )
        except Exception as e:
            logger.error(f"创建 Ollama embedding 失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查 Ollama 提供商是否可用"""
        # 简单检查，实际使用时可以添加连接测试
        return True


class DeepSeekEmbeddingProvider(BaseEmbeddingProvider):
    """DeepSeek Embedding 提供商（使用 OpenAI 兼容接口）"""
    
    def get_embeddings(self) -> Embeddings:
        """获取 DeepSeek embedding 实例"""
        try:
            return OpenAIEmbeddings(
                model=self.model,
                openai_api_key=self.api_key,
                openai_api_base=self.base_url
            )
        except Exception as e:
            logger.error(f"创建 DeepSeek embedding 失败: {e}")
            raise
    
    def is_available(self) -> bool:
        """检查 DeepSeek 提供商是否可用"""
        return bool(self.api_key and self.base_url)


class EmbeddingProviderManager:
    """Embedding 提供商管理器"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIEmbeddingProvider,
            "siliconflow": SiliconFlowEmbeddingProvider,
            "ollama": OllamaEmbeddingProvider,
            "deepseek": DeepSeekEmbeddingProvider,
        }
        logger.info("Embedding 提供商管理器初始化完成")
    
    def get_embedding_instance(
        self,
        provider: str = None,
        model: str = None,
        api_key: str = None,
        base_url: str = None
    ) -> Optional[Embeddings]:
        """
        获取 embedding 实例
        
        Args:
            provider: 提供商名称
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
            
        Returns:
            Embedding 实例或 None
        """
        try:
            # 使用配置文件中的默认值
            provider = provider or Config.EMBEDDING_PROVIDER
            model = model or Config.EMBEDDING_MODEL
            api_key = api_key or Config.EMBEDDING_API_KEY
            base_url = base_url or Config.EMBEDDING_BASE_URL
            
            logger.info(f"尝试创建 embedding 实例: provider={provider}, model={model}")
            
            if provider not in self.providers:
                logger.error(f"不支持的 embedding 提供商: {provider}")
                return None
            
            provider_class = self.providers[provider]
            provider_instance = provider_class(model, api_key, base_url)
            
            if not provider_instance.is_available():
                logger.warning(f"Embedding 提供商 {provider} 不可用，缺少必要配置")
                return None
            
            embeddings = provider_instance.get_embeddings()
            logger.info(f"成功创建 {provider} embedding 实例")
            return embeddings
            
        except Exception as e:
            logger.error(f"创建 embedding 实例失败: {e}")
            return None
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        available = []
        for name, provider_class in self.providers.items():
            try:
                # 尝试创建实例来检查可用性
                if name == "openai":
                    provider = provider_class("text-embedding-ada-002", Config.EMBEDDING_API_KEY, Config.EMBEDDING_BASE_URL)
                elif name == "siliconflow":
                    provider = provider_class("BAAI/bge-m3", Config.EMBEDDING_API_KEY, Config.EMBEDDING_BASE_URL)
                elif name == "ollama":
                    provider = provider_class("nomic-embed-text", None, "http://localhost:11434")
                elif name == "deepseek":
                    provider = provider_class("text-embedding-v1", Config.EMBEDDING_API_KEY, Config.EMBEDDING_BASE_URL)
                else:
                    continue
                
                if provider.is_available():
                    available.append(name)
            except Exception as e:
                logger.debug(f"提供商 {name} 不可用: {e}")
                continue
        
        return available
    
    def test_embedding(self, provider: str = None, model: str = None) -> bool:
        """
        测试 embedding 功能
        
        Args:
            provider: 提供商名称
            model: 模型名称
            
        Returns:
            是否测试成功
        """
        try:
            embeddings = self.get_embedding_instance(provider, model)
            if embeddings is None:
                return False
            
            # 测试嵌入一个简单文本
            test_text = "这是一个测试文本"
            result = embeddings.embed_query(test_text)
            
            if result and len(result) > 0:
                logger.info(f"Embedding 测试成功，向量维度: {len(result)}")
                return True
            else:
                logger.error("Embedding 测试失败，返回空向量")
                return False
                
        except Exception as e:
            logger.error(f"Embedding 测试失败: {e}")
            return False


# 全局实例
embedding_manager = EmbeddingProviderManager()


def get_embedding_instance(
    provider: str = None,
    model: str = None,
    api_key: str = None,
    base_url: str = None
) -> Optional[Embeddings]:
    """
    便捷函数：获取 embedding 实例
    
    Args:
        provider: 提供商名称
        model: 模型名称
        api_key: API 密钥
        base_url: API 基础 URL
        
    Returns:
        Embedding 实例或 None
    """
    return embedding_manager.get_embedding_instance(provider, model, api_key, base_url)


if __name__ == "__main__":
    # 测试代码
    print("测试 Embedding 提供商管理器...")
    
    manager = EmbeddingProviderManager()
    
    print("\n可用的提供商:")
    available = manager.get_available_providers()
    for provider in available:
        print(f"  - {provider}")
    
    if available:
        print(f"\n测试第一个可用提供商: {available[0]}")
        success = manager.test_embedding(available[0])
        print(f"测试结果: {'成功' if success else '失败'}")
    else:
        print("\n没有可用的 embedding 提供商")