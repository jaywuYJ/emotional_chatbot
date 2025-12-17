-- 消息编辑和撤回功能相关索引
-- 为提高查询性能而添加

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id_created_at ON chat_messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_role ON chat_messages(session_id, role);

-- 情感分析表索引
CREATE INDEX IF NOT EXISTS idx_emotion_analysis_message_id ON emotion_analysis(message_id);

-- 用户反馈表索引
CREATE INDEX IF NOT EXISTS idx_user_feedback_message_id ON user_feedback(message_id);

-- 评估表索引
CREATE INDEX IF NOT EXISTS idx_response_evaluations_message_id ON response_evaluations(message_id);
