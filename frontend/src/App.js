import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AppContainer } from './styles';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import FeedbackModal from './components/FeedbackModal';
import PersonalizationPanel from './components/PersonalizationPanel';
import HistoryManagementModal from './components/HistoryManagementModal';
import { useTheme } from './contexts/ThemeContext';
import { useChat, useFileUpload, useKeyboard, useSession, useFeedback, useURLDetection } from './hooks';

function App() {
  // 用户ID管理
  const [currentUserId] = useState(() => {
    const savedUserId = localStorage.getItem('emotional_chat_user_id');
    if (savedUserId) {
      return savedUserId;
    }
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    localStorage.setItem('emotional_chat_user_id', newUserId);
    return newUserId;
  });

  // UI状态
  const [inputValue, setInputValue] = useState('');
  const [showPersonalizationPanel, setShowPersonalizationPanel] = useState(false);
  const [showHistoryManagement, setShowHistoryManagement] = useState(false);
  const [deepThinkActive, setDeepThinkActive] = useState(false);
  const [forceUpdateKey, setForceUpdateKey] = useState(0);
  
  // 主题管理
  const { theme, toggleTheme } = useTheme();

  // Refs
  const inputRef = useRef(null);
  const attachmentButtonRef = useRef(null);
  const sendButtonRef = useRef(null);

  // 自定义Hooks
  const {
    sessionId: sessionIdFromHook,
    setSessionId: setSessionIdFromHook,
    historySessions,
    loadHistorySessions,
    loadSessionHistory,
    deleteConversation: deleteConversationHook,
    startNewChat: startNewChatHook
  } = useSession(currentUserId);

  const chatHook = useChat(currentUserId);
  const {
    messages,
    setMessages,
    isLoading,
    sessionId: chatSessionId,
    setSessionId: setChatSessionId,
    suggestions,
    setSuggestions,
    messagesEndRef,
    scrollToBottom,
    sendMessage: sendMessageHook
  } = chatHook;

  const {
    attachments,
    setAttachments,
    fileInputRef,
    handleFileUpload,
    removeAttachment
  } = useFileUpload();

  const {
    detectedURLs,
    setDetectedURLs,
    debouncedDetectURLs
  } = useURLDetection();

  const {
    showFeedbackModal,
    feedbackType,
    feedbackRating,
    feedbackComment,
    openFeedbackModal,
    closeFeedbackModal,
    setFeedbackType,
    setFeedbackRating,
    setFeedbackComment,
    submitFeedback
  } = useFeedback(sessionIdFromHook || chatSessionId, currentUserId, messages);

  // 使用统一的sessionId
  const sessionId = sessionIdFromHook || chatSessionId;
  const setSessionId = useCallback((id) => {
    setSessionIdFromHook(id);
    setChatSessionId(id);
  }, [setSessionIdFromHook, setChatSessionId]);

  // 发送消息
  const sendMessage = useCallback(async () => {
    await sendMessageHook(inputValue, attachments, setInputValue, setAttachments, setDetectedURLs, deepThinkActive);
    // 只有在发送新消息时才刷新历史会话列表（创建新会话或更新现有会话）
    loadHistorySessions();
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [inputValue, attachments, sendMessageHook, setInputValue, setAttachments, setDetectedURLs, loadHistorySessions, deepThinkActive]);

  // 新建对话
  const startNewChat = useCallback(() => {
    startNewChatHook(setMessages, setSessionId, setSuggestions, setAttachments, setDetectedURLs);
    setDeepThinkActive(false); // 重置深度思考状态
  }, [startNewChatHook, setSessionId, setMessages, setSuggestions, setAttachments, setDetectedURLs]);

  // 加载会话历史
  const handleLoadSession = useCallback((targetSessionId) => {
    loadSessionHistory(targetSessionId, setMessages, setSuggestions);
  }, [loadSessionHistory, setMessages, setSuggestions]);

  // 删除对话
  const handleDeleteSession = useCallback((targetSessionId, event) => {
    deleteConversationHook(targetSessionId, sessionId, setMessages, setSessionId, setSuggestions);
  }, [deleteConversationHook, sessionId, setSessionId, setMessages, setSuggestions]);

  // 处理历史消息管理中的会话选择
  const handleHistorySessionSelect = useCallback((targetSessionId) => {
    loadSessionHistory(targetSessionId, setMessages, setSuggestions);
    setSessionId(targetSessionId);
  }, [loadSessionHistory, setMessages, setSuggestions, setSessionId]);

  // 处理批量删除后的回调
  const handleSessionsDeleted = useCallback((deletedSessionIds) => {
    // 如果当前会话被删除，清空消息
    if (deletedSessionIds.includes(sessionId)) {
      setMessages([]);
      setSessionId(null);
      setSuggestions([]);
    }
    // 刷新历史会话列表
    loadHistorySessions();
  }, [sessionId, setMessages, setSessionId, setSuggestions, loadHistorySessions]);

  // 键盘处理
  const { handleKeyPress, handleTabNavigation } = useKeyboard(
    startNewChat,
    sendMessage,
    inputRef,
    attachmentButtonRef,
    sendButtonRef
  );

  // 输入处理
  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    setInputValue(value);
    debouncedDetectURLs(value);
  }, [debouncedDetectURLs, setInputValue]);

  // 消息更新处理
  const handleMessageUpdate = useCallback((updatedMessage) => {
    console.log('handleMessageUpdate 被调用:', updatedMessage);
    
    if (updatedMessage.regenerated && updatedMessage.newResponse) {
      console.log('处理编辑消息并重新生成AI回复的情况');
      // 编辑消息并重新生成AI回复的情况
      setMessages(prevMessages => {
        console.log('当前消息列表:', prevMessages);
        
        // 找到被编辑消息的索引
        const editedMessageIndex = prevMessages.findIndex(msg => msg.id === updatedMessage.id);
        console.log('被编辑消息索引:', editedMessageIndex);
        
        if (editedMessageIndex === -1) {
          console.log('未找到被编辑的消息');
          return prevMessages;
        }
        
        // 获取被编辑消息的时间戳（用于确定删除范围）
        const editedMessage = prevMessages[editedMessageIndex];
        const editedTimestamp = editedMessage.timestamp;
        
        console.log('被编辑的消息:', editedMessage);
        
        // 创建新的消息列表：
        // 1. 保留编辑消息之前的所有消息
        // 2. 更新编辑的消息内容
        // 3. 删除编辑消息之后的所有消息
        // 4. 添加新的AI回复
        const messagesBeforeEdit = prevMessages.slice(0, editedMessageIndex);
        const updatedEditedMessage = {
          ...editedMessage,
          content: updatedMessage.content,
          timestamp: new Date().toISOString()
        };
        
        // 创建新的AI回复消息
        const newAIMessage = {
          id: updatedMessage.newResponse.ai_message_id || `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: updatedMessage.newResponse.content,
          emotion: updatedMessage.newResponse.emotion || 'neutral',
          suggestions: updatedMessage.newResponse.suggestions || [],
          timestamp: new Date().toISOString(),
          dbId: updatedMessage.newResponse.ai_message_id,  // 设置数据库ID
          user_id: currentUserId,
          context: updatedMessage.newResponse.context || {}
        };
        
        console.log(`消息编辑：删除了 ${updatedMessage.deletedCount || 0} 条后续消息，重新生成AI回复`);
        console.log('新的AI消息:', newAIMessage);
        
        const newMessages = [
          ...messagesBeforeEdit,
          updatedEditedMessage,
          newAIMessage
        ];
        
        console.log('更新后的消息列表:', newMessages);
        
        // 强制触发重新渲染
        setTimeout(() => {
          console.log('强制滚动到底部');
          setForceUpdateKey(prev => prev + 1);
          if (messagesEndRef && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 200);
        
        return newMessages;
      });
    } else {
      console.log('处理简单的消息内容更新');
      // 简单的消息内容更新
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === updatedMessage.id 
            ? { ...msg, content: updatedMessage.content } 
            : msg
        )
      );
    }
  }, [setMessages, currentUserId]);

  // 消息删除处理
  const handleMessageDelete = useCallback((deleteInfo) => {
    console.log('🗑️ handleMessageDelete 被调用:', deleteInfo);
    
    // 兼容旧的调用方式（直接传递messageId）
    if (typeof deleteInfo === 'string') {
      console.log('使用旧的删除方式，直接删除消息ID:', deleteInfo);
      setMessages(prevMessages => prevMessages.filter(msg => msg.id !== deleteInfo));
      return;
    }
    
    // 新的调用方式（传递删除信息对象）
    const { messageId, deletedCount, deletedMessages, result } = deleteInfo;
    console.log('🔍 删除信息详情:', {
      messageId,
      deletedCount,
      deletedMessages,
      result
    });
    
    setMessages(prevMessages => {
      console.log('📊 删除前消息状态:');
      console.log(`  总消息数: ${prevMessages.length}`);
      prevMessages.forEach((msg, index) => {
        console.log(`  ${index + 1}. ID: ${msg.id}, dbId: ${msg.dbId}, 角色: ${msg.role}, 内容: ${msg.content.substring(0, 30)}...`);
      });
      
      // 如果后端返回了具体删除的消息ID列表，使用它们
      if (deletedMessages && deletedMessages.length > 0) {
        console.log('🎯 使用后端返回的删除ID列表:', deletedMessages);
        
        const newMessages = prevMessages.filter(msg => {
          // 检查消息的数据库ID是否在删除列表中
          const dbId = msg.dbId || msg.id;
          const shouldDelete = deletedMessages.includes(parseInt(dbId)) || 
                              deletedMessages.includes(String(dbId)) ||
                              deletedMessages.includes(dbId);
          
          if (shouldDelete) {
            console.log(`❌ 删除消息: ${msg.id} (dbId: ${dbId}), 角色: ${msg.role}`);
          } else {
            console.log(`✅ 保留消息: ${msg.id} (dbId: ${dbId}), 角色: ${msg.role}`);
          }
          return !shouldDelete;
        });
        
        console.log('📊 删除后消息状态:');
        console.log(`  删除前: ${prevMessages.length} 条`);
        console.log(`  删除后: ${newMessages.length} 条`);
        console.log(`  实际删除: ${prevMessages.length - newMessages.length} 条`);
        
        // 强制触发重新渲染和状态同步
        setTimeout(() => {
          console.log('🔄 强制触发重新渲染');
          setForceUpdateKey(prev => prev + 1);
          
          // 确保滚动到底部
          if (messagesEndRef && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
        
        // 额外的强制更新，确保UI同步
        setTimeout(() => {
          console.log('🔄 额外的强制更新');
          setForceUpdateKey(prev => prev + 1);
          
          // 重新加载当前会话历史以确保数据同步
          if (sessionId && loadSessionHistory) {
            console.log('🔄 重新加载会话历史以确保同步');
            loadSessionHistory(sessionId, setMessages, setSuggestions);
          }
        }, 500);
        
        // 检查删除后的会话状态
        if (newMessages.length === 0) {
          console.log('🗑️ 会话已清空，重置会话状态');
          // 如果所有消息都被删除了，重置会话状态
          setTimeout(() => {
            setSessionId(null);
            setSuggestions([]);
          }, 200);
        }
        
        return newMessages;
      } else {
        console.log('⚠️ 后端未返回删除ID列表，使用回退方案');
        // 回退到只删除指定的消息
        const newMessages = prevMessages.filter(msg => msg.id !== messageId);
        console.log(`回退删除: ${prevMessages.length} -> ${newMessages.length}`);
        
        // 检查删除后的会话状态
        if (newMessages.length === 0) {
          console.log('🗑️ 会话已清空（回退方案），重置会话状态');
          setTimeout(() => {
            setSessionId(null);
            setSuggestions([]);
          }, 200);
        }
        
        // 回退方案也需要强制更新
        setTimeout(() => {
          console.log('🔄 回退方案强制更新');
          setForceUpdateKey(prev => prev + 1);
          
          if (sessionId && loadSessionHistory) {
            console.log('🔄 回退方案重新加载会话历史');
            loadSessionHistory(sessionId, setMessages, setSuggestions);
          }
        }, 500);
        
        return newMessages;
      }
    });
  }, [setMessages, setForceUpdateKey, setSessionId, setSuggestions, sessionId, loadSessionHistory]);

  // 快捷建议点击
  const handleSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  }, []);

  // 自动滚动
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 应用主题到body
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <AppContainer>
      <Sidebar
        currentUserId={currentUserId}
        sessionId={sessionId}
        historySessions={historySessions}
        onNewChat={startNewChat}
        onLoadSession={handleLoadSession}
        onDeleteSession={handleDeleteSession}
        onOpenPersonalization={() => setShowPersonalizationPanel(true)}
        onToggleTheme={toggleTheme}
        theme={theme}
        onOpenHistoryManagement={() => setShowHistoryManagement(true)}
      />

      <ChatContainer
        key={forceUpdateKey}
        messages={messages}
        isLoading={isLoading}
        suggestions={suggestions}
        inputValue={inputValue}
        attachments={attachments}
        detectedURLs={detectedURLs}
        messagesEndRef={messagesEndRef}
        inputRef={inputRef}
        attachmentButtonRef={attachmentButtonRef}
        sendButtonRef={sendButtonRef}
        fileInputRef={fileInputRef}
        onInputChange={handleInputChange}
        onKeyPress={handleKeyPress}
        onTabNavigation={handleTabNavigation}
        onSendMessage={sendMessage}
        onFileUpload={handleFileUpload}
        onRemoveAttachment={removeAttachment}
        onSuggestionClick={handleSuggestionClick}
        onOpenFeedbackModal={openFeedbackModal}
        deepThinkActive={deepThinkActive}
        onDeepThinkChange={setDeepThinkActive}
        onMessageUpdate={handleMessageUpdate}
        onMessageDelete={handleMessageDelete}
      />

      <PersonalizationPanel
        isOpen={showPersonalizationPanel}
        onClose={() => setShowPersonalizationPanel(false)}
        userId={currentUserId}
      />

      <FeedbackModal
        show={showFeedbackModal}
        feedbackType={feedbackType}
        feedbackRating={feedbackRating}
        feedbackComment={feedbackComment}
        onClose={closeFeedbackModal}
        onTypeChange={setFeedbackType}
        onRatingChange={setFeedbackRating}
        onCommentChange={setFeedbackComment}
        onSubmit={submitFeedback}
      />

      <HistoryManagementModal
        show={showHistoryManagement}
        onClose={() => setShowHistoryManagement(false)}
        userId={currentUserId}
        onSessionSelect={handleHistorySessionSelect}
        onSessionsDeleted={handleSessionsDeleted}
      />
    </AppContainer>
  );
}

export default App;
