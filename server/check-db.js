const { db } = require('./database-sqlite');

console.log('Checking SQLite database...');

// 테이블 확인
db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, tables) => {
  if (err) {
    console.error('Error getting tables:', err);
    return;
  }
  console.log('Tables:', tables);

  // 관리자 확인
  db.all("SELECT * FROM admins", (err, admins) => {
    if (err) {
      console.error('Error getting admins:', err);
    } else {
      console.log('Admins:', admins);
    }

    // 대화방 확인
    db.all("SELECT * FROM conversations", (err, conversations) => {
      if (err) {
        console.error('Error getting conversations:', err);
      } else {
        console.log('Conversations:', conversations);
      }

      // 메시지 확인
      db.all("SELECT * FROM messages", (err, messages) => {
        if (err) {
          console.error('Error getting messages:', err);
        } else {
          console.log('Messages:', messages);
        }
        
        process.exit(0);
      });
    });
  });
});