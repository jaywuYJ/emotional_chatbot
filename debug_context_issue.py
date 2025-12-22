#!/usr/bin/env python3
"""
调试AI回复重复问题 - 检查数据库和上下文状态
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database import DatabaseManager
from backend.services.chat_service import ChatService
from backend.services.context_service import ContextService
from backend.services.memory_service import MemoryService

def check_database_messages(session_id: str):
    """检查数据库中的消息存储情况"""
    print("=" * 60)
    print("检查数据库消息存储")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            messages = db.get_session_messages(session_id, limit=50)
            
            print(f"会话 {session_id} 中共有 {len(messages)} 条消息:")
            print()
            
            for i, msg in enumerate(messages, 1):
                print(f"{i}. ID: {msg.id}")
                print(f"   角色: {msg.role}")
                print(f"   内容: {msg.content[:100]}...")
                print(f"   情感: {msg.emotion}")
                print(f"   时间: {msg.created_at}")
                print(f"   用户ID: {msg.user_id}")
                print()
            
            if len(messages) == 0:
                print("⚠️  数据库中没有找到消息，可能存在保存问题")
            else:
                print(f"✅ 数据库中有 {len(messages)} 条消息")
                
                # 检查消息顺序
                user_messages = [msg for msg in messages if msg.role == 'user']
                ai_messages = [msg for msg in messages if msg.role == 'assistant']
                
                print(f"用户消息: {len(user_messages)} 条")
                print(f"AI消息: {len(ai_messages)} 条")
                
                if len(user_messages) != len(ai_messages):
                    print("⚠️  用户消息和AI消息数量不匹配，可能存在保存问题")
                
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        import traceback
        traceback.print_exc()

async def check_context_service(user_id: str, session_id: str, message: str):
    """检查上下文服务是否正常工作"""
    print("=" * 60)
    print("检查上下文服务")
    print("=" * 60)
    
    try:
        memory_service = MemoryService()
        context_service = ContextService(memory_service=memory_service)
        
        context = await context_service.build_context(
            user_id=user_id,
            session_id=session_id,
            current_message=message,
            emotion="neutral",
            emotion_intensity=5.0
        )
        
        print("上下文构建结果:")
        print(f"- 记忆数量: {len(context.get('memories', {}).get('all', []))}")
        print(f"- 用户画像: {'有' if context.get('user_profile', {}).get('summary') else '无'}")
        print(f"- 情感趋势: {context.get('emotion_context', {}).get('trend', {}).get('trend', '无')}")
        
        # 显示记忆内容
        memories = context.get('memories', {})
        if memories:
            print("\n记忆详情:")
            for memory_type, memory_list in memories.items():
                if memory_list and memory_type != 'all':
                    print(f"  {memory_type}: {len(memory_list)} 条")
                    for mem in memory_list[:2]:  # 只显示前2条
                        print(f"    - {mem.get('content', '')[:50]}...")
        
        print("✅ 上下文服务工作正常")
        return context
        
    except Exception as e:
        print(f"❌ 上下文服务检查失败: {e}")
        import traceback
        traceback.print_exc()
        return {}

def check_llm_config():
    """检查LLM配置"""
    print("=" * 60)
    print("检查LLM配置")
    print("=" * 60)
    
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base_url = os.getenv("LLM_BASE_URL") or os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("DEFAULT_MODEL", "qwen-plus")
    
    print(f"API Key: {'已配置' if api_key else '❌ 未配置'}")
    print(f"API Base URL: {api_base_url}")
    print(f"默认模型: {model}")
    
    if not api_key:
        print("⚠️  API Key未配置，AI将使用fallback模式，可能导致回复重复")
    else:
        print("✅ LLM配置正常")

async def debug_specific_session(session_id: str):
    """调试特定会话的问题"""
    print("=" * 60)
    print(f"调试会话: {session_id}")
    print("=" * 60)
    
    # 1. 检查数据库消息
    check_database_messages(session_id)
    
    # 2. 检查LLM配置
    check_llm_config()
    
    # 3. 检查上下文服务
    user_id = "debug_user"
    test_message = "这是一条测试消息"
    context = await check_context_service(user_id, session_id, test_message)
    
    # 4. 检查聊天服务初始化
    print("=" * 60)
    print("检查聊天服务初始化")
    print("=" * 60)
    
    try:
        chat_service = ChatService()
        
        print(f"RAG服务: {'已启用' if chat_service.rag_enabled else '未启用'}")
        print(f"意图识别: {'已启用' if chat_service.intent_enabled else '未启用'}")
        print(f"增强处理器: {'已启用' if chat_service.enhanced_processor_enabled else '未启用'}")
        print(f"向量数据库: {'已连接' if chat_service.vector_store else '未连接'}")
        
        # 检查LLM引擎类型
        engine_type = type(chat_service.chat_engine).__name__
        print(f"LLM引擎类型: {engine_type}")
        
        if hasattr(chat_service.chat_engine, 'api_key'):
            print(f"引擎API Key: {'已配置' if chat_service.chat_engine.api_key else '❌ 未配置'}")
        
        print("✅ 聊天服务初始化正常")
        
    except Exception as e:
        print(f"❌ 聊天服务检查失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主调试函数"""
    print("AI回复重复问题调试工具")
    print("=" * 60)
    
    # 可以指定要调试的会话ID，或者使用默认的测试会话
    session_id = input("请输入要调试的会话ID（直接回车使用默认测试会话）: ").strip()
    if not session_id:
        session_id = "test_session_001"
    
    await debug_specific_session(session_id)
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)
    print("\n常见问题和解决方案:")
    print("1. 如果API Key未配置 → 检查config.env文件")
    print("2. 如果数据库无消息 → 检查数据库连接和消息保存逻辑")
    print("3. 如果上下文服务异常 → 检查记忆服务和向量数据库")
    print("4. 如果LLM引擎异常 → 检查API配置和网络连接")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())