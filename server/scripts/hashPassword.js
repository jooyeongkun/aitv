const bcrypt = require('bcrypt');

async function hashPassword(password) {
  const saltRounds = 10;
  const hash = await bcrypt.hash(password, saltRounds);
  console.log(`Password: ${password}`);
  console.log(`Hash: ${hash}`);
  return hash;
}

// 기본 관리자 비밀번호 해시 생성
hashPassword('admin123');