import { useState, useRef, useCallback } from 'react';
import ChatAPI from '../services/ChatAPI';
import { detectURLs } from '../utils/formatters';

export const useChat = (currentUserId) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const sendMessage = useCallback(async (inputValue, attachments, setInputValue, setAttachments, setDetectedURLs, deepThinking = false) => {
    if ((!inputValue.trim() && attachments.length === 0) || isLoading) return;

    const userMessage = inputValue.trim();
    const urls = detectURLs(userMessage);
    
    // 处理检测到的URL
    let urlContents = [];
    if (urls.length > 0) {
      for (const url of urls) {
        try {
          const urlContent = await ChatAPI.parseURL({ url });
          if (urlContent) {
            urlContents.push(urlContent);
          }
        } catch (error) {
          console.error('URL解析失败:', error);
        }
      }
    }

    setInputValue('');
    setIsLoading(true);

    // 添加用户消息
    const newUserMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      user_id: currentUserId,  // 添加user_id字段
      attachments: attachments.map(att => ({
        id: att.id,
        name: att.name,
        type: att.type,
        size: att.size
      })),
      urls: urlContents,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      // 准备FormData用于文件上传
      const formData = new FormData();
      formData.append('message', userMessage);
      formData.append('session_id', sessionId || '');
      formData.append('user_id', currentUserId);
      formData.append('deep_thinking', deepThinking ? 'true' : 'false'); // 添加深度思考参数
      
      // 添加URL内容
      if (urlContents.length > 0) {
        formData.append('url_contents', JSON.stringify(urlContents));
      }

      // 添加文件附件
      attachments.forEach((attachment, index) => {
        formData.append(`file_${index}`, attachment.file, attachment.name);
      });

      const response = await ChatAPI.sendMessageWithAttachments(formData);

      setSessionId(response.session_id);
      setSuggestions(response.suggestions || []);

      // 更新用户消息的ID为后端返回的真实ID，同时保存数据库ID
      setMessages(prev => prev.map(msg => 
        msg.id === newUserMessage.id 
          ? { 
              ...msg, 
              id: response.message_id,
              dbId: response.message_id,  // 保存数据库ID用于编辑和撤回
              user_id: currentUserId      // 确保user_id存在
            } 
          : msg
      ));

      // 添加机器人回复
      const botMessage = {
        id: response.ai_message_id || Date.now() + 1,  // 使用后端返回的AI消息ID
        role: 'assistant',
        content: response.response,
        emotion: response.emotion,
        timestamp: new Date(),
        dbId: response.ai_message_id,  // 设置数据库ID
        user_id: currentUserId  // 设置用户ID（AI消息也使用相同的用户ID）
      };
      
      console.log('🤖 创建AI消息:', {
        id: botMessage.id,
        dbId: botMessage.dbId,
        ai_message_id: response.ai_message_id,
        user_id: botMessage.user_id
      });
      
      setMessages(prev => [...prev, botMessage]);

      // 清空附件和URL
      setAttachments([]);
      setDetectedURLs([]);

    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 用户友好的错误提示
      let errorMsg = '抱歉，我现在无法回应。';
      if (error.response?.status === 500) {
        errorMsg += '服务器遇到了一些问题，请稍后再试。';
      } else if (error.message === 'Network Error') {
        errorMsg += '网络连接似乎有问题，请检查网络设置。';
      } else {
        errorMsg += '请稍后再试。';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
        dbId: null,  // 错误消息没有数据库ID
        user_id: currentUserId
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId, currentUserId]);

  return {
    messages,
    setMessages,
    isLoading,
    sessionId,
    setSessionId,
    suggestions,
    setSuggestions,
    messagesEndRef,
    scrollToBottom,
    sendMessage
  };
};

