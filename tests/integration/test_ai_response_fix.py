#!/usr/bin/env python3
"""
测试AI回复重复问题的修复效果
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.models import ChatRequest
from backend.services.chat_service import ChatService

async def test_conversation_context():
    """测试对话上下文是否正确传递"""
    print("=" * 60)
    print("测试AI回复重复问题修复效果")
    print("=" * 60)
    
    # 初始化聊天服务
    chat_service = ChatService()
    
    # 模拟你的对话场景
    user_id = "test_user_001"
    session_id = "test_session_001"
    
    print("\n1. 第一轮对话：用户表达复杂情绪")
    request1 = ChatRequest(
        message="有点开心又有点焦虑",
        user_id=user_id,
        session_id=session_id
    )
    
    response1 = await chat_service.chat(request1, use_memory_system=True)
    print(f"用户: {request1.message}")
    print(f"AI: {response1.response[:200]}...")
    print(f"情感: {response1.emotion}")
    
    print("\n2. 第二轮对话：用户提供具体信息")
    request2 = ChatRequest(
        message="开心的是，找到了学习大模型应用开发包括RAG的一套很好的资料，焦虑的是，要掌握课程可能比我想象的要花上更多的精力和时间。",
        user_id=user_id,
        session_id=session_id
    )
    
    response2 = await chat_service.chat(request2, use_memory_system=True)
    print(f"用户: {request2.message}")
    print(f"AI: {response2.response[:200]}...")
    print(f"情感: {response2.emotion}")
    
    # 检查回复是否不同
    print("\n3. 分析结果：")
    if response1.response == response2.response:
        print("❌ 问题仍然存在：AI回复完全相同")
        print("需要进一步调试上下文传递机制")
    else:
        print("✅ 修复成功：AI回复已根据新信息调整")
        print("上下文传递机制工作正常")
    
    # 显示详细的回复差异
    print(f"\n回复1长度: {len(response1.response)}")
    print(f"回复2长度: {len(response2.response)}")
    
    # 计算相似度（简单字符匹配）
    common_chars = sum(1 for c1, c2 in zip(response1.response, response2.response) if c1 == c2)
    similarity = common_chars / max(len(response1.response), len(response2.response))
    print(f"回复相似度: {similarity:.2%}")
    
    if similarity > 0.8:
        print("⚠️  回复相似度过高，可能仍存在问题")
    else:
        print("✅ 回复相似度合理，说明AI能够根据新信息调整回复")

async def test_context_length():
    """测试上下文长度是否足够"""
    print("\n" + "=" * 60)
    print("测试上下文长度")
    print("=" * 60)
    
    chat_service = ChatService()
    user_id = "test_user_002"
    session_id = "test_session_002"
    
    # 发送多轮对话
    messages = [
        "我今天心情不太好",
        "因为工作上遇到了一些困难",
        "我的项目进度落后了",
        "老板对我有些不满",
        "我担心会影响我的职业发展",
        "但是我也在努力学习新技能",
        "比如最近在学习AI和机器学习",
        "希望能够提升自己的竞争力",
        "你觉得我应该怎么办？"  # 这条消息应该能引用前面的所有上下文
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n第{i}轮对话:")
        request = ChatRequest(
            message=msg,
            user_id=user_id,
            session_id=session_id
        )
        
        response = await chat_service.chat(request, use_memory_system=True)
        print(f"用户: {msg}")
        print(f"AI: {response.response[:150]}...")
        
        # 在最后一轮检查AI是否能引用前面的上下文
        if i == len(messages):
            context_keywords = ["工作", "项目", "老板", "学习", "AI", "机器学习"]
            mentioned_keywords = [kw for kw in context_keywords if kw in response.response]
            
            print(f"\n上下文关键词检查:")
            print(f"期望关键词: {context_keywords}")
            print(f"AI提及的关键词: {mentioned_keywords}")
            print(f"上下文覆盖率: {len(mentioned_keywords)}/{len(context_keywords)} = {len(mentioned_keywords)/len(context_keywords):.1%}")
            
            if len(mentioned_keywords) >= 3:
                print("✅ AI能够很好地利用对话历史上下文")
            elif len(mentioned_keywords) >= 1:
                print("⚠️  AI部分利用了对话历史，但可能需要改进")
            else:
                print("❌ AI没有有效利用对话历史上下文")

async def main():
    """主测试函数"""
    try:
        await test_conversation_context()
        await test_context_length()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        print("\n如果测试显示问题仍然存在，请检查：")
        print("1. 数据库连接是否正常")
        print("2. LLM API配置是否正确")
        print("3. 消息保存和读取是否正常")
        print("4. 上下文构建逻辑是否正确")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())