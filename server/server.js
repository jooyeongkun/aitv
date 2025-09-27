require('dotenv').config();

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const db = require('./database');
const axios = require('axios');

// 환영 메시지 생성 함수
async function generateWelcomeMessage() {
  try {
    // 호텔과 투어 목록 조회
    const hotelsResult = await db.query(`
      SELECT hotel_name, hotel_region, adult_price
      FROM hotels WHERE is_active = true
      ORDER BY created_at DESC LIMIT 5
    `);

    const toursResult = await db.query(`
      SELECT tour_name
      FROM tours WHERE is_active = true
      ORDER BY created_at DESC LIMIT 5
    `);

    let message = "안녕하세요! 😊 여행 상담사입니다.\n\n현재 보유한 패키지는 다음과 같습니다:\n\n";

    // 호텔 목록 추가
    if (hotelsResult.rows && hotelsResult.rows.length > 0) {
      message += "🏨 **호텔 패키지:**\n";
      hotelsResult.rows.forEach(hotel => {
        const priceInfo = hotel.adult_price ? ` (${hotel.adult_price.toLocaleString()}원~)` : "";
        message += `• ${hotel.hotel_name} (${hotel.hotel_region})${priceInfo}\n`;
      });
      message += "\n";
    }

    // 투어 목록 추가
    if (toursResult.rows && toursResult.rows.length > 0) {
      message += "🎯 **투어 패키지:**\n";
      toursResult.rows.forEach(tour => {
        message += `• ${tour.tour_name}\n`;
      });
      message += "\n";
    }

    message += "이 외에도 호텔, 항공 등이 있습니다.\n무엇을 도와드릴까요?";
    return message;

  } catch (error) {
    console.error('환영 메시지 생성 오류:', error);
    return "안녕하세요! 😊 여행 상담사입니다. 무엇을 도와드릴까요?";
  }
}

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

console.log('🚀 Socket.IO server initialized');

app.use(cors());
app.use(express.json());

// 관리자 로그인
app.post('/api/admin/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    const result = await db.query('SELECT * FROM admin_users WHERE username = $1', [username]);
    if (result.rows.length === 0) {
      return res.status(401).json({ error: '아이디 또는 비밀번호가 틀렸습니다.' });
    }

    const admin = result.rows[0];
    const validPassword = await bcrypt.compare(password, admin.password);
    
    if (!validPassword) {
      return res.status(401).json({ error: '아이디 또는 비밀번호가 틀렸습니다.' });
    }

    const token = jwt.sign(
      { adminId: admin.id, username: admin.username },
      process.env.JWT_SECRET,
      { expiresIn: '8h' }
    );


    res.json({
      token,
      admin: {
        id: admin.id,
        username: admin.username,
        name: admin.name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: '서버 오류가 발생했습니다.' });
  }
});

// 대화 목록 조회
app.get('/api/conversations', async (req, res) => {
  try {
    console.log('API: Getting conversations...');
    // 임시로 단순한 쿼리 사용
    const result = await db.query(`
      SELECT id, session_id, admin_id, customer_name, status,
             created_at, updated_at
      FROM conversations
      ORDER BY updated_at DESC
    `);

    console.log('API: Conversations found:', result.rows);
    res.json(result.rows || []);
  } catch (error) {
    console.error('Get conversations error:', error);
    // 임시로 빈 배열 반환하여 프론트엔드가 로드되도록 함
    console.log('API: Returning empty array due to error');
    res.json([]);
  }
});

// 특정 대화의 메시지 조회
app.get('/api/conversations/:id/messages', async (req, res) => {
  try {
    const { id } = req.params;
    console.log('API: Getting messages for conversation:', id);
    
    const result = await db.query(`
      SELECT m.*, a.name as admin_name
      FROM messages m
      LEFT JOIN admin_users a ON m.sender_id = a.id AND m.sender_type = 'admin'
      WHERE m.conversation_id = $1
      ORDER BY m.created_at ASC
    `, [id]);
    
    console.log('API: Messages found:', result.rows);
    res.json(result.rows);
  } catch (error) {
    console.error('Get messages error:', error);
    res.status(500).json({ error: '서버 오류가 발생했습니다.' });
  }
});

// Socket.io 연결 처리
io.on('connection', (socket) => {
  console.log('🟢 User connected:', socket.id);

  // 고객 채팅 시작
  socket.on('start-chat', async (data) => {
    try {
      const { sessionId, customerName } = data;
      
      // 기존 대화 찾기 또는 새 대화 생성
      let result = await db.query('SELECT * FROM conversations WHERE session_id = $1', [sessionId]);
      
      let isNewChat = false;
      if (result.rows.length === 0) {
        result = await db.query(
          'INSERT INTO conversations (session_id, customer_name, status) VALUES ($1, $2, $3) RETURNING *',
          [sessionId, customerName || null, 'waiting']
        );
        isNewChat = true;
      }

      const conversation = result.rows[0];
      socket.join(`conversation_${conversation.id}`);

      socket.emit('chat-started', { conversationId: conversation.id });

      // 자동 환영 메시지 비활성화 (AI가 첫 응답에서 환영 메시지를 생성)
      // if (isNewChat) {
      //   const welcomeMessage = await generateWelcomeMessage();
      //   // 환영 메시지 생성 코드 비활성화
      // }

      // 모든 관리자에게 새 채팅 알림 (관리자만 받도록)
      socket.broadcast.emit('new-chat', conversation);

      console.log('New chat created:', conversation.id, 'Session:', conversation.session_id);
      
    } catch (error) {
      console.error('Start chat error:', error);
      socket.emit('error', { message: '채팅을 시작할 수 없습니다.' });
    }
  });

  // 메시지 전송
  socket.on('send-message', async (data) => {
    try {
      const { conversationId, message, senderType, senderId } = data;
      
      console.log('🔵 Message received:', { conversationId, message, senderType });
      
      // 메시지 DB 저장
      const result = await db.query(
        'INSERT INTO messages (conversation_id, sender_type, sender_id, message_text) VALUES ($1, $2, $3, $4) RETURNING *',
        [conversationId, senderType, senderId || null, message]
      );
      
      const newMessage = result.rows[0];
      
      // 대화방 업데이트 시간 갱신
      await db.query('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = $1', [conversationId]);
      
      console.log('Broadcasting message to conversation room:', `conversation_${conversationId}`);
      
      // 해당 대화방의 모든 사용자에게 메시지 전송
      io.to(`conversation_${conversationId}`).emit('new-message', newMessage);
      
      // 관리자에게도 새 메시지 알림 (대화 목록 업데이트용)
      socket.broadcast.emit('conversation-updated', conversationId);
      
      // 고객 메시지인 경우 AI 자동 응답 처리
      if (senderType === 'customer') {
        try {
          // AI 서비스에 요청
          const aiResponse = await axios.post('http://localhost:5002/chat', {
            message: message,
            conversation_id: conversationId
          }, {
            headers: {
              'Content-Type': 'application/json; charset=utf-8'
            }
          });
          
          if (aiResponse.data && aiResponse.data.response && aiResponse.data.response.trim().length > 0) {
            // AI 응답을 DB에 저장
            const aiMessageResult = await db.query(
              'INSERT INTO messages (conversation_id, sender_type, sender_id, message_text) VALUES ($1, $2, $3, $4) RETURNING *',
              [conversationId, 'ai', null, aiResponse.data.response]
            );

            const aiMessage = aiMessageResult.rows[0];

            // 대화방 업데이트 시간 갱신
            await db.query('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = $1', [conversationId]);

            // AI 응답을 대화방에 전송
            setTimeout(() => {
              io.to(`conversation_${conversationId}`).emit('new-message', aiMessage);
              socket.broadcast.emit('conversation-updated', conversationId);
            }, 1000); // 1초 딜레이로 자연스럽게

            console.log('AI response sent:', aiResponse.data.response);
          } else {
            // AI 응답이 유효하지 않을 때 고객에게 친근한 안내 메시지 전송
            let errorMessage = '죄송합니다. 잠시 후 다시 질문해 주시거나, 좀 더 구체적으로 질문해 주세요. 어떤 정보가 필요하신지 자세히 알려주시면 더 정확한 답변을 드릴 수 있습니다.';

            if (aiResponse.data && aiResponse.data.error_type) {
              if (aiResponse.data.error_type === 'need_more_info') {
                // AI가 안내하는 경우 그대로 사용
                errorMessage = aiResponse.data.response;
              } else {
                errorMessage = '죄송합니다. 질문을 이해하는 데 어려움이 있습니다. 좀 더 구체적으로 질문해 주시면 정확한 정보를 안내해드리겠습니다.';
              }
            } else if (aiResponse.data && !aiResponse.data.response) {
              errorMessage = '죄송합니다. 잠시 기술적인 문제가 있는 것 같습니다. 몇 초 후 다시 질문해 주세요.';
            } else if (aiResponse.data && aiResponse.data.response.trim().length === 0) {
              errorMessage = '죄송합니다. 다른 방식으로 질문해 주시면 더 정확한 답변을 드릴 수 있습니다.';
            }

            console.log('AI response invalid, sending error message:', errorMessage);

            // 오류 메시지를 DB에 저장
            const errorMessageResult = await db.query(
              'INSERT INTO messages (conversation_id, sender_type, sender_id, message_text) VALUES ($1, $2, $3, $4) RETURNING *',
              [conversationId, 'ai', null, errorMessage]
            );

            const errorMessageObj = errorMessageResult.rows[0];

            // 대화방 업데이트 시간 갱신
            await db.query('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = $1', [conversationId]);

            // 오류 메시지를 대화방에 전송
            setTimeout(() => {
              io.to(`conversation_${conversationId}`).emit('new-message', errorMessageObj);
              socket.broadcast.emit('conversation-updated', conversationId);
            }, 1000);
          }
        } catch (aiError) {
          console.error('AI service error:', aiError.message);
          // AI 서비스 오류 시에도 기본 메시지는 정상 전송되도록
        }
      }
      
    } catch (error) {
      console.error('Send message error:', error);
      socket.emit('error', { message: '메시지를 전송할 수 없습니다.' });
    }
  });

  // 관리자가 대화방 입장
  socket.on('join-conversation', async (data) => {
    try {
      const { conversationId, adminId } = data;
      
      socket.join(`conversation_${conversationId}`);
      
      // 대화방에 관리자 배정
      await db.query('UPDATE conversations SET admin_id = $1, status = $2 WHERE id = $3', 
        [adminId, 'active', conversationId]);
      
    } catch (error) {
      console.error('Join conversation error:', error);
      socket.emit('error', { message: '대화방에 입장할 수 없습니다.' });
    }
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

// 호텔 관리 API
// 호텔 목록 조회
app.get('/api/hotels', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT id, hotel_name, hotel_region, 
             TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
             TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
             is_unlimited, adult_price, child_price, child_criteria, description, is_active,
             created_at, updated_at
      FROM hotels WHERE is_active = true ORDER BY created_at DESC
    `);
    res.json(result.rows || result);
  } catch (error) {
    console.error('호텔 목록 조회 오류:', error);
    res.status(500).json({ error: '호텔 목록을 가져올 수 없습니다.' });
  }
});

// 새 호텔 생성
app.post('/api/hotels', async (req, res) => {
  try {
    console.log('호텔 생성 요청 받음:', req.body);
    const { hotel_name, hotel_region, promotion_start, promotion_end, is_unlimited, adult_price, child_price, child_criteria, description } = req.body;
    
    // 빈 문자열을 null이나 기본값으로 변환
    const adult_price_val = adult_price && adult_price !== '' ? parseInt(adult_price) : null;
    const child_price_val = child_price && child_price !== '' ? parseInt(child_price) : null;
    
    const result = await db.query(`
      INSERT INTO hotels (hotel_name, hotel_region, promotion_start, promotion_end, is_unlimited, adult_price, child_price, child_criteria, description)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      RETURNING id, hotel_name, hotel_region, 
                TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                is_unlimited, adult_price, child_price, child_criteria, description, is_active
    `, [
      hotel_name || '', 
      hotel_region || '', 
      promotion_start || new Date().toISOString().split('T')[0], 
      promotion_end || null, 
      is_unlimited || false, 
      adult_price_val, 
      child_price_val, 
      child_criteria || '', 
      description || ''
    ]);
    
    res.json(result.rows ? result.rows[0] : { id: result.lastID, ...req.body });
  } catch (error) {
    console.error('호텔 생성 오류:', error);
    res.status(500).json({ error: '호텔을 생성할 수 없습니다.' });
  }
});


// 호텔 정보 수정
app.put('/api/hotels/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    // 데이터 타입 변환
    const processedUpdates = {};
    Object.keys(updates).forEach(key => {
      let value = updates[key];
      if ((key === 'adult_price' || key === 'child_price') && value !== '' && value !== null) {
        value = parseInt(value);
      } else if ((key === 'adult_price' || key === 'child_price') && (value === '' || value === null)) {
        value = null;
      }
      processedUpdates[key] = value;
    });
    
    // 동적으로 업데이트 쿼리 생성
    const fields = Object.keys(processedUpdates);
    const values = Object.values(processedUpdates);
    const setClause = fields.map((field, index) => `${field} = $${index + 2}`).join(', ');
    
    const result = await db.query(`
      UPDATE hotels SET ${setClause}, updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING id, hotel_name, hotel_region, 
                TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                is_unlimited, adult_price, child_price, child_criteria, description, is_active
    `, [id, ...values]);
    
    res.json(result.rows ? result.rows[0] : { id, ...updates });
  } catch (error) {
    console.error('호텔 수정 오류:', error);
    res.status(500).json({ error: '호텔 정보를 수정할 수 없습니다.' });
  }
});

// 호텔 삭제
app.delete('/api/hotels/:id', async (req, res) => {
  try {
    const { id } = req.params;
    console.log(`호텔 삭제 요청 받음: ID ${id}`);
    
    // 완전 삭제
    const result = await db.query('DELETE FROM hotels WHERE id = $1', [id]);
    console.log(`삭제 결과:`, result.rowCount);
    
    res.json({ message: '호텔이 삭제되었습니다.', deletedRows: result.rowCount });
  } catch (error) {
    console.error('호텔 삭제 오류:', error);
    res.status(500).json({ error: '호텔을 삭제할 수 없습니다.' });
  }
});

// 투어 관리 API
// 투어 목록 조회
app.get('/api/tours', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT id, tour_name, tour_region, duration, description, is_active, display_order, created_at
      FROM tours WHERE is_active = true ORDER BY display_order ASC, created_at DESC
    `);
    res.json(result.rows || result);
  } catch (error) {
    console.error('투어 목록 조회 오류:', error);
    res.status(500).json({ error: '투어 목록을 가져올 수 없습니다.' });
  }
});

// 새 투어 생성
app.post('/api/tours', async (req, res) => {
  try {
    console.log('투어 생성 요청 받음:', req.body);
    const { tour_name, tour_region, duration, promotion_start, promotion_end, is_unlimited, description } = req.body;

    const result = await db.query(`
      INSERT INTO tours (tour_name, tour_region, duration, promotion_start, promotion_end, is_unlimited, description)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id, tour_name, tour_region, duration,
                TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                is_unlimited, description, is_active
    `, [
      tour_name || '',
      tour_region || '',
      duration || '',
      promotion_start || new Date().toISOString().split('T')[0],
      promotion_end || null,
      is_unlimited || false,
      description || ''
    ]);

    console.log('투어 생성 응답:', result.rows[0]);
    res.json(result.rows ? result.rows[0] : { id: result.lastID, ...req.body });
  } catch (error) {
    console.error('투어 생성 오류:', error);
    res.status(500).json({ error: '투어를 생성할 수 없습니다.' });
  }
});

// 투어 정보 수정
app.put('/api/tours/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const processedUpdates = updates;
    
    // 동적으로 업데이트 쿼리 생성
    const fields = Object.keys(processedUpdates);
    const values = Object.values(processedUpdates);
    const setClause = fields.map((field, index) => `${field} = $${index + 2}`).join(', ');
    
    const result = await db.query(`
      UPDATE tours SET ${setClause}, updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING id, tour_name, tour_region, duration,
                TO_CHAR(promotion_start, 'YYYY-MM-DD') as promotion_start,
                TO_CHAR(promotion_end, 'YYYY-MM-DD') as promotion_end,
                is_unlimited, description, is_active
    `, [id, ...values]);
    
    res.json(result.rows ? result.rows[0] : { id, ...updates });
  } catch (error) {
    console.error('투어 수정 오류:', error);
    res.status(500).json({ error: '투어 정보를 수정할 수 없습니다.' });
  }
});

// 투어 삭제
app.delete('/api/tours/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // 완전 삭제
    const result = await db.query('DELETE FROM tours WHERE id = $1', [id]);
    
    res.json({ message: '투어가 삭제되었습니다.', deletedRows: result.rowCount });
  } catch (error) {
    console.error('투어 삭제 오류:', error);
    res.status(500).json({ error: '투어를 삭제할 수 없습니다.' });
  }
});

// 투어 순서 위로 이동
app.put('/api/tours/:id/move-up', async (req, res) => {
  try {
    const { id } = req.params;

    // 현재 투어 정보 조회
    const currentTour = await db.query('SELECT display_order FROM tours WHERE id = $1', [id]);
    if (currentTour.rows.length === 0) {
      return res.status(404).json({ error: '투어를 찾을 수 없습니다.' });
    }

    let currentOrder = currentTour.rows[0].display_order;

    // display_order가 null이거나 0인 경우 재정렬
    if (!currentOrder || currentOrder === 0) {
      await reorderAllTours();
      const updatedTour = await db.query('SELECT display_order FROM tours WHERE id = $1', [id]);
      currentOrder = updatedTour.rows[0].display_order;
    }

    // 이미 최상위인지 확인
    if (currentOrder <= 1) {
      return res.status(400).json({ error: '이미 최상위입니다.' });
    }

    // 위에 있는 투어 찾기 (바로 위 순서)
    const upperTour = await db.query(
      'SELECT id, display_order FROM tours WHERE display_order = $1',
      [currentOrder - 1]
    );

    if (upperTour.rows.length === 0) {
      return res.status(400).json({ error: '이미 최상위입니다.' });
    }

    const upperTourId = upperTour.rows[0].id;
    const upperOrder = upperTour.rows[0].display_order;

    // 순서 교체
    await db.query('UPDATE tours SET display_order = $1 WHERE id = $2', [upperOrder, id]);
    await db.query('UPDATE tours SET display_order = $1 WHERE id = $2', [currentOrder, upperTourId]);

    res.json({ message: '순서가 변경되었습니다.' });
  } catch (error) {
    console.error('투어 순서 이동 오류:', error);
    res.status(500).json({ error: '순서를 변경할 수 없습니다.' });
  }
});

// 투어 순서 아래로 이동
app.put('/api/tours/:id/move-down', async (req, res) => {
  try {
    const { id } = req.params;

    // 현재 투어 정보 조회
    const currentTour = await db.query('SELECT display_order FROM tours WHERE id = $1', [id]);
    if (currentTour.rows.length === 0) {
      return res.status(404).json({ error: '투어를 찾을 수 없습니다.' });
    }

    let currentOrder = currentTour.rows[0].display_order;

    // display_order가 null이거나 0인 경우 재정렬
    if (!currentOrder || currentOrder === 0) {
      await reorderAllTours();
      const updatedTour = await db.query('SELECT display_order FROM tours WHERE id = $1', [id]);
      currentOrder = updatedTour.rows[0].display_order;
    }

    // 전체 투어 개수 확인
    const totalCount = await db.query('SELECT COUNT(*) as count FROM tours');
    const maxOrder = totalCount.rows[0].count;

    // 이미 최하위인지 확인
    if (currentOrder >= maxOrder) {
      return res.status(400).json({ error: '이미 최하위입니다.' });
    }

    // 아래에 있는 투어 찾기 (바로 아래 순서)
    const lowerTour = await db.query(
      'SELECT id, display_order FROM tours WHERE display_order = $1',
      [currentOrder + 1]
    );

    if (lowerTour.rows.length === 0) {
      return res.status(400).json({ error: '이미 최하위입니다.' });
    }

    const lowerTourId = lowerTour.rows[0].id;
    const lowerOrder = lowerTour.rows[0].display_order;

    // 순서 교체
    await db.query('UPDATE tours SET display_order = $1 WHERE id = $2', [lowerOrder, id]);
    await db.query('UPDATE tours SET display_order = $1 WHERE id = $2', [currentOrder, lowerTourId]);

    res.json({ message: '순서가 변경되었습니다.' });
  } catch (error) {
    console.error('투어 순서 이동 오류:', error);
    res.status(500).json({ error: '순서를 변경할 수 없습니다.' });
  }
});

// 투어 순서 재정렬 헬퍼 함수
async function reorderAllTours() {
  try {
    const result = await db.query('SELECT id FROM tours ORDER BY id ASC');
    for (let i = 0; i < result.rows.length; i++) {
      const tourId = result.rows[i].id;
      const newOrder = i + 1;
      await db.query('UPDATE tours SET display_order = $1 WHERE id = $2', [newOrder, tourId]);
    }
  } catch (error) {
    console.error('투어 순서 재정렬 오류:', error);
  }
}

const PORT = process.env.PORT || 3004;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});