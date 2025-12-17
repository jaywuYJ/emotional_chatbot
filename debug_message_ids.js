// 调试消息ID匹配问题的脚本
// 在浏览器控制台中运行

function debugMessageIds() {
    console.log('=== 调试消息ID匹配问题 ===');
    
    // 模拟当前消息列表
    const messages = [
        {
            id: 'history_test_session_123_107_2025-12-17T09:55:24',
            role: 'user',
            content: '今天天气怎么样？',
            dbId: 107,
            user_id: 'test_user',
            isHistory: true
        },
        {
            id: 'history_test_session_123_108_2025-12-17T09:55:25',
            role: 'assistant',
            content: '你在哪里呢？可以告诉我你所在的城市吗？',
            dbId: 108,
            user_id: 'test_user',
            isHistory: true
        },
        {
            id: 'history_test_session_123_109_2025-12-17T09:55:26',
            role: 'user',
            content: '那明天呢？',
            dbId: 109,
            user_id: 'test_user',
            isHistory: true
        },
        {
            id: 'history_test_session_123_110_2025-12-17T09:55:27',
            role: 'assistant',
            content: '你提到"明天"，是想了解明天的天气...',
            dbId: 110,
            user_id: 'test_user',
            isHistory: true
        }
    ];
    
    console.log('当前消息列表:', messages);
    
    // 模拟编辑第一条消息
    const messageToEdit = messages[0];
    console.log('要编辑的消息:', messageToEdit);
    console.log('消息ID:', messageToEdit.id);
    console.log('数据库ID:', messageToEdit.dbId);
    
    // 模拟编辑响应
    const editResponse = {
        message: "消息编辑成功，已重新生成对话",
        message_id: 107,
        content: "今天北京的天气如何？",
        updated_at: "2025-12-17T09:55:24",
        new_response: {
            content: "你好呀～虽然你问的是北京的天气...",
            emotion: "neutral",
            suggestions: [],
            context: {}
        },
        deleted_messages_count: 3,
        regenerated: true
    };
    
    console.log('编辑响应:', editResponse);
    
    // 模拟前端更新逻辑
    const updatedMessage = {
        id: messageToEdit.id,
        content: editResponse.content,
        regenerated: true,
        newResponse: editResponse.new_response,
        deletedCount: editResponse.deleted_messages_count
    };
    
    console.log('传递给handleMessageUpdate的数据:', updatedMessage);
    
    // 模拟handleMessageUpdate逻辑
    if (updatedMessage.regenerated && updatedMessage.newResponse) {
        console.log('检测到重新生成，开始处理...');
        
        // 找到被编辑消息的索引
        const editedMessageIndex = messages.findIndex(msg => msg.id === updatedMessage.id);
        console.log('被编辑消息索引:', editedMessageIndex);
        
        if (editedMessageIndex === -1) {
            console.error('❌ 未找到被编辑的消息！');
            console.log('查找的ID:', updatedMessage.id);
            console.log('消息列表中的ID:');
            messages.forEach((msg, index) => {
                console.log(`  ${index}: ${msg.id}`);
            });
            return;
        }
        
        console.log('✅ 找到被编辑的消息');
        
        // 创建新的消息列表
        const messagesBeforeEdit = messages.slice(0, editedMessageIndex);
        const editedMessage = messages[editedMessageIndex];
        
        const updatedEditedMessage = {
            ...editedMessage,
            content: updatedMessage.content,
            timestamp: new Date().toISOString()
        };
        
        const newAIMessage = {
            id: `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            role: 'assistant',
            content: updatedMessage.newResponse.content,
            emotion: updatedMessage.newResponse.emotion || 'neutral',
            suggestions: updatedMessage.newResponse.suggestions || [],
            timestamp: new Date().toISOString(),
            user_id: 'test_user',
            context: updatedMessage.newResponse.context || {}
        };
        
        const newMessages = [
            ...messagesBeforeEdit,
            updatedEditedMessage,
            newAIMessage
        ];
        
        console.log('✅ 更新成功');
        console.log('原始消息数量:', messages.length);
        console.log('更新后消息数量:', newMessages.length);
        console.log('删除的消息数量:', messages.length - newMessages.length + 1); // +1 因为添加了新的AI回复
        console.log('新的消息列表:', newMessages);
        
    } else {
        console.log('简单内容更新');
    }
}

// 运行调试
debugMessageIds();