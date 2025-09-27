  module.exports = {
    apps: [{
      name: 'backend',
      script: './server/server.js',
      env: {
        DB_PASSWORD: 'admin123',
        DB_HOST: 'localhost',
        DB_PORT: '5432',
        DB_NAME: 'travel_consultation',
        DB_USER: 'travel_user',
        JWT_SECRET: 'your-secret-key-here'
      }
    }]
  };
