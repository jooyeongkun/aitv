import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const CustomerChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // 세션 ID 생성 (브라우저별 고유 식별자)
  const getSessionId = () => {
    let sessionId = sessionStorage.getItem('chat-session-id');
    if (!sessionId) {
      sessionId = 'chat-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('chat-session-id', sessionId);
    }
    return sessionId;
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // HTTP로 메시지 전송
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const messageText = inputMessage.trim();
    setInputMessage('');
    setIsAiTyping(true);

    try {
      console.log('🔵 [Customer] Sending message via HTTP:', messageText);
      console.log('🔵 [Customer] Current conversationId:', conversationId);

      let currentConversationId = conversationId;

      // 대화가 시작되지 않았으면 새로 시작
      if (!currentConversationId) {
        console.log('🔵 [Customer] Creating new chat via HTTP with session:', getSessionId());

        const startResponse = await axios.post(`${process.env.REACT_APP_API_URL}/conversations/start`, {
          sessionId: getSessionId(),
          customerName: null
        });

        currentConversationId = startResponse.data.conversationId;
        setConversationId(currentConversationId);
        console.log('🟢 [Customer] Chat started with ID:', currentConversationId);
      }

      // 메시지 전송
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/conversations/${currentConversationId}/messages`, {
        message: messageText,
        senderType: 'customer'
      });

      console.log('🟢 [Customer] HTTP Response:', response.data);

      // 고객 메시지 추가
      if (response.data.customerMessage) {
        setMessages(prev => [...prev, response.data.customerMessage]);
      }

      // AI 응답 추가
      if (response.data.aiMessage) {
        setIsAiTyping(false);
        setMessages(prev => [...prev, response.data.aiMessage]);
      } else {
        setIsAiTyping(false);
      }

    } catch (error) {
      console.error('❌ [Customer] Message send error:', error);
      setIsAiTyping(false);

      // 에러 메시지 표시
      setMessages(prev => [...prev, {
        id: 'error-' + Date.now(),
        message_text: '죄송합니다. 메시지 전송 중 오류가 발생했습니다.',
        sender_type: 'ai',
        created_at: new Date().toISOString()
      }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (text) => {
    return text.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < text.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* 헤더 */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '15px 20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>💬 여행 상담 채팅</h2>
        <p style={{ margin: '5px 0 0 0', fontSize: '12px', opacity: 0.9 }}>
          궁금한 것이 있으시면 언제든 물어보세요!
        </p>
      </div>

      {/* 메시지 영역 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        backgroundColor: '#f8f9fa'
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: '#666',
            marginTop: '50px'
          }}>
            <p>안녕하세요! 여행 상담을 도와드리겠습니다.</p>
            <p>궁금한 것이 있으시면 메시지를 보내주세요.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={message.id || index} style={{
            marginBottom: '15px',
            display: 'flex',
            justifyContent: message.sender_type === 'customer' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: message.sender_type === 'customer' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              backgroundColor: message.sender_type === 'customer' ? '#007bff' : '#e9ecef',
              color: message.sender_type === 'customer' ? 'white' : '#333',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              fontSize: '14px',
              lineHeight: '1.4'
            }}>
              {formatMessage(message.message_text)}
            </div>
          </div>
        ))}

        {isAiTyping && (
          <div style={{
            marginBottom: '15px',
            display: 'flex',
            justifyContent: 'flex-start'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '18px 18px 18px 4px',
              backgroundColor: '#e9ecef',
              color: '#666',
              fontSize: '14px'
            }}>
              AI가 답변 중입니다...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div style={{
        padding: '20px',
        backgroundColor: 'white',
        borderTop: '1px solid #dee2e6',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #ced4da',
              borderRadius: '25px',
              fontSize: '14px',
              resize: 'none',
              height: '20px',
              outline: 'none',
              fontFamily: 'inherit'
            }}
            rows="1"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isAiTyping}
            style={{
              padding: '12px 24px',
              backgroundColor: inputMessage.trim() && !isAiTyping ? '#007bff' : '#ced4da',
              color: 'white',
              border: 'none',
              borderRadius: '25px',
              cursor: inputMessage.trim() && !isAiTyping ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.2s'
            }}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomerChat;