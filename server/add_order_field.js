const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'chat_consulting',
  user: 'postgres',
  password: 'admin123'
});

async function addOrderField() {
  try {
    // 1. display_order 컬럼 추가
    await pool.query(`
      ALTER TABLE tours
      ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0
    `);

    console.log('✅ display_order 컬럼 추가 완료');

    // 2. 기존 투어들에 순서 할당 (id 순서대로)
    const existingTours = await pool.query('SELECT id FROM tours ORDER BY id');

    for (let i = 0; i < existingTours.rows.length; i++) {
      await pool.query(
        'UPDATE tours SET display_order = $1 WHERE id = $2',
        [i + 1, existingTours.rows[i].id]
      );
    }

    console.log(`✅ ${existingTours.rows.length}개 투어에 순서 할당 완료`);

    // 3. 결과 확인
    const result = await pool.query('SELECT id, tour_name, display_order FROM tours ORDER BY display_order');
    console.log('\n현재 투어 순서:');
    result.rows.forEach(tour => {
      console.log(`${tour.display_order}. ${tour.tour_name} (ID: ${tour.id})`);
    });

  } catch (error) {
    console.error('오류:', error);
  } finally {
    pool.end();
  }
}

addOrderField();