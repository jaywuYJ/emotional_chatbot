#!/usr/bin/env python3
"""
测试上下文传递修复效果
专门测试你遇到的RAG技术讨论场景
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.models import ChatRequest
from backend.services.chat_service import ChatService

async def test_rag_discussion_context():
    """测试RAG技术讨论的上下文传递"""
    print("=" * 80)
    print("测试RAG技术讨论的上下文传递修复效果")
    print("=" * 80)
    
    # 初始化聊天服务
    chat_service = ChatService()
    
    # 模拟你的实际对话场景
    user_id = "rag_test_user"
    session_id = "rag_discussion_session"
    
    # 第一轮：表达复杂情绪
    print("\n1️⃣ 第一轮对话：用户表达复杂情绪")
    print("-" * 50)
    request1 = ChatRequest(
        message="有点开心又有点焦虑",
        user_id=user_id,
        session_id=session_id
    )
    
    response1 = await chat_service.chat(request1, use_memory_system=True)
    print(f"👤 用户: {request1.message}")
    print(f"🤖 AI: {response1.response}")
    print(f"😊 情感: {response1.emotion}")
    
    # 第二轮：AI询问详情
    print("\n2️⃣ 第二轮对话：AI询问详情")
    print("-" * 50)
    request2 = ChatRequest(
        message="你好呀，能感觉到你心里有些说不清的情绪。愿意和我聊聊是什么让你觉得复杂吗？我在认真听。",
        user_id="assistant",  # 模拟AI回复
        session_id=session_id
    )
    # 这里我们直接跳过，因为这是AI的回复
    
    # 第三轮：用户提供具体信息
    print("\n3️⃣ 第三轮对话：用户提供具体信息")
    print("-" * 50)
    request3 = ChatRequest(
        message="开心的是，找到了学习大模型应用开发包括RAG的一套很好的资料，焦虑的是，要掌握课程可能比我想象的要花上更多的精力和时间。",
        user_id=user_id,
        session_id=session_id
    )
    
    response3 = await chat_service.chat(request3, use_memory_system=True)
    print(f"👤 用户: {request3.message}")
    print(f"🤖 AI: {response3.response}")
    print(f"😊 情感: {response3.emotion}")
    
    # 第四轮：用户提供更详细的技术信息
    print("\n4️⃣ 第四轮对话：用户提供详细技术信息")
    print("-" * 50)
    request4 = ChatRequest(
        message="我2年前就做过RAG的尝试，当时用向量数据库把自己的小说向量化了之后，用chunk",
        user_id=user_id,
        session_id=session_id
    )
    
    response4 = await chat_service.chat(request4, use_memory_system=True)
    print(f"👤 用户: {request4.message}")
    print(f"🤖 AI: {response4.response}")
    print(f"😊 情感: {response4.emotion}")
    
    # 第五轮：用户提供更多技术细节
    print("\n5️⃣ 第五轮对话：用户提供更多技术细节")
    print("-" * 50)
    request5 = ChatRequest(
        message="当时用RAG做的目的是让他能提取出我写的小说中的故事情节，并且希望他能够按照我的风格来续写小说。但是我发现搜索虽然大差不差，但是限于上下文长度等问题，还是会有很多不能精准命中的情况。当时并不知道为什么检索出来的chunk有时候会不那么相关。我想知道到底是embedding 模型的问题还是其它什么原因。其次就是各种细节问题，比如如何处理原始文档，如何调试RAG项目并发现问题的根源出在哪个环节，如何评估RAG的准确率，如何打造生产级别的RAG产品等等",
        user_id=user_id,
        session_id=session_id
    )
    
    response5 = await chat_service.chat(request5, use_memory_system=True)
    print(f"👤 用户: {request5.message}")
    print(f"🤖 AI: {response5.response}")
    print(f"😊 情感: {response5.emotion}")
    
    # 分析结果
    print("\n" + "=" * 80)
    print("📊 分析结果")
    print("=" * 80)
    
    # 检查AI是否能够引用之前的技术讨论
    rag_keywords = ["RAG", "向量数据库", "chunk", "embedding", "小说", "续写", "检索", "上下文长度"]
    technical_keywords = ["调试", "评估", "准确率", "生产级别", "原始文档"]
    
    mentioned_rag = [kw for kw in rag_keywords if kw in response5.response]
    mentioned_tech = [kw for kw in technical_keywords if kw in response5.response]
    
    print(f"🔍 RAG相关关键词检查:")
    print(f"   期望关键词: {rag_keywords}")
    print(f"   AI提及的: {mentioned_rag}")
    print(f"   覆盖率: {len(mentioned_rag)}/{len(rag_keywords)} = {len(mentioned_rag)/len(rag_keywords):.1%}")
    
    print(f"\n🔧 技术细节关键词检查:")
    print(f"   期望关键词: {technical_keywords}")
    print(f"   AI提及的: {mentioned_tech}")
    print(f"   覆盖率: {len(mentioned_tech)}/{len(technical_keywords)} = {len(mentioned_tech)/len(technical_keywords):.1%}")
    
    # 检查是否出现"今天感觉怎么样"这种脱离上下文的回复
    generic_phrases = ["今天感觉怎么样", "今天过得如何", "心情如何", "有什么想聊的吗"]
    found_generic = [phrase for phrase in generic_phrases if phrase in response5.response]
    
    if found_generic:
        print(f"\n❌ 发现脱离上下文的通用回复: {found_generic}")
        print("   这表明上下文传递仍有问题")
    else:
        print(f"\n✅ 没有发现脱离上下文的通用回复")
    
    # 检查回复是否与技术讨论相关
    if len(mentioned_rag) >= 2 or len(mentioned_tech) >= 1:
        print(f"\n✅ AI能够很好地跟进技术讨论")
        print(f"   回复与RAG技术话题高度相关")
    elif len(mentioned_rag) >= 1:
        print(f"\n⚠️  AI部分跟进了技术讨论，但可能需要改进")
    else:
        print(f"\n❌ AI没有有效跟进技术讨论")
        print(f"   可能存在上下文传递问题")
    
    # 检查回复长度和质量
    response_length = len(response5.response)
    print(f"\n📏 回复质量分析:")
    print(f"   回复长度: {response_length} 字符")
    
    if response_length < 50:
        print(f"   ⚠️  回复过短，可能是fallback回复")
    elif response_length > 200:
        print(f"   ✅ 回复长度适中，内容较为丰富")
    else:
        print(f"   ✅ 回复长度正常")

async def test_context_memory():
    """测试上下文记忆功能"""
    print("\n" + "=" * 80)
    print("测试上下文记忆功能")
    print("=" * 80)
    
    chat_service = ChatService()
    user_id = "memory_test_user"
    session_id = "memory_test_session"
    
    # 建立一些背景信息
    background_messages = [
        "我是一个程序员，专门做AI相关的工作",
        "我最近在研究RAG技术",
        "我有2年的向量数据库使用经验",
        "我之前用RAG处理过小说文本",
        "我现在想学习更高级的RAG技术"
    ]
    
    print("🏗️ 建立背景上下文...")
    for i, msg in enumerate(background_messages, 1):
        request = ChatRequest(
            message=msg,
            user_id=user_id,
            session_id=session_id
        )
        response = await chat_service.chat(request, use_memory_system=True)
        print(f"   {i}. 用户: {msg}")
        print(f"      AI: {response.response[:50]}...")
    
    # 测试AI是否能记住这些信息
    print(f"\n🧠 测试记忆效果...")
    test_request = ChatRequest(
        message="根据我们之前的对话，你觉得我应该重点关注RAG的哪些方面？",
        user_id=user_id,
        session_id=session_id
    )
    
    test_response = await chat_service.chat(test_request, use_memory_system=True)
    print(f"👤 用户: {test_request.message}")
    print(f"🤖 AI: {test_response.response}")
    
    # 检查AI是否引用了之前的信息
    background_keywords = ["程序员", "AI", "RAG", "向量数据库", "2年", "小说", "经验"]
    mentioned_bg = [kw for kw in background_keywords if kw in test_response.response]
    
    print(f"\n📋 记忆效果分析:")
    print(f"   背景关键词: {background_keywords}")
    print(f"   AI提及的: {mentioned_bg}")
    print(f"   记忆覆盖率: {len(mentioned_bg)}/{len(background_keywords)} = {len(mentioned_bg)/len(background_keywords):.1%}")
    
    if len(mentioned_bg) >= 3:
        print(f"   ✅ 记忆功能工作良好")
    elif len(mentioned_bg) >= 1:
        print(f"   ⚠️  记忆功能部分工作")
    else:
        print(f"   ❌ 记忆功能可能存在问题")

async def main():
    """主测试函数"""
    try:
        await test_rag_discussion_context()
        await test_context_memory()
        
        print("\n" + "=" * 80)
        print("🎯 测试总结")
        print("=" * 80)
        print("\n如果测试显示问题仍然存在，可能的原因：")
        print("1. 🔧 LLM API配置问题 - 检查config.env中的API设置")
        print("2. 💾 数据库连接问题 - 检查MySQL连接和消息保存")
        print("3. 🧠 记忆服务问题 - 检查向量数据库和记忆处理")
        print("4. 📡 上下文传递问题 - 检查ChatService到LLM引擎的数据传递")
        print("5. 🎛️  模型参数问题 - 可能需要调整temperature或max_tokens")
        
        print("\n💡 建议的调试步骤：")
        print("1. 运行 python debug_context_issue.py 检查系统状态")
        print("2. 检查日志输出中的上下文信息传递")
        print("3. 验证数据库中的消息保存是否正确")
        print("4. 测试不同的对话场景")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())