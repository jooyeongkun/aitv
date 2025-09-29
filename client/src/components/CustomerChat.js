import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const CustomerChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [packages, setPackages] = useState([]);
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

  // 패키지 목록 가져오기 (투어만)
  const fetchPackages = async () => {
    try {
      const toursResponse = await axios.get(`${process.env.REACT_APP_API_URL}/tours`);

      const tourPackages = toursResponse.data.map(tour => ({
        name: tour.tour_name,
        type: '투어'
      }));

      setPackages(tourPackages);
    } catch (error) {
      console.error('패키지 목록 조회 실패:', error);
      // 서버 연결 실패시 빈 배열로 설정
      setPackages([]);
    }
  };

  useEffect(() => {
    // 패키지 목록 가져오기
    fetchPackages();

    // Socket.io 제거됨 - HTTP API만 사용
  }, []);

  useEffect(() => {
    // 메시지 리스트 맨 아래로 스크롤
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Socket.io 제거됨


  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const messageToSend = inputMessage;
    setInputMessage('');

    console.log('🔵 [Customer] Sending message via HTTP:', messageToSend);
    console.log('🔵 [Customer] Current conversationId:', conversationId);

    // AI 타이핑 상태 활성화
    setIsAiTyping(true);

    // 즉시 화면에 표시
    const tempMessage = {
      id: 'temp-' + Date.now(),
      message_text: messageToSend,
      sender_type: 'customer',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMessage]);

    try {
      let currentConversationId = conversationId;

      // 채팅방이 없으면 HTTP API로 생성
      if (!currentConversationId) {
        const sessionId = getSessionId();
        console.log('🔵 [Customer] Creating new chat via HTTP with session:', sessionId);

        const startResponse = await axios.post(`${process.env.REACT_APP_API_URL}/conversations/start`, {
          sessionId,
          customerName: null
        });

        currentConversationId = startResponse.data.conversationId;
        setConversationId(currentConversationId);
        console.log('🟢 [Customer] Chat started with ID:', currentConversationId);
      }

      // HTTP API로 메시지 전송
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/conversations/${currentConversationId}/messages`, {
        message: messageToSend,
        senderType: 'customer'
      });

      console.log('🟢 [Customer] HTTP Response:', response.data);

      // 임시 메시지 제거
      setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));

      // 서버에서 받은 실제 메시지들 추가
      if (response.data.customerMessage) {
        setMessages(prev => [...prev, response.data.customerMessage]);
      }

      // AI 응답이 있으면 추가
      if (response.data.aiMessage) {
        setIsAiTyping(false);
        setTimeout(() => {
          setMessages(prev => [...prev, response.data.aiMessage]);
        }, 500); // 자연스러운 AI 응답 딜레이
      } else {
        setIsAiTyping(false);
      }

    } catch (error) {
      console.error('HTTP 메시지 전송 실패:', error);
      setIsAiTyping(false);

      // 임시 메시지 제거
      setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));

      // 오류 메시지 표시
      const errorMessage = {
        id: Date.now(),
        message_text: '메시지 전송에 실패했습니다. 다시 시도해주세요.',
        sender_type: 'system',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  // 첫 메시지에서만 채팅방 생성하므로 자동 생성 제거

  // 임시로 연결 상태 체크 비활성화 - 항상 채팅창 표시
  // if (!isConnected) {
  //   return (
  //     <div className="customer-chat">
  //       <div className="chat-header">
  //         <h3>고객 상담 채팅</h3>
  //       </div>
  //       <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
  //         <h4>서버에 연결 중...</h4>
  //       </div>
  //     </div>
  //   );
  // }

  return (
    <div className="customer-chat">
      <div className="chat-header">
        <h3>세친구 투어</h3>
      </div>

      {/* 고정 투어 목록 표시 */}
      <div className="fixed-package-list" style={{
        position: 'sticky',
        top: 0,
        backgroundColor: '#f8f9fa',
        borderBottom: '1px solid #dee2e6',
        padding: '0.5rem 1rem',
        zIndex: 100,
        fontSize: '0.85em'
      }}>
        <div style={{
          fontWeight: 'bold',
          color: '#495057',
          marginBottom: '0.3rem',
          fontSize: '0.9em'
        }}>
          🎯 현재 이용 가능한 패키지
        </div>
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.5rem',
          color: '#6c757d'
        }}>
          {packages.length > 0 ? (
            packages.map((pkg, index) => (
              <span key={index} style={{
                backgroundColor: '#e9ecef',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '0.8em'
              }}>
                {pkg.name}
              </span>
            ))
          ) : (
            <span style={{ fontSize: '0.8em', color: '#adb5bd' }}>
              패키지 정보를 불러오는 중...
            </span>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#888', padding: '1rem' }}>
            <div style={{ fontSize: '0.9em' }}>
              궁금한 점을 남겨주시면 AI가 답변해드립니다.
            </div>
          </div>
        )}
        
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`message ${msg.sender_type === 'ai' ? 'admin' : msg.sender_type}`}
          >
            {msg.sender_type === 'ai' && (
              <div style={{ fontSize: '0.8em', opacity: 0.8, marginBottom: '3px', color: '#007bff' }}>
                🤖 AI 상담사
              </div>
            )}
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {msg.message_text}
            </div>
            <div style={{ 
              fontSize: '0.7em', 
              opacity: 0.7, 
              marginTop: '5px' 
            }}>
              {new Date(msg.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {isAiTyping && (
          <div className="message admin typing-message">
            <div style={{ fontSize: '0.8em', opacity: 0.8, marginBottom: '3px', color: '#007bff' }}>
              🤖 AI 상담사
            </div>
            <div className="typing-animation">
              AI가 답변 중입니다
              <span className="typing-dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Message..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="send-icon" onClick={sendMessage}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 12L22 2L13 21L11 13L2 12Z" fill="white"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default CustomerChat;