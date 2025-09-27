require('dotenv').config();

// PostgreSQL이 없으면 SQLite 사용
const USE_SQLITE = !process.env.DB_HOST || process.env.USE_SQLITE === 'true';

if (USE_SQLITE) {
  console.log('Using SQLite database');
  module.exports = require('./database-sqlite');
} else {
  console.log('Using PostgreSQL database');
  const { Pool } = require('pg');
  
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });
  
  module.exports = pool;
}