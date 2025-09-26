import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/admin/login`, {
        username,
        password
      });

      // JWT 토큰과 관리자 정보를 로컬스토리지에 저장
      localStorage.setItem('admin-token', response.data.token);
      localStorage.setItem('admin-info', JSON.stringify(response.data.admin));

      // 관리자 대시보드로 이동
      navigate('/admin/dashboard');
    } catch (error) {
      alert(error.response?.data?.error || '로그인에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login">
      <form className="login-form" onSubmit={handleLogin}>
        <h2>관리자 로그인</h2>
        
        <div className="form-group">
          <label>아이디</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="아이디를 입력하세요"
            required
          />
        </div>

        <div className="form-group">
          <label>비밀번호</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="비밀번호를 입력하세요"
            required
          />
        </div>

        <button 
          type="submit" 
          className="login-button"
          disabled={loading}
        >
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  );
};

export default AdminLogin;