const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// SQLite 데이터베이스 파일 경로
const dbPath = path.join(__dirname, 'chat_consulting.sqlite');

const db = new sqlite3.Database(dbPath);

// 테이블 생성
db.serialize(() => {
  // 관리자 테이블
  db.run(`
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      name TEXT NOT NULL,
      is_online BOOLEAN DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // 대화방 테이블
  db.run(`
    CREATE TABLE IF NOT EXISTS conversations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT UNIQUE NOT NULL,
      admin_id INTEGER,
      customer_name TEXT,
      status TEXT DEFAULT 'waiting' CHECK (status IN ('active', 'closed', 'waiting')),
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (admin_id) REFERENCES admins(id)
    )
  `);

  // 메시지 테이블
  db.run(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      conversation_id INTEGER NOT NULL,
      sender_type TEXT NOT NULL CHECK (sender_type IN ('customer', 'admin')),
      sender_id INTEGER,
      message_text TEXT NOT NULL,
      message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file')),
      is_read BOOLEAN DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (conversation_id) REFERENCES conversations(id),
      FOREIGN KEY (sender_id) REFERENCES admins(id)
    )
  `);

  // 호텔 테이블
  db.run(`
    CREATE TABLE IF NOT EXISTS hotels (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      hotel_name TEXT NOT NULL,
      hotel_region TEXT NOT NULL,
      promotion_start DATE NOT NULL,
      promotion_end DATE,
      is_unlimited BOOLEAN DEFAULT 0,
      adult_price INTEGER NOT NULL,
      child_price INTEGER NOT NULL,
      child_criteria TEXT DEFAULT '만 12세 미만',
      description TEXT,
      is_active BOOLEAN DEFAULT 1,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // 샘플 관리자 데이터 (비밀번호: admin123)
  db.run(`
    INSERT OR IGNORE INTO admins (username, password_hash, name) VALUES 
    ('admin1', '$2b$10$vX1gC3zCPBe.snsZJaer6eP7GSut0MFHM/oIkVC2Eixgr1TzCIoZa', '관리자1')
  `);
});

// PostgreSQL 스타일의 쿼리를 SQLite에 맞게 변환하는 헬퍼 함수들
const query = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    // PostgreSQL의 $1, $2 스타일을 SQLite의 ? 스타일로 변환
    let sqliteSQL = sql.replace(/\$(\d+)/g, '?');
    
    if (sql.includes('RETURNING')) {
      // RETURNING을 사용하는 INSERT/UPDATE 쿼리 처리
      const [mainQuery] = sqliteSQL.split('RETURNING');
      db.run(mainQuery.trim(), params, function(err) {
        if (err) {
          reject(err);
        } else {
          // 방금 삽입된 행을 조회
          const tableName = mainQuery.match(/INSERT INTO (\w+)/i)?.[1] || 
                           mainQuery.match(/UPDATE (\w+)/i)?.[1];
          if (tableName) {
            db.get(`SELECT * FROM ${tableName} WHERE id = ?`, [this.lastID], (err, row) => {
              if (err) reject(err);
              else resolve({ rows: row ? [row] : [] });
            });
          } else {
            resolve({ rows: [] });
          }
        }
      });
    } else if (sql.toUpperCase().startsWith('SELECT')) {
      db.all(sqliteSQL, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve({ rows: rows || [] });
        }
      });
    } else {
      db.run(sqliteSQL, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ rows: [], lastID: this.lastID, changes: this.changes });
        }
      });
    }
  });
};

module.exports = { query, db };