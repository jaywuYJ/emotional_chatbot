// 实时删除调试工具
// 在浏览器控制台中运行此脚本来调试删除功能

window.debugDelete = {
  // 监听删除操作
  monitorDelete: function() {
    console.log('🔍 开始监听删除操作...');
    
    // 拦截fetch请求
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      const [url, options] = args;
      
      // 检查是否是删除请求
      if (url.includes('/chat/messages/') && options?.method === 'DELETE') {
        console.log('🗑️ 检测到删除请求:', {
          url,
          options,
          messageId: url.split('/').pop().split('?')[0]
        });
        
        return originalFetch.apply(this, args).then(response => {
          if (response.ok) {
            response.clone().json().then(result => {
              console.log('✅ 删除请求成功:', result);
              console.log('📋 删除的消息ID列表:', result.deleted_messages);
              
              // 检查当前页面的消息状态
              setTimeout(() => {
                this.checkCurrentMessages();
              }, 500);
            });
          } else {
            console.log('❌ 删除请求失败:', response.status, response.statusText);
          }
          return response;
        });
      }
      
      return originalFetch.apply(this, args);
    }.bind(this);
  },
  
  // 检查当前页面的消息
  checkCurrentMessages: function() {
    console.log('📊 检查当前页面消息状态...');
    
    // 查找消息容器
    const messageElements = document.querySelectorAll('[class*="MessageBubble"]');
    console.log(`页面上显示的消息数量: ${messageElements.length}`);
    
    messageElements.forEach((element, index) => {
      const isUser = element.textContent.includes('👤') || element.querySelector('[class*="user"]');
      const isAI = element.textContent.includes('🤖') || element.querySelector('[class*="assistant"]');
      const content = element.textContent.substring(0, 50);
      
      console.log(`  ${index + 1}. ${isUser ? '👤 用户' : isAI ? '🤖 AI' : '❓ 未知'}: ${content}...`);
    });
  },
  
  // 检查React状态
  checkReactState: function() {
    console.log('⚛️ 检查React状态...');
    
    // 尝试获取React DevTools信息
    const reactRoot = document.querySelector('#root');
    if (reactRoot && reactRoot._reactInternalFiber) {
      console.log('找到React根节点');
    } else {
      console.log('未找到React DevTools信息');
    }
    
    // 检查localStorage中的会话信息
    const currentSession = localStorage.getItem('emotional_chat_current_session');
    const userId = localStorage.getItem('emotional_chat_user_id');
    
    console.log('💾 本地存储信息:', {
      currentSession,
      userId
    });
  },
  
  // 模拟删除操作
  simulateDelete: async function(messageId, userId) {
    console.log(`🧪 模拟删除操作: messageId=${messageId}, userId=${userId}`);
    
    try {
      const response = await fetch(`/chat/messages/${messageId}?user_id=${userId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ 模拟删除成功:', result);
        return result;
      } else {
        console.log('❌ 模拟删除失败:', response.status, response.statusText);
        return null;
      }
    } catch (error) {
      console.log('❌ 模拟删除异常:', error);
      return null;
    }
  },
  
  // 检查消息ID匹配
  checkIdMatching: function(deletedIds) {
    console.log('🔍 检查消息ID匹配...');
    console.log('后端删除的ID列表:', deletedIds);
    
    // 检查页面上的消息元素
    const messageElements = document.querySelectorAll('[class*="MessageBubble"]');
    
    messageElements.forEach((element, index) => {
      // 尝试从元素中提取ID信息
      const textContent = element.textContent;
      const idMatch = textContent.match(/ID[:\s]*(\d+)/);
      const dbIdMatch = textContent.match(/dbId[:\s]*(\d+)/);
      
      if (idMatch || dbIdMatch) {
        const id = idMatch ? idMatch[1] : null;
        const dbId = dbIdMatch ? dbIdMatch[1] : null;
        
        const shouldBeDeleted = deletedIds.some(deletedId => 
          deletedId == id || deletedId == dbId
        );
        
        console.log(`  消息 ${index + 1}: ID=${id}, dbId=${dbId}, 应该被删除=${shouldBeDeleted}`);
        
        if (shouldBeDeleted) {
          console.log(`    ❌ 这条消息应该被删除但仍然显示`);
          element.style.border = '2px solid red';
          element.style.backgroundColor = '#ffebee';
        }
      }
    });
  },
  
  // 完整的调试流程
  fullDebug: function() {
    console.log('🚀 开始完整的删除调试流程...');
    
    this.monitorDelete();
    this.checkCurrentMessages();
    this.checkReactState();
    
    console.log('📝 调试工具已启动，现在可以执行删除操作');
    console.log('💡 可用命令:');
    console.log('  - debugDelete.checkCurrentMessages() - 检查当前消息');
    console.log('  - debugDelete.checkReactState() - 检查React状态');
    console.log('  - debugDelete.simulateDelete(messageId, userId) - 模拟删除');
    console.log('  - debugDelete.checkIdMatching([id1, id2]) - 检查ID匹配');
  }
};

// 自动启动调试
console.log('🔧 删除功能实时调试工具已加载');
console.log('运行 debugDelete.fullDebug() 开始调试');

// 导出到全局
window.debugDelete = debugDelete;