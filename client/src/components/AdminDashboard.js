import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import axios from 'axios';

const AdminDashboard = () => {
  const [socket, setSocket] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [adminInfo, setAdminInfo] = useState(null);
  const [monthlyCount, setMonthlyCount] = useState(0);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    // 로그인 확인
    const token = localStorage.getItem('admin-token');
    const savedAdminInfo = localStorage.getItem('admin-info');
    
    if (!token || !savedAdminInfo) {
      navigate('/admin');
      return;
    }

    setAdminInfo(JSON.parse(savedAdminInfo));

    // JWT 토큰 임시 제거로 테스트
    // axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    console.log('Token set:', token.substring(0, 20) + '...');

    // 소켓 연결
    const newSocket = io(process.env.REACT_APP_SOCKET_URL);
    setSocket(newSocket);

    // 대화 목록 가져오기
    fetchConversations();

    // 소켓 이벤트 리스너
    newSocket.on('new-chat', (conversation) => {
      console.log('New chat received:', conversation);
      setConversations(prev => [conversation, ...prev]);
    });

    newSocket.on('new-message', (message) => {
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('conversation-updated', (conversationId) => {
      // 대화 목록 새로고침
      fetchConversations();
    });

    return () => newSocket.close();
  }, [navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchConversations = async () => {
    try {
      console.log('Fetching conversations...');
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/conversations`);
      console.log('Conversations received:', response.data);
      setConversations(response.data);
      
      // 이번달 상담 갯수 계산
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      const monthlyConversations = response.data.filter(conv => {
        const convDate = new Date(conv.created_at);
        return convDate.getMonth() === currentMonth && convDate.getFullYear() === currentYear;
      });
      setMonthlyCount(monthlyConversations.length);
    } catch (error) {
      console.error('대화 목록 가져오기 실패:', error);
    }
  };

  const selectConversation = async (conversation) => {
    setSelectedConversation(conversation);
    
    try {
      // 대화방 입장
      socket.emit('join-conversation', {
        conversationId: conversation.id,
        adminId: adminInfo.id
      });

      // 메시지 가져오기
      console.log('Fetching messages for conversation:', conversation.id);
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/conversations/${conversation.id}/messages`);
      console.log('Messages received:', response.data);
      setMessages(response.data);
    } catch (error) {
      console.error('메시지 가져오기 실패:', error);
    }
  };

  const sendMessage = () => {
    if (!inputMessage.trim() || !selectedConversation) return;

    socket.emit('send-message', {
      conversationId: selectedConversation.id,
      message: inputMessage,
      senderType: 'admin',
      senderId: adminInfo.id
    });

    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const logout = () => {
    localStorage.removeItem('admin-token');
    localStorage.removeItem('admin-info');
    navigate('/admin');
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="admin-dashboard">
      {/* 좌측 네비게이션 */}
      <div className="admin-sidebar">
        <div className="nav-tabs">
          <div className="nav-tab active">채팅</div>
          <div className="nav-tab" onClick={() => navigate('/admin/statistics')}>통계</div>
          <div className="nav-tab" onClick={() => navigate('/admin/hotels')}>호텔</div>
          <div className="nav-tab">투어</div>
          <div className="nav-tab">렌트카</div>
          <div className="nav-tab">티켓</div>
          <div className="nav-tab">기타</div>
        </div>
      </div>
      
      {/* 채팅 리스트 */}
      <div className="chat-list">
        <div className="chat-list-header">
          <p>{adminInfo?.name}님</p>
          <button 
            onClick={logout}
            style={{
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: 'white',
              padding: '5px 10px',
              borderRadius: '3px',
              marginTop: '10px',
              cursor: 'pointer'
            }}
          >
            로그아웃
          </button>
        </div>

        <div style={{ overflow: 'auto', flex: 1 }}>
          {conversations.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
              대기 중인 채팅이 없습니다.
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`chat-item ${selectedConversation?.id === conv.id ? 'active' : ''}`}
                onClick={() => selectConversation(conv)}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {conv.customer_name}
                </div>
                <div style={{ fontSize: '0.9em', color: '#666' }}>
                  상태: {conv.status === 'waiting' ? '대기중' : conv.status === 'active' ? '상담중' : '종료'}
                </div>
                <div style={{ fontSize: '0.8em', color: '#888', marginTop: '5px' }}>
                  {formatTime(conv.updated_at)}
                </div>
                {conv.message_count > 0 && (
                  <div style={{ fontSize: '0.8em', color: '#4CAF50' }}>
                    메시지 {conv.message_count}개
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* 우측 채팅 상세 */}
      <div className="chat-detail">
        {selectedConversation ? (
          <>
            <div className="chat-detail-header">
              <h4>{selectedConversation.customer_name}</h4>
              <p>세션 ID: {selectedConversation.session_id}</p>
            </div>

            <div className="admin-messages">
              {messages.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#888', padding: '2rem' }}>
                  아직 메시지가 없습니다.
                </div>
              ) : (
                messages.map((msg) => (
                  <div 
                    key={msg.id} 
                    className={`message ${msg.sender_type === 'ai' ? 'admin' : msg.sender_type}`}
                  >
                    <div style={{ fontSize: '0.8em', opacity: 0.7, marginBottom: '3px' }}>
                      {msg.sender_type === 'admin' ? (msg.admin_name || '관리자') : 
                       msg.sender_type === 'ai' ? 'AI 상담사' : '고객'}
                    </div>
                    {msg.message_text}
                    <div style={{ 
                      fontSize: '0.7em', 
                      opacity: 0.7, 
                      marginTop: '5px' 
                    }}>
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="admin-input">
              <input
                type="text"
                placeholder="메시지를 입력하세요..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <button onClick={sendMessage}>전송</button>
            </div>
          </>
        ) : (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            color: '#888'
          }}>
            좌측에서 채팅을 선택해주세요.
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;