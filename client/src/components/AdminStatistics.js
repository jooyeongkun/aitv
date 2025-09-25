import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminStatistics = () => {
  const [monthlyCount, setMonthlyCount] = useState(0);
  const [adminInfo, setAdminInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // 로그인 확인
    const token = localStorage.getItem('admin-token');
    const savedAdminInfo = localStorage.getItem('admin-info');
    
    if (!token || !savedAdminInfo) {
      navigate('/admin');
      return;
    }

    setAdminInfo(JSON.parse(savedAdminInfo));
    fetchStatistics();
  }, [navigate]);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get('http://localhost:3006/api/conversations');
      
      // 이번달 상담 갯수 계산
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      const monthlyConversations = response.data.filter(conv => {
        const convDate = new Date(conv.created_at);
        return convDate.getMonth() === currentMonth && convDate.getFullYear() === currentYear;
      });
      setMonthlyCount(monthlyConversations.length);
    } catch (error) {
      console.error('통계 데이터 가져오기 실패:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('admin-token');
    localStorage.removeItem('admin-info');
    navigate('/admin');
  };

  return (
    <div className="admin-dashboard">
      {/* 좌측 네비게이션 */}
      <div className="admin-sidebar">
        <div className="nav-tabs">
          <div className="nav-tab" onClick={() => navigate('/admin/dashboard')}>채팅</div>
          <div className="nav-tab active">통계</div>
          <div className="nav-tab" onClick={() => navigate('/admin/hotels')}>호텔</div>
          <div className="nav-tab">투어</div>
          <div className="nav-tab">렌트카</div>
          <div className="nav-tab">티켓</div>
          <div className="nav-tab">기타</div>
        </div>
      </div>
      
      {/* 통계 메인 화면 */}
      <div className="statistics-main">
        <div className="statistics-header">
          <div className="statistics-title">
            <h2>상담 통계</h2>
            <div className="monthly-stats">
              <span className="month-label">{new Date().getMonth() + 1}월 상담:</span>
              <span className="count-badge">{monthlyCount}건</span>
            </div>
          </div>
          
          <div className="admin-info">
            <p>{adminInfo?.name}님</p>
            <button onClick={logout} className="logout-btn">
              로그아웃
            </button>
          </div>
        </div>
        
        <div className="statistics-content">
          <h3>통계 페이지 준비중...</h3>
          <p>카테고리별 상담 통계, 월별 트렌드 등의 기능이 추가될 예정입니다.</p>
        </div>
      </div>
    </div>
  );
};

export default AdminStatistics;