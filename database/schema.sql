-- 채팅 상담 시스템 DB 스키마
-- PostgreSQL 용

-- 관리자 테이블
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_online BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 대화방 테이블
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL, -- 고객 브라우저 세션 ID
    admin_id INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    customer_name VARCHAR(100), -- 고객이 입력한 이름 (선택사항)
    status VARCHAR(20) DEFAULT 'waiting' CHECK (status IN ('active', 'closed', 'waiting')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 메시지 테이블
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('customer', 'admin')),
    sender_id INTEGER REFERENCES admins(id) ON DELETE SET NULL, -- admin인 경우만 사용
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_admin_id ON conversations(admin_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 설정
CREATE TRIGGER update_admins_updated_at BEFORE UPDATE ON admins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 샘플 데이터 삽입 (비밀번호: admin123)
INSERT INTO admins (username, password_hash, name) VALUES
('admin1', '$2b$10$vX1gC3zCPBe.snsZJaer6eP7GSut0MFHM/oIkVC2Eixgr1TzCIoZa', '관리자1'),
('admin2', '$2b$10$vX1gC3zCPBe.snsZJaer6eP7GSut0MFHM/oIkVC2Eixgr1TzCIoZa', '관리자2');