import React, { useState } from 'react';
import ChatAPI from '../services/ChatAPI';

import { AnimatePresence } from 'framer-motion';
import { User, Bot, Loader2, Paperclip, Send, Link, ExternalLink, X, Sparkles, Mic, PenLine, Image, Music, Languages, Presentation, MoreHorizontal } from 'lucide-react';
import {
  ChatContainer as ChatContainerStyled,
  MessagesContainer,
  MessageBubble,
  Avatar,
  MessageWrapper,
  MessageContent,
  FeedbackButtons,
  FeedbackButton,
  EmotionTag,
  MessageTimestamp,
  Suggestions,
  SuggestionChip,
  WelcomeMessage,
  LoadingIndicator,
  InputContainer
} from '../styles';
import {
  InputWrapper,
  InputBox,
  MessageInput,
  InputActions,
  LeftActions,
  RightActions,
  AttachmentButton,
  SendButton,
  FileInput,
  AttachmentsPreview,
  AttachmentItem,
  AttachmentIcon,
  RemoveAttachmentButton,
  URLPreview,
  URLText,
  URLButton,
  FeatureButton,
  QuickActions,
  QuickActionButton
} from '../styles/input';
import { emotionLabels } from '../constants/emotions';
import { formatTimestamp, formatFileSize } from '../utils/formatters';
import TypewriterComponent from './TypewriterText';
import { getFileIcon } from '../utils/fileUtils';

// 添加旋转动画的CSS
const spinKeyframes = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 将CSS注入到页面中
if (typeof document !== 'undefined' && !document.getElementById('edit-spinner-styles')) {
  const style = document.createElement('style');
  style.id = 'edit-spinner-styles';
  style.textContent = spinKeyframes;
  document.head.appendChild(style);
}

// 获取问候语
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 6) return '夜深了';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  if (hour < 22) return '晚上好';
  return '夜深了';
};

const ChatContainer = ({
  messages,
  isLoading,
  suggestions,
  inputValue,
  attachments,
  detectedURLs,
  messagesEndRef,
  inputRef,
  attachmentButtonRef,
  sendButtonRef,
  fileInputRef,
  onInputChange,
  onKeyPress,
  onTabNavigation,
  onSendMessage,
  onFileUpload,
  onRemoveAttachment,
  onSuggestionClick,
  onOpenFeedbackModal,
  deepThinkActive,
  onDeepThinkChange,
  onMessageUpdate,
  onMessageDelete
}) => {

  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [isEditingSaving, setIsEditingSaving] = useState(false);
  const [isDeletingMessage, setIsDeletingMessage] = useState(null); // 存储正在删除的消息ID

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
    if (onTabNavigation) {
      onTabNavigation(e);
    }
  };

  // 开始编辑消息
  const handleEditStart = (message) => {
    setEditingMessageId(message.id);
    setEditContent(message.content);
  };

  // 取消编辑
  const handleEditCancel = () => {
    setEditingMessageId(null);
    setEditContent('');
    setIsEditingSaving(false); // 重置加载状态
  };

  // 保存编辑
  const handleEditSave = async (messageId) => {
    // 防止重复提交
    if (isEditingSaving) {
      return;
    }
    
    const trimmedContent = editContent.trim();
    
    // 输入验证
    if (!trimmedContent) {
      alert('消息内容不能为空');
      return;
    }
    
    if (trimmedContent.length > 2000) {
      alert('消息内容过长，最多2000字符');
      return;
    }
    
    // 设置加载状态
    setIsEditingSaving(true);
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) {
        alert('消息不存在');
        return;
      }
      
      // 调试信息
      console.log('编辑消息调试信息:', {
        messageId,
        message,
        dbId: message.dbId,
        user_id: message.user_id,
        content: message.content
      });
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      console.log('发送编辑请求:', {
        dbId,
        user_id: message.user_id || 'anonymous',
        new_content: trimmedContent
      });
      
      const result = await ChatAPI.updateMessage(dbId, {
        user_id: message.user_id || 'anonymous',
        new_content: trimmedContent
      });
      
      console.log('编辑响应结果:', result);
      
      // 处理编辑结果
      if (result.new_response) {
        // 如果有新的AI回复，需要更新整个消息列表
        console.log('检测到新的AI回复，更新消息列表');
        console.log('传递给onMessageUpdate的数据:', {
          id: messageId,
          content: trimmedContent,
          regenerated: true,
          newResponse: result.new_response,
          deletedCount: result.deleted_messages_count
        });
        if (onMessageUpdate) {
          onMessageUpdate({
            id: messageId,
            content: trimmedContent,
            regenerated: true,
            newResponse: result.new_response,
            deletedCount: result.deleted_messages_count
          });
        }
      } else {
        // 只是简单的内容更新
        console.log('简单内容更新');
        if (onMessageUpdate) {
          onMessageUpdate({
            id: messageId,
            content: trimmedContent
          });
        }
      }
      
      // 成功后重置编辑状态
      setEditingMessageId(null);
      setEditContent('');
      
      // 如果有新回复，显示成功提示（使用更温和的提示方式）
      if (result.new_response) {
        console.log('消息已编辑并重新生成了回复');
        // 强制滚动到底部以显示新消息
        setTimeout(() => {
          if (messagesEndRef && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
        
        // 使用更温和的提示方式，避免弹框
        console.log('✅ 消息编辑成功，已重新生成回复');
      } else {
        console.log('✅ 消息内容已更新');
      }
      
    } catch (error) {
      console.error('编辑消息失败:', error);
      
      // 更友好的错误提示
      let errorMessage = '编辑消息失败，请重试';
      if (error.response?.status === 400) {
        errorMessage = error.response.data.detail || '输入内容无效';
      } else if (error.response?.status === 404) {
        errorMessage = '消息不存在或无权修改';
      } else if (error.response?.status === 500) {
        errorMessage = '服务器错误，请稍后重试';
      }
      
      console.error('❌ 编辑失败:', errorMessage);
      
      // 只在严重错误时才弹框，其他情况使用控制台提示
      if (error.response?.status === 404 || error.response?.status === 403) {
        alert(errorMessage);
      } else {
        // 可以在这里添加更温和的错误提示，比如toast通知
        console.log('💡 提示: 可以查看控制台了解详细错误信息');
      }
    } finally {
      // 无论成功还是失败，都重置加载状态
      setIsEditingSaving(false);
    }
  };

  // 撤回消息
  const handleDeleteMessage = async (messageId) => {
    // 防止重复删除
    if (isDeletingMessage === messageId) {
      return;
    }
    
    if (!window.confirm('确定要撤回这条消息吗？撤回后无法恢复。')) return;
    
    // 设置删除状态
    setIsDeletingMessage(messageId);
    
    try {
      const message = messages.find(m => m.id === messageId);
      if (!message) {
        alert('消息不存在');
        return;
      }
      
      // 使用数据库ID而不是前端生成的ID
      const dbId = message.dbId || message.id;
      
      const result = await ChatAPI.deleteMessage(dbId, message.user_id || 'anonymous');
      
      if (onMessageDelete) {
        onMessageDelete(messageId);
      }
    } catch (error) {
      console.error('撤回消息失败:', error);
      
      // 更友好的错误提示
      let errorMessage = '撤回消息失败，请重试';
      if (error.response?.status === 404) {
        errorMessage = '消息不存在或无权撤回';
      } else if (error.response?.status === 500) {
        errorMessage = '服务器错误，请稍后重试';
      }
      
      alert(errorMessage);
    } finally {
      // 重置删除状态
      setIsDeletingMessage(null);
    }
  };

  return (
    <ChatContainerStyled
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <MessagesContainer>
        <AnimatePresence initial={false}>
          {messages.length === 0 ? (
            <WelcomeMessage
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h3>{getGreeting()}，小草</h3>
              <p>
                我是你的情感支持伙伴，随时倾听你的心声。<br/>
                无论开心、难过还是困惑，都可以和我聊聊。
              </p>
            </WelcomeMessage>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                isUser={message.role === 'user'}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Avatar isUser={message.role === 'user'}>
                  {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                </Avatar>
                <MessageWrapper>
                  {editingMessageId === message.id ? (
                    <div style={{ width: '100%' }}>
                      <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        disabled={isEditingSaving}
                        style={{
                          width: '100%',
                          padding: '8px 12px',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          minHeight: '60px',
                          resize: 'vertical',
                          fontSize: '14px',
                          fontFamily: 'inherit',
                          opacity: isEditingSaving ? 0.6 : 1,
                          cursor: isEditingSaving ? 'not-allowed' : 'text'
                        }}
                        autoFocus
                      />
                      <div style={{ 
                        display: 'flex', 
                        gap: '8px', 
                        marginTop: '8px', 
                        justifyContent: 'flex-end'
                      }}>
                        <button
                          onClick={handleEditCancel}
                          disabled={isEditingSaving}
                          style={{
                            padding: '4px 12px',
                            borderRadius: '4px',
                            border: '1px solid #e5e7eb',
                            background: isEditingSaving ? '#f3f4f6' : 'white',
                            cursor: isEditingSaving ? 'not-allowed' : 'pointer',
                            fontSize: '12px',
                            opacity: isEditingSaving ? 0.6 : 1
                          }}
                        >
                          取消
                        </button>
                        <button
                          onClick={() => handleEditSave(message.id)}
                          disabled={isEditingSaving}
                          style={{
                            padding: '4px 12px',
                            borderRadius: '4px',
                            border: '1px solid #6366f1',
                            background: isEditingSaving ? '#9ca3af' : '#6366f1',
                            color: 'white',
                            cursor: isEditingSaving ? 'not-allowed' : 'pointer',
                            fontSize: '12px',
                            opacity: isEditingSaving ? 0.8 : 1,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          {isEditingSaving ? (
                            <>
                              <div style={{
                                width: '12px',
                                height: '12px',
                                border: '2px solid #ffffff',
                                borderTop: '2px solid transparent',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite'
                              }} />
                              保存中...
                            </>
                          ) : (
                            '保存'
                          )}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <MessageContent 
                        isUser={message.role === 'user'}
                        emotion={message.emotion}
                      >
                        {message.role === 'assistant' && !message.isHistory ? (
                          <TypewriterComponent
                            text={message.content}
                            speed={30}
                            showCursor={true}
                            cursorColor="#6366f1"
                            isUser={false}
                          />
                        ) : (
                          message.content
                        )}
                        {message.emotion && message.emotion !== 'neutral' && (
                          <EmotionTag emotion={message.emotion}>
                            {emotionLabels[message.emotion] || message.emotion}
                          </EmotionTag>
                        )}
                      </MessageContent>
                      <MessageTimestamp isUser={message.role === 'user'}>
                        {formatTimestamp(message.timestamp)}
                      </MessageTimestamp>
                      {message.role === 'assistant' && (
                        <FeedbackButtons>
                          <FeedbackButton
                            onClick={() => onOpenFeedbackModal(message)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            反馈
                          </FeedbackButton>
                        </FeedbackButtons>
                      )}
                      {message.role === 'user' && (
                        <div style={{ 
                          display: 'flex', 
                          gap: '8px', 
                          marginTop: '4px' 
                        }}>
                          <button
                            onClick={() => handleEditStart(message)}
                            disabled={isEditingSaving || isDeletingMessage === message.id}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: (isEditingSaving || isDeletingMessage === message.id) ? '#d1d5db' : '#9ca3af',
                              fontSize: '12px',
                              cursor: (isEditingSaving || isDeletingMessage === message.id) ? 'not-allowed' : 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '2px',
                              opacity: (isEditingSaving || isDeletingMessage === message.id) ? 0.5 : 1
                            }}
                          >
                            <PenLine size={12} />
                            编辑
                          </button>
                          <button
                            onClick={() => handleDeleteMessage(message.id)}
                            disabled={isEditingSaving || isDeletingMessage === message.id}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: isDeletingMessage === message.id ? '#ef4444' : (isEditingSaving ? '#d1d5db' : '#9ca3af'),
                              fontSize: '12px',
                              cursor: (isEditingSaving || isDeletingMessage === message.id) ? 'not-allowed' : 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '2px',
                              opacity: isEditingSaving ? 0.5 : 1
                            }}
                          >
                            {isDeletingMessage === message.id ? (
                              <>
                                <div style={{
                                  width: '12px',
                                  height: '12px',
                                  border: '2px solid #ef4444',
                                  borderTop: '2px solid transparent',
                                  borderRadius: '50%',
                                  animation: 'spin 1s linear infinite'
                                }} />
                                删除中...
                              </>
                            ) : (
                              <>
                                <X size={12} />
                                撤回
                              </>
                            )}
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </MessageWrapper>
              </MessageBubble>
            ))
          )}
        </AnimatePresence>

        {isLoading && (
          <LoadingIndicator
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Loader2 size={16} className="spinner" />
            <span>正在思考中</span>
            <span className="dots">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          </LoadingIndicator>
        )}

        {suggestions.length > 0 && (
          <Suggestions>
            <AnimatePresence>
              {suggestions.map((suggestion, index) => (
                <SuggestionChip
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onSuggestionClick(suggestion)}
                >
                  {suggestion}
                </SuggestionChip>
              ))}
            </AnimatePresence>
          </Suggestions>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        {/* URL预览 */}
        {detectedURLs.length > 0 && (
          <URLPreview
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Link size={14} />
            <URLText>{detectedURLs[0]}</URLText>
            <URLButton onClick={() => window.open(detectedURLs[0], '_blank')}>
              <ExternalLink size={14} />
            </URLButton>
          </URLPreview>
        )}

        {/* 附件预览 */}
        {attachments.length > 0 && (
          <AttachmentsPreview>
            <AnimatePresence>
              {attachments.map((attachment) => (
                <AttachmentItem
                  key={attachment.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                >
                  <AttachmentIcon>
                    {getFileIcon(attachment.type)}
                  </AttachmentIcon>
                  <span>{attachment.name}</span>
                  <span style={{ color: '#999' }}>({formatFileSize(attachment.size)})</span>
                  <RemoveAttachmentButton
                    onClick={() => onRemoveAttachment(attachment.id)}
                  >
                    <X size={12} />
                  </RemoveAttachmentButton>
                </AttachmentItem>
              ))}
            </AnimatePresence>
          </AttachmentsPreview>
        )}

        <InputWrapper>
          <InputBox>
            <MessageInput
              ref={inputRef}
              value={inputValue}
              onChange={onInputChange}
              onKeyDown={handleKeyDown}
              placeholder="发消息或输入 / 选择技能"
              disabled={isLoading}
              rows={1}
            />
            <InputActions>
              <LeftActions>
                <AttachmentButton
                  ref={attachmentButtonRef}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="添加附件"
                >
                  <Paperclip size={18} />
                </AttachmentButton>
                <FeatureButton
                  active={deepThinkActive}
                  onClick={() => onDeepThinkChange && onDeepThinkChange(!deepThinkActive)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Sparkles size={14} />
                  深度思考
                </FeatureButton>
              </LeftActions>
              <RightActions>
                <AttachmentButton
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="语音输入"
                >
                  <Mic size={18} />
                </AttachmentButton>
                <SendButton
                  ref={sendButtonRef}
                  onClick={onSendMessage}
                  disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="发送消息"
                >
                  <Send size={16} />
                </SendButton>
              </RightActions>
            </InputActions>
          </InputBox>

        </InputWrapper>

        <FileInput
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,application/pdf,.doc,.docx,.txt"
          onChange={onFileUpload}
        />
      </InputContainer>
    </ChatContainerStyled>
  );
};

export default ChatContainer;

