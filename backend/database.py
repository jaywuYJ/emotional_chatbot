#!/usr/bin/env python3
"""
数据库配置和模型定义
"""
import os
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 数据库配置
# 从环境变量获取数据库URL，如果没有设置则从各个组件构建
_default_db_url = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:"
    f"{os.getenv('MYSQL_PASSWORD', '')}@"
    f"{os.getenv('MYSQL_HOST', 'localhost')}:"
    f"{os.getenv('MYSQL_PORT', '3306')}/"
    f"{os.getenv('MYSQL_DATABASE', 'emotional_chat')}"
)
DATABASE_URL = os.getenv("DATABASE_URL", _default_db_url)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    username = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    emotion = Column(String(50))  # 情感标签
    emotion_intensity = Column(Float)  # 情感强度
    created_at = Column(DateTime, default=datetime.utcnow)

class EmotionAnalysis(Base):
    """情感分析记录表"""
    __tablename__ = "emotion_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    message_id = Column(BigInteger)  # 关联到chat_messages.id
    emotion = Column(String(50))
    intensity = Column(Float)
    keywords = Column(Text)  # JSON格式存储关键词
    suggestions = Column(Text)  # JSON格式存储建议
    created_at = Column(DateTime, default=datetime.utcnow)

class Knowledge(Base):
    """知识库表"""
    __tablename__ = "knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    category = Column(String(100))
    tags = Column(Text)  # JSON格式存储标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20))  # INFO, WARNING, ERROR
    message = Column(Text)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserFeedback(Base):
    """用户反馈表"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    message_id = Column(BigInteger, index=True)  # 关联到chat_messages.id
    feedback_type = Column(String(50))  # irrelevant(答非所问), lack_empathy(缺乏共情), overstepping(越界建议), helpful(有帮助), other
    rating = Column(Integer)  # 1-5分评分
    comment = Column(Text)  # 用户的详细评论
    user_message = Column(Text)  # 用户消息内容（快照）
    bot_response = Column(Text)  # 机器人回复内容（快照）
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)  # 是否已处理优化

class ResponseEvaluation(Base):
    """回应评估表 - 存储LLM自动评估结果"""
    __tablename__ = "response_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    message_id = Column(BigInteger, index=True)  # 关联到chat_messages.id
    
    # 评估对象
    user_message = Column(Text)  # 用户消息（快照）
    bot_response = Column(Text)  # 机器人回复（快照）
    user_emotion = Column(String(50))  # 用户情感
    emotion_intensity = Column(Float)  # 情感强度
    
    # 评估维度分数 (1-5)
    empathy_score = Column(Float)  # 共情程度
    naturalness_score = Column(Float)  # 自然度
    safety_score = Column(Float)  # 安全性
    
    # 总分和平均分
    total_score = Column(Float)  # 总分 (三个维度之和)
    average_score = Column(Float)  # 平均分
    
    # 评估详情 (JSON格式)
    empathy_reasoning = Column(Text)  # 共情评价理由
    naturalness_reasoning = Column(Text)  # 自然度评价理由
    safety_reasoning = Column(Text)  # 安全性评价理由
    overall_comment = Column(Text)  # 总体评价
    strengths = Column(Text)  # 优点 (JSON数组)
    weaknesses = Column(Text)  # 缺点 (JSON数组)
    improvement_suggestions = Column(Text)  # 改进建议 (JSON数组)
    
    # 元数据
    evaluation_model = Column(String(100))  # 使用的评估模型
    prompt_version = Column(String(50))  # Prompt版本（可选，用于A/B测试）
    is_human_verified = Column(Boolean, default=False)  # 是否经过人工验证
    human_rating_diff = Column(Float)  # 人工评分与AI评分的差异（可选）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserProfileDB(Base):
    """用户画像表 - 存储用户的基本信息和特征"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    
    # 基本信息
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    
    # 用户特征 (JSON格式存储)
    personality_traits = Column(Text)  # 性格特征列表
    interests = Column(Text)  # 兴趣爱好列表
    concerns = Column(Text)  # 长期关注的问题列表
    
    # 沟通偏好
    communication_style = Column(String(50), default="默认")  # 沟通风格偏好
    emotional_baseline = Column(String(50), default="稳定")  # 情绪基线
    
    # 统计信息
    total_sessions = Column(Integer, default=0)  # 总会话数
    total_messages = Column(Integer, default=0)  # 总消息数
    avg_emotion_intensity = Column(Float)  # 平均情绪强度
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MemoryItem(Base):
    """记忆条目表 - 存储结构化的用户记忆（配合向量数据库使用）"""
    __tablename__ = "memory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(String(100), unique=True, index=True)  # 对应向量数据库中的ID
    user_id = Column(String(100), index=True)
    session_id = Column(String(100), index=True)
    
    # 记忆内容
    content = Column(Text)  # 原始内容
    summary = Column(Text)  # 摘要
    memory_type = Column(String(50))  # event, relationship, commitment, preference, concern
    
    # 关联信息
    emotion = Column(String(50))  # 相关情绪
    emotion_intensity = Column(Float)  # 情绪强度
    importance = Column(Float)  # 重要性评分 (0-1)
    
    # 提取信息
    extraction_method = Column(String(50))  # rule_based, llm_based
    keywords = Column(Text)  # 关键词 (JSON数组)
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否活跃（可以设置为False来软删除）
    access_count = Column(Integer, default=0)  # 被检索次数
    last_accessed = Column(DateTime)  # 最后访问时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPersonalization(Base):
    """用户个性化配置表 - 存储用户的AI伙伴定制设置"""
    __tablename__ = "user_personalizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    
    # 角色层：AI身份与人格
    role = Column(String(100), default="温暖倾听者")  # 角色类型
    role_name = Column(String(100), default="心语")  # 角色名称
    role_background = Column(Text)  # 角色背景故事
    personality = Column(String(100), default="温暖耐心")  # 性格特征
    core_principles = Column(Text)  # 核心原则 (JSON数组)
    forbidden_behaviors = Column(Text)  # 禁忌行为 (JSON数组)
    
    # 表达层：风格与语气
    tone = Column(String(50), default="温和")  # 语气: 温和/活泼/正式/幽默
    style = Column(String(50), default="简洁")  # 风格: 简洁/详细/诗意/直接
    formality = Column(Float, default=0.3)  # 正式程度 (0-1)
    enthusiasm = Column(Float, default=0.5)  # 活泼度 (0-1)
    empathy_level = Column(Float, default=0.8)  # 共情程度 (0-1)
    humor_level = Column(Float, default=0.3)  # 幽默程度 (0-1)
    response_length = Column(String(20), default="medium")  # 回复长度: short/medium/long
    use_emoji = Column(Boolean, default=False)  # 是否使用emoji
    
    # 记忆层：长期偏好
    preferred_topics = Column(Text)  # 偏好话题 (JSON数组)
    avoided_topics = Column(Text)  # 避免话题 (JSON数组)
    communication_preferences = Column(Text)  # 沟通偏好 (JSON对象)
    
    # 高级设置
    learning_mode = Column(Boolean, default=True)  # 是否启用学习模式
    safety_level = Column(String(20), default="standard")  # 安全级别: strict/standard/relaxed
    context_window = Column(Integer, default=10)  # 上下文窗口大小
    
    # 情境化角色（多角色支持）
    situational_roles = Column(Text)  # 情境角色配置 (JSON对象)
    active_role = Column(String(50), default="default")  # 当前激活的角色
    
    # 统计信息
    total_interactions = Column(Integer, default=0)  # 总交互次数
    positive_feedbacks = Column(Integer, default=0)  # 正向反馈次数
    config_version = Column(Integer, default=1)  # 配置版本号
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建所有表
def create_tables():
    """
    创建数据库表（不推荐直接使用）
    
    警告：请使用 Alembic 迁移系统来管理数据库结构变更
    使用命令：python db_manager.py init
    
    仅在特殊情况下（如测试环境快速建表）才直接调用此函数
    """
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库操作类
class DatabaseManager:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def save_message(self, session_id, user_id, role, content, emotion=None, emotion_intensity=None):
        """保存聊天消息"""
        message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id, limit=50):
        """获取会话消息"""
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
    
    def save_emotion_analysis(self, session_id, user_id, message_id, emotion, intensity, keywords, suggestions):
        """保存情感分析结果"""
        analysis = EmotionAnalysis(
            session_id=session_id,
            user_id=user_id,
            message_id=message_id,
            emotion=emotion,
            intensity=intensity,
            keywords=str(keywords),
            suggestions=str(suggestions)
        )
        self.db.add(analysis)
        self.db.commit()
        return analysis
    
    def get_user_emotion_history(self, user_id, limit=100):
        """获取用户情感历史"""
        return self.db.query(EmotionAnalysis)\
            .filter(EmotionAnalysis.user_id == user_id)\
            .order_by(EmotionAnalysis.created_at.desc())\
            .limit(limit)\
            .all()
    
    def save_knowledge(self, title, content, category, tags=None):
        """保存知识"""
        knowledge = Knowledge(
            title=title,
            content=content,
            category=category,
            tags=str(tags) if tags else None
        )
        self.db.add(knowledge)
        self.db.commit()
        return knowledge
    
    def search_knowledge(self, query, category=None, limit=10):
        """搜索知识"""
        q = self.db.query(Knowledge).filter(Knowledge.is_active == True)
        if category:
            q = q.filter(Knowledge.category == category)
        # 简单的文本搜索，可以后续优化为全文搜索
        q = q.filter(Knowledge.content.contains(query))
        return q.limit(limit).all()
    
    def log_system_event(self, level, message, session_id=None, user_id=None):
        """记录系统日志"""
        log = SystemLog(
            level=level,
            message=message,
            session_id=session_id,
            user_id=user_id
        )
        self.db.add(log)
        self.db.commit()
        return log
    
    def get_user_sessions(self, user_id, limit=50):
        """获取用户的所有会话"""
        return self.db.query(ChatSession)\
            .filter(ChatSession.user_id == user_id)\
            .order_by(ChatSession.updated_at.desc())\
            .limit(limit)\
            .all()
    
    def get_message(self, message_id, user_id=None):
        """获取特定消息"""
        # 尝试将message_id转换为整数，如果失败则直接返回None
        try:
            message_id_int = int(message_id)
        except ValueError:
            return None
            
        query = self.db.query(ChatMessage).filter(ChatMessage.id == message_id_int)
        if user_id:
            query = query.filter(ChatMessage.user_id == user_id)
        return query.first()
    
    def update_message(self, message_id, user_id, new_content, emotion=None, emotion_intensity=None):
        """更新消息内容"""
        message = self.get_message(message_id, user_id)
        if not message:
            return None
        
        # 验证内容不为空
        if not new_content or not new_content.strip():
            raise ValueError("消息内容不能为空")
        
        message.content = new_content.strip()
        if emotion is not None:
            message.emotion = emotion
        if emotion_intensity is not None:
            message.emotion_intensity = emotion_intensity
        
        # 更新修改时间（如果有该字段）
        from datetime import datetime
        if hasattr(message, 'updated_at'):
            message.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def delete_message(self, message_id, user_id):
        """删除（撤回）消息，如果是用户消息，同时删除对应的AI回复"""
        print(f"[DELETE] 开始删除消息: message_id={message_id}, user_id={user_id}")
        
        message = self.get_message(message_id, user_id)
        if not message:
            print(f"[DELETE] 消息不存在或无权删除: message_id={message_id}, user_id={user_id}")
            return {
                "success": False,
                "error": "消息不存在或无权删除"
            }
        
        print(f"[DELETE] 找到消息: {message.id}, 角色: {message.role}, 内容: {message.content[:50]}...")
        
        try:
            messages_to_delete = [message]
            
            # 如果是用户消息，查找对应的AI回复
            if message.role == 'user':
                print(f"[DELETE] 查找用户消息 {message.id} 对应的AI回复...")
                print(f"[DELETE] 用户消息时间: {message.created_at}")
                print(f"[DELETE] 会话ID: {message.session_id}")
                
                # 首先查看该会话中的所有AI消息
                all_ai_messages = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id == message.session_id,
                    ChatMessage.role == 'assistant'
                ).order_by(ChatMessage.created_at.asc()).all()
                
                print(f"[DELETE] 会话中总共有 {len(all_ai_messages)} 条AI消息")
                for ai_msg in all_ai_messages:
                    print(f"[DELETE]   AI消息 {ai_msg.id}: 时间={ai_msg.created_at}, 用户ID={ai_msg.user_id}")
                    time_diff = (ai_msg.created_at - message.created_at).total_seconds()
                    print(f"[DELETE]   时间差: {time_diff}秒 ({'之后' if time_diff > 0 else '之前'})")
                
                # 查找该用户消息之后的AI回复
                ai_responses = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id == message.session_id,
                    ChatMessage.role == 'assistant',
                    ChatMessage.created_at > message.created_at
                ).order_by(ChatMessage.created_at.asc()).all()
                
                print(f"[DELETE] 用户消息之后找到 {len(ai_responses)} 条AI回复")
                
                if ai_responses:
                    # 只删除紧接着的第一条AI回复
                    first_ai_response = ai_responses[0]
                    print(f"[DELETE] 将删除第一条AI回复: {first_ai_response.id}, 内容: {first_ai_response.content[:50]}...")
                    messages_to_delete.append(first_ai_response)
                else:
                    print(f"[DELETE] 未找到用户消息之后的AI回复")
                    
                    # 如果没找到，尝试查找最近的AI回复（可能时间戳有微小差异）
                    print(f"[DELETE] 尝试查找最近的AI回复...")
                    recent_ai = self.db.query(ChatMessage).filter(
                        ChatMessage.session_id == message.session_id,
                        ChatMessage.role == 'assistant'
                    ).order_by(ChatMessage.created_at.desc()).first()
                    
                    if recent_ai:
                        print(f"[DELETE] 找到最近的AI回复: {recent_ai.id}, 时间: {recent_ai.created_at}")
                        # 如果AI回复的时间在用户消息时间的5分钟内，认为是对应的回复
                        time_diff = abs((recent_ai.created_at - message.created_at).total_seconds())
                        if time_diff <= 300:  # 5分钟内
                            print(f"[DELETE] AI回复时间差在5分钟内({time_diff}秒)，认为是对应回复")
                            messages_to_delete.append(recent_ai)
                        else:
                            print(f"[DELETE] AI回复时间差过大({time_diff}秒)，不删除")
                    
                    # 如果还是没找到，尝试更简单的策略：删除该会话中的最后一条AI消息
                    if len(messages_to_delete) == 1:  # 只有用户消息
                        print(f"[DELETE] 尝试删除该会话中的最后一条AI消息...")
                        last_ai = self.db.query(ChatMessage).filter(
                            ChatMessage.session_id == message.session_id,
                            ChatMessage.role == 'assistant'
                        ).order_by(ChatMessage.id.desc()).first()  # 按ID降序，获取最新的
                        
                        if last_ai:
                            print(f"[DELETE] 找到最后一条AI消息: {last_ai.id}")
                            messages_to_delete.append(last_ai)
            
            # 删除所有相关消息及其关联数据
            total_deleted = 0
            deleted_message_ids = []
            
            for msg_to_delete in messages_to_delete:
                print(f"[DELETE] 删除消息: {msg_to_delete.id} ({msg_to_delete.role})")
                
                # 删除相关的情感分析记录
                emotion_count = self.db.query(EmotionAnalysis).filter(EmotionAnalysis.message_id == msg_to_delete.id).count()
                if emotion_count > 0:
                    self.db.query(EmotionAnalysis).filter(EmotionAnalysis.message_id == msg_to_delete.id).delete()
                    print(f"[DELETE] 删除了 {emotion_count} 条情感分析记录 (消息 {msg_to_delete.id})")
                
                # 删除相关的反馈记录
                feedback_count = self.db.query(UserFeedback).filter(UserFeedback.message_id == msg_to_delete.id).count()
                if feedback_count > 0:
                    self.db.query(UserFeedback).filter(UserFeedback.message_id == msg_to_delete.id).delete()
                    print(f"[DELETE] 删除了 {feedback_count} 条反馈记录 (消息 {msg_to_delete.id})")
                
                # 删除相关的评估记录
                eval_count = self.db.query(ResponseEvaluation).filter(ResponseEvaluation.message_id == msg_to_delete.id).count()
                if eval_count > 0:
                    self.db.query(ResponseEvaluation).filter(ResponseEvaluation.message_id == msg_to_delete.id).delete()
                    print(f"[DELETE] 删除了 {eval_count} 条评估记录 (消息 {msg_to_delete.id})")
                
                # 记录要删除的消息ID
                deleted_message_ids.append(msg_to_delete.id)
                
                # 删除消息本身
                self.db.delete(msg_to_delete)
                total_deleted += 1
            
            self.db.commit()
            print(f"[DELETE] 成功删除 {total_deleted} 条消息: {deleted_message_ids}")
            return {
                "success": True,
                "deleted_count": total_deleted,
                "deleted_messages": deleted_message_ids
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"[DELETE] 删除消息失败: {e}")
            import traceback
            print(f"[DELETE] 错误堆栈: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_session(self, session_id, user_id):
        """创建新会话"""
        session = ChatSession(
            session_id=session_id,
            user_id=user_id
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def delete_session(self, session_id):
        """删除会话及其相关数据"""
        try:
            # 删除会话相关的所有消息
            self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            
            # 删除会话相关的反馈
            self.db.query(UserFeedback).filter(UserFeedback.session_id == session_id).delete()
            
            # 删除会话相关的系统日志
            self.db.query(SystemLog).filter(SystemLog.session_id == session_id).delete()
            
            # 删除会话记录
            deleted_count = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).delete()
            
            self.db.commit()
            return deleted_count > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def save_feedback(self, session_id, user_id, message_id, feedback_type, rating, comment, user_message, bot_response):
        """保存用户反馈"""
        feedback = UserFeedback(
            session_id=session_id,
            user_id=user_id,
            message_id=message_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            user_message=user_message,
            bot_response=bot_response
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
    
    def get_all_feedback(self, feedback_type=None, limit=1000):
        """获取所有反馈"""
        query = self.db.query(UserFeedback)
        if feedback_type:
            query = query.filter(UserFeedback.feedback_type == feedback_type)
        return query.order_by(UserFeedback.created_at.desc()).limit(limit).all()
    
    def get_feedback_by_session(self, session_id):
        """获取特定会话的反馈"""
        return self.db.query(UserFeedback)\
            .filter(UserFeedback.session_id == session_id)\
            .order_by(UserFeedback.created_at.desc())\
            .all()
    
    def get_feedback_statistics(self):
        """获取反馈统计信息"""
        from sqlalchemy import func
        
        # 按类型统计
        type_stats = self.db.query(
            UserFeedback.feedback_type,
            func.count(UserFeedback.id).label('count'),
            func.avg(UserFeedback.rating).label('avg_rating')
        ).group_by(UserFeedback.feedback_type).all()
        
        # 总体统计
        total_count = self.db.query(func.count(UserFeedback.id)).scalar()
        avg_rating = self.db.query(func.avg(UserFeedback.rating)).scalar()
        
        return {
            'total_count': total_count or 0,
            'avg_rating': float(avg_rating) if avg_rating else 0.0,
            'by_type': [
                {
                    'type': stat.feedback_type,
                    'count': stat.count,
                    'avg_rating': float(stat.avg_rating) if stat.avg_rating else 0.0
                }
                for stat in type_stats
            ]
        }
    
    def mark_feedback_resolved(self, feedback_id):
        """标记反馈已解决"""
        feedback = self.db.query(UserFeedback).filter(UserFeedback.id == feedback_id).first()
        if feedback:
            feedback.is_resolved = True
            self.db.commit()
        return feedback
    
    def save_evaluation(self, evaluation_data):
        """保存评估结果"""
        import json
        
        evaluation = ResponseEvaluation(
            session_id=evaluation_data.get("session_id"),
            user_id=evaluation_data.get("user_id", "anonymous"),
            message_id=evaluation_data.get("message_id"),
            user_message=evaluation_data.get("user_message"),
            bot_response=evaluation_data.get("bot_response"),
            user_emotion=evaluation_data.get("user_emotion"),
            emotion_intensity=evaluation_data.get("emotion_intensity"),
            empathy_score=evaluation_data.get("empathy_score"),
            naturalness_score=evaluation_data.get("naturalness_score"),
            safety_score=evaluation_data.get("safety_score"),
            total_score=evaluation_data.get("total_score"),
            average_score=evaluation_data.get("average_score"),
            empathy_reasoning=evaluation_data.get("empathy_reasoning"),
            naturalness_reasoning=evaluation_data.get("naturalness_reasoning"),
            safety_reasoning=evaluation_data.get("safety_reasoning"),
            overall_comment=evaluation_data.get("overall_comment"),
            strengths=json.dumps(evaluation_data.get("strengths", []), ensure_ascii=False),
            weaknesses=json.dumps(evaluation_data.get("weaknesses", []), ensure_ascii=False),
            improvement_suggestions=json.dumps(evaluation_data.get("improvement_suggestions", []), ensure_ascii=False),
            evaluation_model=evaluation_data.get("model"),
            prompt_version=evaluation_data.get("prompt_version"),
            is_human_verified=evaluation_data.get("is_human_verified", False),
            human_rating_diff=evaluation_data.get("human_rating_diff")
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation
    
    def get_evaluations(self, session_id=None, limit=100):
        """获取评估结果列表"""
        query = self.db.query(ResponseEvaluation)
        if session_id:
            query = query.filter(ResponseEvaluation.session_id == session_id)
        return query.order_by(ResponseEvaluation.created_at.desc()).limit(limit).all()
    
    def get_evaluation_statistics(self, start_date=None, end_date=None):
        """获取评估统计信息"""
        from sqlalchemy import func
        
        query = self.db.query(ResponseEvaluation)
        if start_date:
            query = query.filter(ResponseEvaluation.created_at >= start_date)
        if end_date:
            query = query.filter(ResponseEvaluation.created_at <= end_date)
        
        evaluations = query.all()
        
        if not evaluations:
            return {
                "total_count": 0,
                "average_scores": {
                    "empathy": 0,
                    "naturalness": 0,
                    "safety": 0,
                    "overall": 0
                }
            }
        
        total_count = len(evaluations)
        avg_empathy = sum(e.empathy_score or 0 for e in evaluations) / total_count
        avg_naturalness = sum(e.naturalness_score or 0 for e in evaluations) / total_count
        avg_safety = sum(e.safety_score or 0 for e in evaluations) / total_count
        avg_overall = sum(e.average_score or 0 for e in evaluations) / total_count
        
        return {
            "total_count": total_count,
            "average_scores": {
                "empathy": round(avg_empathy, 2),
                "naturalness": round(avg_naturalness, 2),
                "safety": round(avg_safety, 2),
                "overall": round(avg_overall, 2)
            },
            "score_ranges": {
                "empathy": {
                    "min": min(e.empathy_score or 0 for e in evaluations),
                    "max": max(e.empathy_score or 0 for e in evaluations)
                },
                "naturalness": {
                    "min": min(e.naturalness_score or 0 for e in evaluations),
                    "max": max(e.naturalness_score or 0 for e in evaluations)
                },
                "safety": {
                    "min": min(e.safety_score or 0 for e in evaluations),
                    "max": max(e.safety_score or 0 for e in evaluations)
                }
            }
        }
    
    def update_evaluation_human_verification(self, evaluation_id, human_scores):
        """更新评估的人工验证数据"""
        evaluation = self.db.query(ResponseEvaluation).filter(ResponseEvaluation.id == evaluation_id).first()
        if evaluation:
            evaluation.is_human_verified = True
            # 计算人工评分与AI评分的差异
            ai_avg = evaluation.average_score or 0
            human_avg = (
                human_scores.get("empathy", 0) +
                human_scores.get("naturalness", 0) +
                human_scores.get("safety", 0)
            ) / 3.0
            evaluation.human_rating_diff = round(human_avg - ai_avg, 2)
            self.db.commit()
            self.db.refresh(evaluation)
        return evaluation