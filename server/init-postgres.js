require('dotenv').config();
const { Pool } = require('pg');
const bcrypt = require('bcrypt');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

async function initializeDatabase() {
  const client = await pool.connect();
  
  try {
    console.log('PostgreSQL 데이터베이스 초기화 시작...');

    // 관리자 테이블
    await client.query(`
      CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        is_online BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 대화방 테이블
    await client.query(`
      CREATE TABLE IF NOT EXISTS conversations (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(255) UNIQUE NOT NULL,
        admin_id INTEGER REFERENCES admins(id),
        customer_name VARCHAR(100),
        status VARCHAR(20) DEFAULT 'waiting' CHECK (status IN ('active', 'closed', 'waiting')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 메시지 테이블
    await client.query(`
      CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        conversation_id INTEGER NOT NULL REFERENCES conversations(id),
        sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('customer', 'admin', 'system', 'ai')),
        sender_id INTEGER REFERENCES admins(id),
        message_text TEXT NOT NULL,
        message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file')),
        is_read BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 호텔 테이블
    await client.query(`
      CREATE TABLE IF NOT EXISTS hotels (
        id SERIAL PRIMARY KEY,
        hotel_name VARCHAR(200) NOT NULL,
        hotel_region VARCHAR(100) NOT NULL,
        promotion_start DATE NOT NULL,
        promotion_end DATE,
        is_unlimited BOOLEAN DEFAULT false,
        adult_price INTEGER,
        child_price INTEGER,
        child_criteria VARCHAR(100) DEFAULT '만 12세 미만',
        description TEXT,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 투어 테이블
    await client.query(`
      CREATE TABLE IF NOT EXISTS tours (
        id SERIAL PRIMARY KEY,
        tour_name VARCHAR(200) NOT NULL,
        tour_region VARCHAR(100) NOT NULL,
        promotion_start DATE NOT NULL,
        promotion_end DATE,
        is_unlimited BOOLEAN DEFAULT false,
        adult_price INTEGER,
        child_price INTEGER,
        infant_price INTEGER,
        child_criteria VARCHAR(100) DEFAULT '만 12세 미만',
        infant_criteria VARCHAR(100) DEFAULT '만 3세 미만',
        description TEXT,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 샘플 관리자 데이터 삽입 (비밀번호: admin123)
    const hashedPassword = await bcrypt.hash('admin123', 10);
    await client.query(`
      INSERT INTO admins (username, password_hash, name) 
      VALUES ($1, $2, $3)
      ON CONFLICT (username) DO NOTHING
    `, ['admin1', hashedPassword, '관리자1']);

    console.log('PostgreSQL 데이터베이스 초기화 완료!');
    console.log('관리자 계정: admin1 / admin123');
    
  } catch (error) {
    console.error('데이터베이스 초기화 오류:', error);
  } finally {
    client.release();
    pool.end();
  }
}

initializeDatabase();