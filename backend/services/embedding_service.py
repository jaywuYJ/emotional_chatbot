#!/usr/bin/env python3
"""
Embedding服务
支持多种embedding提供商
"""

import os
from typing import List, Dict, Any, Optional
from backend.modules.llm.providers.siliconflow_provider import SiliconFlowProvider

class EmbeddingService:
    """Embedding服务"""
    
    def __init__(self):
        self.provider = os.getenv('EMBEDDING_PROVIDER', 'siliconflow')
        self.model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
        self.api_key = os.getenv('EMBEDDING_API_KEY') or os.getenv('SILICONFLOW_API_KEY')
        self.base_url = os.getenv('EMBEDDING_BASE_URL', 'https://api.siliconflow.cn/v1')
        
        # 初始化提供商
        self._init_provider()
    
    def _init_provider(self):
        """初始化embedding提供商"""
        if self.provider == 'siliconflow':
            if not self.api_key:
                print("警告: SiliconFlow API key未设置，embedding功能不可用")
                self.embedding_provider = None
                return
            
            config = {
                'api_key': self.api_key,
                'base_url': self.base_url,
                'model': self.model
            }
            
            try:
                self.embedding_provider = SiliconFlowProvider(config)
                print(f"✓ Embedding服务初始化成功: {self.provider} - {self.model}")
            except Exception as e:
                print(f"⚠ Embedding服务初始化失败: {e}")
                self.embedding_provider = None
        else:
            print(f"不支持的embedding提供商: {self.provider}")
            self.embedding_provider = None
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        获取文本的embedding向量
        
        Args:
            texts: 要获取embedding的文本列表
            
        Returns:
            embedding向量列表
        """
        if not self.embedding_provider:
            raise Exception("Embedding服务不可用")
        
        if not texts:
            return []
        
        try:
            if hasattr(self.embedding_provider, 'get_embedding'):
                return self.embedding_provider.get_embedding(texts, self.model)
            else:
                raise Exception(f"提供商 {self.provider} 不支持embedding功能")
        except Exception as e:
            print(f"获取embedding失败: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的embedding向量
        
        Args:
            text: 要获取embedding的文本
            
        Returns:
            embedding向量
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def is_available(self) -> bool:
        """检查embedding服务是否可用"""
        return self.embedding_provider is not None
    
    def get_info(self) -> Dict[str, Any]:
        """获取embedding服务信息"""
        return {
            "provider": self.provider,
            "model": self.model,
            "available": self.is_available(),
            "base_url": self.base_url
        }

# 全局embedding服务实例
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """获取全局embedding服务实例"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service