#!/usr/bin/env python3
"""
消息编辑和撤回功能数据库迁移脚本
"""

from backend.database import DatabaseManager, ChatMessage
from sqlalchemy import text

def add_updated_at_column():
    """为消息表添加updated_at字段"""
    try:
        with DatabaseManager() as db:
            # 检查字段是否已存在
            result = db.db.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'chat_messages' 
                AND column_name = 'updated_at'
            """)).fetchone()
            
            if result.count == 0:
                # 添加updated_at字段
                db.db.execute(text("""
                    ALTER TABLE chat_messages 
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """))
                db.db.commit()
                print("✓ 已添加updated_at字段到chat_messages表")
            else:
                print("✓ updated_at字段已存在")
                
    except Exception as e:
        print(f"添加updated_at字段失败: {e}")

def add_message_version_tracking():
    """添加消息版本跟踪表"""
    try:
        with DatabaseManager() as db:
            # 创建消息版本历史表
            db.db.execute(text("""
                CREATE TABLE IF NOT EXISTS message_edit_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message_id INT NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    old_content TEXT,
                    new_content TEXT,
                    edit_reason VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_message_edit_history_message_id (message_id),
                    INDEX idx_message_edit_history_user_id (user_id)
                )
            """))
            db.db.commit()
            print("✓ 已创建消息编辑历史表")
            
    except Exception as e:
        print(f"创建消息编辑历史表失败: {e}")

def run_migration():
    """运行迁移"""
    print("开始数据库迁移...")
    add_updated_at_column()
    add_message_version_tracking()
    print("数据库迁移完成")

if __name__ == "__main__":
    run_migration()
