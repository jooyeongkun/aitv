const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'chat_consulting',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASS || 'your_password'
});

async function checkData() {
  try {
    // 호텔 지역 확인
    const hotelsResult = await pool.query('SELECT DISTINCT hotel_region, COUNT(*) as count FROM hotels WHERE is_active = true GROUP BY hotel_region ORDER BY hotel_region');
    console.log('=== 호텔 지역별 데이터 ===');
    hotelsResult.rows.forEach(row => {
      console.log(`${row.hotel_region}: ${row.count}개`);
    });
    
    console.log('\n=== 투어 지역별 데이터 ===');
    // 투어 지역 확인  
    const toursResult = await pool.query('SELECT DISTINCT tour_region, COUNT(*) as count FROM tours WHERE is_active = true GROUP BY tour_region ORDER BY tour_region');
    toursResult.rows.forEach(row => {
      console.log(`${row.tour_region}: ${row.count}개`);
    });
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await pool.end();
  }
}

checkData();