#!/usr/bin/env python3
"""
直接查询数据库调试删除问题
"""
import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.database import DatabaseManager, ChatMessage
from sqlalchemy import text

def debug_database_direct():
    """直接查询数据库调试删除问题"""
    print("🔍 直接查询数据库调试删除问题")
    print("=" * 50)
    
    # 创建测试会话
    session_id = f"db_debug_{int(time.time())}"
    user_id = "db_debug_user"
    
    print(f"会话ID: {session_id}")
    print(f"用户ID: {user_id}")
    
    try:
        with DatabaseManager() as db:
            # 1. 手动插入测试数据
            print("\n1. 插入测试数据...")
            
            # 插入用户消息
            user_message = db.save_message(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content="这是一条测试用户消息"
            )
            print(f"✅ 用户消息已插入: ID={user_message.id}, 时间={user_message.created_at}")
            
            # 稍微延迟一下，确保时间戳不同
            time.sleep(0.1)
            
            # 插入AI回复
            ai_message = db.save_message(
                session_id=session_id,
                user_id=user_id,  # 注意：AI消息使用相同的user_id
                role="assistant",
                content="这是对应的AI回复消息"
            )
            print(f"✅ AI消息已插入: ID={ai_message.id}, 时间={ai_message.created_at}")
            
            # 2. 查询所有消息
            print(f"\n2. 查询会话中的所有消息...")
            all_messages = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            print(f"会话中共有 {len(all_messages)} 条消息:")
            for i, msg in enumerate(all_messages):
                print(f"  {i+1}. ID: {msg.id}")
                print(f"     角色: {msg.role}")
                print(f"     用户ID: {msg.user_id}")
                print(f"     时间: {msg.created_at}")
                print(f"     内容: {msg.content}")
                print()
            
            # 3. 测试删除逻辑
            print(f"3. 测试删除逻辑...")
            print(f"要删除的用户消息: ID={user_message.id}")
            
            # 模拟删除逻辑
            messages_to_delete = [user_message]
            
            # 查找AI回复
            print(f"查找用户消息 {user_message.id} 之后的AI回复...")
            ai_responses = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == user_message.session_id,
                ChatMessage.role == 'assistant',
                ChatMessage.created_at > user_message.created_at
            ).order_by(ChatMessage.created_at.asc()).all()
            
            print(f"找到 {len(ai_responses)} 条AI回复:")
            for ai_resp in ai_responses:
                print(f"  - AI消息 ID: {ai_resp.id}, 时间: {ai_resp.created_at}")
                time_diff = (ai_resp.created_at - user_message.created_at).total_seconds()
                print(f"    时间差: {time_diff}秒")
                
            if ai_responses:
                first_ai = ai_responses[0]
                messages_to_delete.append(first_ai)
                print(f"✅ 将删除AI回复: {first_ai.id}")
            else:
                print("❌ 未找到AI回复")
                
                # 检查所有AI消息
                all_ai = db.db.query(ChatMessage).filter(
                    ChatMessage.session_id == session_id,
                    ChatMessage.role == 'assistant'
                ).all()
                
                print(f"会话中所有AI消息 ({len(all_ai)} 条):")
                for ai_msg in all_ai:
                    time_diff = (ai_msg.created_at - user_message.created_at).total_seconds()
                    print(f"  - ID: {ai_msg.id}, 时间差: {time_diff}秒")
                    print(f"    用户消息时间: {user_message.created_at}")
                    print(f"    AI消息时间: {ai_msg.created_at}")
                    print(f"    时间比较: {ai_msg.created_at} > {user_message.created_at} = {ai_msg.created_at > user_message.created_at}")
            
            # 4. 执行实际删除
            print(f"\n4. 执行实际删除...")
            result = db.delete_message(user_message.id, user_id)
            
            if result.get("success"):
                print(f"✅ 删除成功")
                print(f"删除数量: {result.get('deleted_count')}")
                print(f"删除ID: {result.get('deleted_messages')}")
            else:
                print(f"❌ 删除失败: {result.get('error')}")
            
            # 5. 验证删除结果
            print(f"\n5. 验证删除结果...")
            remaining_messages = db.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).all()
            
            print(f"删除后剩余 {len(remaining_messages)} 条消息:")
            for msg in remaining_messages:
                print(f"  - ID: {msg.id}, 角色: {msg.role}, 内容: {msg.content[:30]}...")
            
            if len(remaining_messages) == 0:
                print("✅ 所有消息都被删除了")
            elif len(remaining_messages) == len(all_messages) - 2:
                print("✅ 用户消息和AI回复都被删除了")
            elif len(remaining_messages) == len(all_messages) - 1:
                print("⚠️ 只删除了1条消息，可能是AI回复未被删除")
            else:
                print(f"❓ 意外的删除结果")
                
    except Exception as e:
        print(f"❌ 调试过程异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_direct()