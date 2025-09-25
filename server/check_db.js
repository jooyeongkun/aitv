const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'chat_consulting',
  user: 'postgres',
  password: 'admin123'
});

async function checkDatabase() {
  try {
    // 테이블 목록 확인
    const tablesResult = await pool.query("SELECT tablename FROM pg_tables WHERE schemaname = 'public'");
    console.log('Tables:', tablesResult.rows);

    // tours 테이블이 있으면 데이터 확인
    if (tablesResult.rows.some(row => row.tablename === 'tours')) {
      const toursResult = await pool.query('SELECT * FROM tours LIMIT 10');
      console.log('Tours data:', toursResult.rows);
    }

    // hotels 테이블이 있으면 데이터 확인
    if (tablesResult.rows.some(row => row.tablename === 'hotels')) {
      const hotelsResult = await pool.query('SELECT * FROM hotels LIMIT 10');
      console.log('Hotels data:', hotelsResult.rows);
    }

  } catch (err) {
    console.log('Error:', err.message);
  } finally {
    pool.end();
  }
}

checkDatabase();