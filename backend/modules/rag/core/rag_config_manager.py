#!/usr/bin/env python3
"""
RAG 配置管理器
提供灵活的 embedding 提供商配置和管理功能
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from backend.logging_config import get_logger
from backend.modules.rag.models.rag_models import RAGConfig
from backend.modules.rag.core.embedding_providers import EmbeddingProviderManager
from config import Config

logger = get_logger(__name__)


class RAGConfigManager:
    """RAG 配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为 None 则只使用环境变量配置
        """
        self.config_file = config_file
        self.embedding_manager = EmbeddingProviderManager()
        self._load_config()
        logger.info("RAG 配置管理器初始化完成")
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            # 如果指定了配置文件且文件存在，则从文件加载
            if self.config_file and os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.config = RAGConfig(**config_data)
                logger.info(f"从文件加载 RAG 配置: {self.config_file}")
            else:
                # 使用环境变量配置（优先）
                self.config = self._create_default_config()
                # 如果指定了配置文件，保存默认配置到文件
                if self.config_file:
                    self._save_config()
                    logger.info("创建默认 RAG 配置并保存到文件")
                else:
                    logger.info("使用环境变量 RAG 配置")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self.config = self._create_default_config()
    
    def _create_default_config(self) -> RAGConfig:
        """创建默认配置"""
        return RAGConfig(
            enabled=True,
            knowledge_base_path="./chroma_db/psychology_kb",
            search_k=3,
            similarity_threshold=0.7,
            max_context_length=4000,
            chunk_size=500,
            chunk_overlap=50,
            chunking_strategy="auto",
            embedding_provider=Config.EMBEDDING_PROVIDER,
            embedding_model=Config.EMBEDDING_MODEL,
            embedding_api_key=Config.EMBEDDING_API_KEY,
            embedding_base_url=Config.EMBEDDING_BASE_URL
        )
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        if not self.config_file:
            logger.warning("未指定配置文件，跳过保存")
            return
            
        try:
            config_dict = self.config.dict()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get_config(self) -> RAGConfig:
        """获取当前配置"""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        try:
            # 更新配置对象
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    logger.info(f"更新配置项: {key} = {value}")
            
            # 保存到文件
            self._save_config()
            
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            raise
    
    def set_embedding_provider(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> bool:
        """
        设置 embedding 提供商
        
        Args:
            provider: 提供商名称
            model: 模型名称
            api_key: API 密钥
            base_url: API 基础 URL
            
        Returns:
            是否设置成功
        """
        try:
            # 测试提供商是否可用
            test_success = self.embedding_manager.test_embedding(provider, model)
            if not test_success:
                logger.warning(f"Embedding 提供商 {provider} 测试失败，但仍会保存配置")
            
            # 更新配置
            self.update_config(
                embedding_provider=provider,
                embedding_model=model,
                embedding_api_key=api_key or self.config.embedding_api_key,
                embedding_base_url=base_url or self.config.embedding_base_url
            )
            
            logger.info(f"成功设置 embedding 提供商: {provider}/{model}")
            return True
            
        except Exception as e:
            logger.error(f"设置 embedding 提供商失败: {e}")
            return False
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取可用的 embedding 提供商列表"""
        providers = []
        
        # 预定义的提供商配置
        provider_configs = {
            "siliconflow": {
                "name": "SiliconFlow",
                "description": "API 聚合平台，支持多种模型",
                "models": [
                    "BAAI/bge-m3",
                    "BAAI/bge-large-zh-v1.5",
                    "sentence-transformers/all-MiniLM-L6-v2"
                ],
                "requires_api_key": True,
                "default_base_url": "https://api.siliconflow.cn/v1"
            },
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI 官方 embedding 服务",
                "models": [
                    "text-embedding-ada-002",
                    "text-embedding-3-small",
                    "text-embedding-3-large"
                ],
                "requires_api_key": True,
                "default_base_url": "https://api.openai.com/v1"
            },
            "ollama": {
                "name": "Ollama",
                "description": "本地部署的 embedding 服务",
                "models": [
                    "nomic-embed-text",
                    "mxbai-embed-large",
                    "all-minilm"
                ],
                "requires_api_key": False,
                "default_base_url": "http://localhost:11434"
            },
            "deepseek": {
                "name": "DeepSeek",
                "description": "DeepSeek 的 embedding 服务",
                "models": [
                    "text-embedding-v1"
                ],
                "requires_api_key": True,
                "default_base_url": "https://api.deepseek.com/v1"
            }
        }
        
        # 检查每个提供商的可用性
        available_provider_names = self.embedding_manager.get_available_providers()
        
        for provider_id, config in provider_configs.items():
            provider_info = {
                "id": provider_id,
                "name": config["name"],
                "description": config["description"],
                "models": config["models"],
                "requires_api_key": config["requires_api_key"],
                "default_base_url": config["default_base_url"],
                "available": provider_id in available_provider_names,
                "current": provider_id == self.config.embedding_provider
            }
            providers.append(provider_info)
        
        return providers
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        return {
            "provider": self.config.embedding_provider,
            "model": self.config.embedding_model,
            "api_key_set": bool(self.config.embedding_api_key),
            "base_url": self.config.embedding_base_url,
            "enabled": self.config.enabled
        }
    
    def test_current_config(self) -> Dict[str, Any]:
        """测试当前配置"""
        try:
            # 测试 embedding
            embedding_success = self.embedding_manager.test_embedding(
                self.config.embedding_provider,
                self.config.embedding_model
            )
            
            # 测试知识库路径
            kb_path_exists = os.path.exists(self.config.knowledge_base_path)
            
            return {
                "embedding_test": embedding_success,
                "knowledge_base_path_exists": kb_path_exists,
                "config_valid": True,
                "message": "配置测试完成"
            }
            
        except Exception as e:
            return {
                "embedding_test": False,
                "knowledge_base_path_exists": False,
                "config_valid": False,
                "message": f"配置测试失败: {e}"
            }
    
    def create_knowledge_base_manager(self):
        """根据当前配置创建知识库管理器"""
        from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager
        
        return KnowledgeBaseManager(
            persist_directory=self.config.knowledge_base_path,
            chunking_strategy=self.config.chunking_strategy,
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            embedding_provider=self.config.embedding_provider,
            embedding_model=self.config.embedding_model,
            embedding_api_key=self.config.embedding_api_key,
            embedding_base_url=self.config.embedding_base_url
        )
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定路径"""
        try:
            config_dict = self.config.dict()
            # 不导出敏感信息
            if 'embedding_api_key' in config_dict:
                config_dict['embedding_api_key'] = "***HIDDEN***"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已导出到: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定路径导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证配置
            new_config = RAGConfig(**config_data)
            self.config = new_config
            self._save_config()
            
            logger.info(f"配置已从 {import_path} 导入")
            return True
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False


# 全局配置管理器实例（使用环境变量配置，不创建文件）
rag_config_manager = RAGConfigManager(config_file=None)


def get_rag_config() -> RAGConfig:
    """获取 RAG 配置"""
    return rag_config_manager.get_config()


def update_rag_config(**kwargs) -> None:
    """更新 RAG 配置"""
    rag_config_manager.update_config(**kwargs)


if __name__ == "__main__":
    # 测试代码
    print("=== RAG 配置管理器测试 ===\n")
    
    manager = RAGConfigManager("./test_rag_config.json")
    
    print("1. 当前配置:")
    config = manager.get_config()
    print(f"   Provider: {config.embedding_provider}")
    print(f"   Model: {config.embedding_model}")
    print(f"   Enabled: {config.enabled}")
    print()
    
    print("2. 可用提供商:")
    providers = manager.get_available_providers()
    for provider in providers:
        status = "✓" if provider["available"] else "✗"
        current = " (当前)" if provider["current"] else ""
        print(f"   {status} {provider['name']}{current}")
        print(f"      模型: {', '.join(provider['models'][:2])}...")
    print()
    
    print("3. 测试当前配置:")
    test_result = manager.test_current_config()
    for key, value in test_result.items():
        print(f"   {key}: {value}")
    print()
    
    print("4. 尝试设置不同的提供商:")
    success = manager.set_embedding_provider("siliconflow", "BAAI/bge-m3")
    print(f"   设置结果: {'成功' if success else '失败'}")
    
    print("\n✅ RAG 配置管理器测试完成！")