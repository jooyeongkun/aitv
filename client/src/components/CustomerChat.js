import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import axios from 'axios';

const CustomerChat = () => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
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
      // 기본값 설정
      setPackages([
        { name: '래프팅', type: '투어' },
        { name: '베이직 골프투어 72홀', type: '투어' },
        { name: '베스트팩', type: '투어' }
      ]);
    }
  };

  useEffect(() => {
    // 패키지 목록 가져오기
    fetchPackages();

    // 소켓 연결 (polling만 사용)
    const newSocket = io(process.env.REACT_APP_SOCKET_URL, {
      transports: ['polling']
    });
    setSocket(newSocket);

    // 소켓 이벤트 리스너
    newSocket.on('connect', () => {
      setIsConnected(true);
    });

    newSocket.on('chat-started', (data) => {
      setConversationId(data.conversationId);
      // 새 채팅 시작 시 이전 메시지 클리어
      setMessages([]);
    });

    newSocket.on('new-message', (message) => {
      // AI 응답이 도착하면 타이핑 상태 해제
      if (message.sender_type === 'ai') {
        setIsAiTyping(false);
      }
      
      // 자신이 보낸 메시지가 아니거나 임시 메시지가 아닌 경우만 추가
      setMessages(prev => {
        // 임시 메시지와 같은 내용이면 교체, 다르면 추가
        const hasTempMessage = prev.some(msg => 
          msg.id && typeof msg.id === 'string' && msg.id.startsWith('temp-') && 
          msg.message_text === message.message_text
        );
        
        if (hasTempMessage) {
          // 임시 메시지를 실제 메시지로 교체
          return prev.map(msg => 
            msg.id && typeof msg.id === 'string' && msg.id.startsWith('temp-') && msg.message_text === message.message_text 
              ? message 
              : msg
          );
        } else {
          // 새 메시지 추가
          return [...prev, message];
        }
      });
    });

    newSocket.on('error', (error) => {
      alert(error.message);
    });

    return () => newSocket.close();
  }, []);

  useEffect(() => {
    // 메시지 리스트 맨 아래로 스크롤
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startChatIfNeeded = () => {
    if (!conversationId && socket && isConnected) {
      const sessionId = getSessionId();
      socket.emit('start-chat', { sessionId });
    }
  };


  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const messageToSend = inputMessage;
    setInputMessage('');

    console.log('🔵 [Customer] Sending message:', messageToSend);
    console.log('🔵 [Customer] Current conversationId:', conversationId);
    console.log('🔵 [Customer] Socket connected:', socket?.connected);

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

    // 채팅방이 없으면 생성
    if (!conversationId) {
      const sessionId = getSessionId();
      console.log('🔵 [Customer] Creating new chat with session:', sessionId);
      
      socket.emit('start-chat', { sessionId });
      
      // 채팅방 생성 완료를 기다린 후 메시지 전송
      socket.once('chat-started', (data) => {
        console.log('🟢 [Customer] Chat started with ID:', data.conversationId);
        setConversationId(data.conversationId);
        
        socket.emit('send-message', {
          conversationId: data.conversationId,
          message: messageToSend,
          senderType: 'customer'
        });
        console.log('🟢 [Customer] Message sent to new conversation');
      });
    } else {
      // 기존 채팅방에 메시지 전송
      socket.emit('send-message', {
        conversationId,
        message: messageToSend,
        senderType: 'customer'
      });
      console.log('🟢 [Customer] Message sent to existing conversation');
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

      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#888', padding: '1rem' }}>
            {/* 패키지 목록 표시 */}
            <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.9em', fontWeight: 'bold', color: '#495057', marginBottom: '0.5rem' }}>
                🎯 현재 이용 가능한 패키지
              </div>
              {packages.length > 0 ? (
                packages.map((pkg, index) => (
                  <div key={index} style={{
                    fontSize: '0.85em',
                    color: '#6c757d',
                    padding: '2px 0',
                    textAlign: 'left'
                  }}>
                    • {pkg.name}
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '0.8em', color: '#adb5bd' }}>
                  패키지 정보를 불러오는 중...
                </div>
              )}
            </div>
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