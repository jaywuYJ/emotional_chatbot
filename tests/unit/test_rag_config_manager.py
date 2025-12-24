#!/usr/bin/env python3
"""
测试 RAG 配置管理器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.rag.core.rag_config_manager import RAGConfigManager

def test_rag_config_manager():
    """测试 RAG 配置管理器"""
    print("=== RAG 配置管理器测试 ===\n")
    
    manager = RAGConfigManager("./test_rag_config.json")
    
    print("1. 当前配置:")
    config = manager.get_config()
    print(f"   Provider: {config.embedding_provider}")
    print(f"   Model: {config.embedding_model}")
    print(f"   Enabled: {config.enabled}")
    print(f"   Knowledge Base Path: {config.knowledge_base_path}")
    print(f"   Chunk Size: {config.chunk_size}")
    print()
    
    print("2. 可用提供商:")
    providers = manager.get_available_providers()
    for provider in providers:
        status = "✓" if provider["available"] else "✗"
        current = " (当前)" if provider["current"] else ""
        print(f"   {status} {provider['name']}{current}")
        print(f"      描述: {provider['description']}")
        print(f"      模型: {', '.join(provider['models'][:2])}...")
        print(f"      需要API密钥: {'是' if provider['requires_api_key'] else '否'}")
    print()
    
    print("3. 当前提供商信息:")
    current_info = manager.get_current_provider_info()
    for key, value in current_info.items():
        print(f"   {key}: {value}")
    print()
    
    print("4. 测试当前配置:")
    test_result = manager.test_current_config()
    for key, value in test_result.items():
        print(f"   {key}: {value}")
    print()
    
    print("5. 尝试更新配置:")
    try:
        manager.update_config(
            chunk_size=600,
            search_k=5,
            similarity_threshold=0.8
        )
        print("   ✓ 配置更新成功")
        
        # 验证更新
        updated_config = manager.get_config()
        print(f"   新的 chunk_size: {updated_config.chunk_size}")
        print(f"   新的 search_k: {updated_config.search_k}")
        print(f"   新的 similarity_threshold: {updated_config.similarity_threshold}")
        
    except Exception as e:
        print(f"   ❌ 配置更新失败: {e}")
    print()
    
    print("6. 尝试设置不同的提供商:")
    try:
        success = manager.set_embedding_provider("siliconflow", "BAAI/bge-m3")
        print(f"   设置结果: {'成功' if success else '失败'}")
        
        if success:
            new_info = manager.get_current_provider_info()
            print(f"   新的提供商: {new_info['provider']}")
            print(f"   新的模型: {new_info['model']}")
            
    except Exception as e:
        print(f"   ❌ 设置提供商失败: {e}")
    print()
    
    print("7. 测试知识库管理器创建:")
    try:
        kb_manager = manager.create_knowledge_base_manager()
        print("   ✓ 知识库管理器创建成功")
        
        # 获取统计信息
        stats = kb_manager.get_stats()
        print("   知识库统计:")
        for key, value in stats.items():
            print(f"     {key}: {value}")
            
    except Exception as e:
        print(f"   ❌ 知识库管理器创建失败: {e}")
    print()
    
    print("8. 测试配置导出:")
    try:
        export_success = manager.export_config("./exported_rag_config.json")
        print(f"   导出结果: {'成功' if export_success else '失败'}")
        
        if export_success and os.path.exists("./exported_rag_config.json"):
            print("   ✓ 导出文件已创建")
            
    except Exception as e:
        print(f"   ❌ 配置导出失败: {e}")
    
    print("\n✅ RAG 配置管理器测试完成！")


if __name__ == "__main__":
    test_rag_config_manager()