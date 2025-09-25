import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const TourManagement = () => {
  const [tours, setTours] = useState([]);
  const [filteredTours, setFilteredTours] = useState([]);
  const [adminInfo, setAdminInfo] = useState(null);
  const [editingCell, setEditingCell] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [currentDetail, setCurrentDetail] = useState('');
  const [editingDetail, setEditingDetail] = useState('');
  const [isEditingModal, setIsEditingModal] = useState(false);
  const [editingTourIndex, setEditingTourIndex] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
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
    fetchTours();
  }, [navigate]);

  const fetchTours = async () => {
    try {
      const response = await axios.get('http://localhost:3006/api/tours');
      setTours(response.data);
      setFilteredTours(response.data);
    } catch (error) {
      console.error('투어 데이터 가져오기 실패:', error);
    }
  };

  // 검색 기능
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredTours(tours);
    } else {
      const filtered = tours.filter(tour => 
        tour.tour_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.tour_region?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.duration?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredTours(filtered);
    }
  }, [searchTerm, tours]);

  const logout = () => {
    localStorage.removeItem('admin-token');
    localStorage.removeItem('admin-info');
    navigate('/admin');
  };

  const addNewTour = () => {
    const newTour = {
      id: 'new',
      tour_name: '',
      tour_region: '',
      duration: '',
      adult_price: null,
      child_price: null,
      infant_price: null,
      child_criteria: '',
      infant_criteria: '',
      description: '',
      is_active: true
    };
    setTours([newTour, ...tours]);
    setEditingCell({ row: 0, col: 'tour_name' });
  };

  const updateTour = async (index, field, value) => {
    const tour = tours[index];
    console.log('updateTour 호출:', { index, field, value, tourId: tour.id });
    
    // 로컬 상태 먼저 업데이트
    const updatedTours = [...tours];
    updatedTours[index][field] = value;
    setTours(updatedTours);
    
    try {
      if (tour.id !== 'new') {
        // 기존 투어만 DB 업데이트 (새 투어는 저장하지 않음)
        console.log('투어 DB 업데이트 시도:', tour.id);
        await axios.put(`http://localhost:3006/api/tours/${tour.id}`, {
          [field]: value
        });
        console.log('투어 DB 업데이트 완료');

        // DB 업데이트 후 최신 데이터 다시 가져오기
        await fetchTours();
      } else {
        console.log('새 투어라서 DB 업데이트 안함');
      }
    } catch (error) {
      console.error('투어 업데이트 실패:', error);
      alert('업데이트에 실패했습니다: ' + error.message);
      // 에러 발생 시 원래 데이터로 복원
      await fetchTours();
    }
  };

  const deleteTour = async (index) => {
    const tour = tours[index];

    if (tour.id !== 'new') {
      try {
        await axios.delete(`http://localhost:3006/api/tours/${tour.id}`);
      } catch (error) {
        console.error('투어 삭제 실패:', error);
        return; // 에러가 발생하면 로컬 상태는 업데이트하지 않음
      }
    }

    const updatedTours = tours.filter((_, i) => i !== index);
    setTours(updatedTours);
  };

  // 투어 순서 위로 이동
  const moveTourUp = async (tourId) => {
    try {
      await axios.put(`http://localhost:3006/api/tours/${tourId}/move-up`);
      fetchTours(); // 목록 새로고침
    } catch (error) {
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        console.error('투어 순서 이동 실패:', error);
        alert('순서 변경에 실패했습니다.');
      }
    }
  };

  // 투어 순서 아래로 이동
  const moveTourDown = async (tourId) => {
    try {
      await axios.put(`http://localhost:3006/api/tours/${tourId}/move-down`);
      fetchTours(); // 목록 새로고침
    } catch (error) {
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      } else {
        console.error('투어 순서 이동 실패:', error);
        alert('순서 변경에 실패했습니다.');
      }
    }
  };

  const toggleActiveStatus = async (index) => {
    const tour = tours[index];
    const newStatus = !tour.is_active;
    
    // 로컬 상태 먼저 업데이트
    const updatedTours = [...tours];
    updatedTours[index].is_active = newStatus;
    setTours(updatedTours);
    
    // DB 업데이트 (새 투어가 아닌 경우만)
    if (tour.id !== 'new') {
      try {
        await axios.put(`http://localhost:3006/api/tours/${tour.id}`, {
          is_active: newStatus
        });
      } catch (error) {
        console.error('활성화 상태 업데이트 실패:', error);
      }
    }
  };

  const duplicateTour = (index) => {
    const tour = tours[index];
    const duplicatedTour = {
      ...tour,
      id: 'new',
      tour_name: tour.tour_name + ' (복제본)'
    };
    
    const updatedTours = [...tours];
    updatedTours.splice(index + 1, 0, duplicatedTour);
    setTours(updatedTours);
  };

  const saveDetailFromModal = async () => {
    if (editingTourIndex !== null) {
      await updateTour(editingTourIndex, 'description', editingDetail);
      setCurrentDetail(editingDetail);
      setIsEditingModal(false);
    }
  };

  const saveNewTour = async (index) => {
    const tour = tours[index];
    console.log('saveNewTour 호출:', { index, tour });
    
    if (!tour.tour_name || tour.tour_name.trim() === '') {
      alert('투어명을 입력해주세요.');
      return;
    }
    
    try {
      console.log('투어 저장 시도:', tour);
      const response = await axios.post('http://localhost:3006/api/tours', tour);
      console.log('투어 저장 응답:', response.data);
      const updatedTours = [...tours];
      updatedTours[index] = response.data;
      setTours(updatedTours);
      console.log('투어 저장 완료');
    } catch (error) {
      console.error('투어 저장 실패:', error);
      alert('투어 저장에 실패했습니다: ' + error.message);
    }
  };

  const EditableCell = ({ value, row, col, type = 'text', placeholder = '입력하세요', multiline = false }) => {
    const [inputValue, setInputValue] = useState(value);
    const [clickTimer, setClickTimer] = useState(null);
    const isEditing = editingCell?.row === row && editingCell?.col === col;

    useEffect(() => {
      if (!isEditing) {
        setInputValue(value || '');
      }
    }, [value, isEditing]);

    useEffect(() => {
      return () => {
        if (clickTimer) {
          clearTimeout(clickTimer);
        }
      };
    }, [clickTimer]);

    const handleClick = () => {
      if (!isEditing) {
        if (col === 'description' && value) {
          // 더블클릭 감지를 위해 딜레이 설정
          const timer = setTimeout(() => {
            setCurrentDetail(value);
            setEditingDetail(value);
            setEditingTourIndex(row);
            setIsEditingModal(true); // 바로 편집 모드로 시작
            setShowDetailModal(true);
          }, 200);
          setClickTimer(timer);
          return;
        }
        setEditingCell({ row, col });
        setInputValue(value || '');
      }
    };

    const handleSave = () => {
      let saveValue = inputValue;
      
      // 가격 필드인 경우 콤마 제거 후 저장
      if ((col === 'adult_price' || col === 'child_price' || col === 'infant_price') && inputValue && typeof inputValue === 'string') {
        saveValue = inputValue.replace(/,/g, '');
      }
      
      updateTour(row, col, saveValue);
      setEditingCell(null);
    };

    const handleKeyPress = (e) => {
      if (e.key === 'Enter' && !multiline) {
        handleSave();
      }
      if (e.key === 'Escape') {
        setEditingCell(null);
        setInputValue(value);
      }
      // Ctrl+Enter로 저장 (multiline인 경우)
      if (e.key === 'Enter' && e.ctrlKey && multiline) {
        handleSave();
      }
      // Tab 키로 다음 셀로 이동
      if (e.key === 'Tab') {
        e.preventDefault();
        handleSave();
        moveToNextCell();
      }
    };

    const moveToNextCell = () => {
      const columns = ['tour_name', 'tour_region', 'duration', 'adult_price', 'child_price', 'infant_price', 'child_criteria', 'infant_criteria', 'description'];
      const currentColIndex = columns.indexOf(col);
      const totalRows = filteredTours.length;
      
      let nextRow = row;
      let nextCol = col;
      
      if (currentColIndex < columns.length - 1) {
        // 같은 행의 다음 열로 이동
        nextCol = columns[currentColIndex + 1];
      } else if (row < totalRows - 1) {
        // 다음 행의 첫 번째 열로 이동
        nextRow = row + 1;
        nextCol = columns[0];
      } else {
        // 마지막 셀인 경우 편집 모드 종료
        setEditingCell(null);
        return;
      }
      
      // 다음 셀로 이동
      setTimeout(() => {
        setEditingCell({ row: nextRow, col: nextCol });
        setInputValue(filteredTours[nextRow][nextCol] || '');
      }, 50);
    };

    const handleDoubleClick = (e) => {
      e.preventDefault();
      // 단일 클릭 타이머 취소
      if (clickTimer) {
        clearTimeout(clickTimer);
        setClickTimer(null);
      }
      if (col === 'description') {
        setEditingCell({ row, col });
        setInputValue(value || '');
      }
    };

    if (isEditing) {
      if (multiline) {
        return (
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyPress}
            className="editable-textarea"
            placeholder={`${placeholder} (Ctrl+Enter로 저장)`}
            autoFocus
            rows={3}
          />
        );
      } else {
        const handleInputChange = (e) => {
          let value = e.target.value;
          
          // 가격 필드인 경우 실시간으로 콤마 추가
          if (col === 'adult_price' || col === 'child_price' || col === 'infant_price') {
            // 숫자가 아닌 문자 제거 (콤마 제외)
            value = value.replace(/[^0-9,]/g, '');
            // 기존 콤마 모두 제거
            value = value.replace(/,/g, '');
            // 콤마 추가
            if (value) {
              value = Number(value).toLocaleString();
            }
          }
          
          setInputValue(value);
        };

        return (
          <input
            type={type}
            value={inputValue}
            onChange={handleInputChange}
            onBlur={handleSave}
            onKeyDown={handleKeyPress}
            className="editable-input"
            placeholder={placeholder}
            autoFocus
          />
        );
      }
    }

    const displayValue = () => {
      if (!value) return placeholder;
      
      // 가격 필드인 경우 콤마 추가
      if ((col === 'adult_price' || col === 'child_price' || col === 'infant_price') && value) {
        return Number(value).toLocaleString();
      }
      
      // multiline 필드의 경우 100자 이상이면 ...로 자르기
      if (multiline && value.length > 100) {
        return value.substring(0, 100) + '...';
      }
      
      return value;
    };

    return (
      <div
        className="editable-cell"
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        title={col === 'description' && value ? "클릭: 전체보기" : ""}
      >
        {displayValue()}
      </div>
    );
  };


  return (
    <div className="admin-dashboard">
      {/* 좌측 네비게이션 */}
      <div className="admin-sidebar">
        <div className="nav-tabs">
          <div className="nav-tab" onClick={() => navigate('/admin/dashboard')}>채팅</div>
          <div className="nav-tab" onClick={() => navigate('/admin/statistics')}>통계</div>
          <div className="nav-tab" onClick={() => navigate('/admin/hotels')}>호텔</div>
          <div className="nav-tab active">투어</div>
          <div className="nav-tab">렌트카</div>
          <div className="nav-tab">티켓</div>
          <div className="nav-tab">기타</div>
        </div>
      </div>
      
      {/* 투어 관리 메인 화면 */}
      <div className="hotel-main">
        <div className="hotel-header">
          <div className="hotel-title">
            <h2>투어 관리</h2>
            <button onClick={addNewTour} className="add-btn">+ 새 투어</button>
          </div>
          
          <div className="admin-info">
            <input
              type="text"
              placeholder="투어명, 지역, 상세내용 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <p>{adminInfo?.name}님</p>
            <button onClick={logout} className="logout-btn">로그아웃</button>
          </div>
        </div>
        
        <div className="hotel-table-container">
          <table className="hotel-table tour-table">
            <thead>
              <tr>
                <th style={{ width: '70px', maxWidth: '70px', padding: '8px 2px' }}>순서</th>
                <th style={{ width: '100px', maxWidth: '100px' }}>투어명</th>
                <th style={{ width: '100px', maxWidth: '100px' }}>지역</th>
                <th style={{ width: '100px', maxWidth: '100px' }}>기간</th>
                <th style={{ width: 'auto' }}>상세내용</th>
                <th style={{ width: '70px', maxWidth: '70px' }}>옵션</th>
              </tr>
            </thead>
            <tbody>
              {filteredTours.map((tour, index) => (
                <tr key={tour.id}>
                  <td style={{ textAlign: 'center', whiteSpace: 'nowrap', width: '70px', maxWidth: '70px', padding: '4px 2px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', alignItems: 'center' }}>
                      <button
                        onClick={() => moveTourUp(tour.id)}
                        style={{
                          background: '#007bff',
                          color: 'white',
                          border: 'none',
                          padding: '1px 4px',
                          fontSize: '10px',
                          cursor: 'pointer',
                          borderRadius: '2px',
                          width: '18px',
                          height: '16px',
                          lineHeight: '1'
                        }}
                        title="위로 이동"
                      >
                        ↑
                      </button>
                      <span style={{ fontSize: '10px', color: '#666', margin: '1px 0' }}>
                        {tour.display_order || index + 1}
                      </span>
                      <button
                        onClick={() => moveTourDown(tour.id)}
                        style={{
                          background: '#007bff',
                          color: 'white',
                          border: 'none',
                          padding: '1px 4px',
                          fontSize: '10px',
                          cursor: 'pointer',
                          borderRadius: '2px',
                          width: '18px',
                          height: '16px',
                          lineHeight: '1'
                        }}
                        title="아래로 이동"
                      >
                        ↓
                      </button>
                    </div>
                  </td>
                  <td style={{ width: '100px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', padding: '4px 2px' }}>
                    <EditableCell value={tour.tour_name} row={index} col="tour_name" placeholder="투어명을 입력하세요" />
                  </td>
                  <td style={{ width: '100px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', padding: '4px 2px' }}>
                    <EditableCell value={tour.tour_region} row={index} col="tour_region" placeholder="지역을 입력하세요" />
                  </td>
                  <td style={{ width: '100px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', padding: '4px 2px' }}>
                    <EditableCell value={tour.duration} row={index} col="duration" placeholder="기간을 입력하세요" />
                  </td>
                  <td style={{ width: 'auto' }}>
                    <EditableCell value={tour.description} row={index} col="description" placeholder="상세내용을 입력하세요" multiline={true} />
                  </td>
                  <td style={{ width: '70px', maxWidth: '70px', padding: '4px 2px' }}>
                    <div className="option-buttons">
                      {tour.id === 'new' ? (
                        <button 
                          onClick={() => saveNewTour(index)}
                          className="save-btn"
                        >
                          저장
                        </button>
                      ) : (
                        <>
                          <button 
                            onClick={() => toggleActiveStatus(index)}
                            className={tour.is_active ? "active-btn" : "inactive-btn"}
                          >
                            {tour.is_active ? "활성화" : "비활성화"}
                          </button>
                          <button 
                            onClick={() => duplicateTour(index)}
                            className="duplicate-btn"
                          >
                            복제
                          </button>
                        </>
                      )}
                      <button 
                        onClick={() => deleteTour(index)}
                        className="delete-btn"
                      >
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* 상세내용 모달 */}
      {showDetailModal && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>상세내용 편집</h3>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={saveDetailFromModal}
                  style={{
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    minWidth: '50px',
                    height: '32px'
                  }}
                >
                  저장
                </button>
                <button
                  onClick={() => setShowDetailModal(false)}
                  style={{
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    minWidth: '50px',
                    height: '32px'
                  }}
                >
                  닫기
                </button>
              </div>
            </div>
            <div className="modal-body">
              <textarea
                value={editingDetail}
                onChange={(e) => setEditingDetail(e.target.value)}
                style={{
                  width: '100%',
                  height: '600px',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
                placeholder="상세내용을 입력하세요..."
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TourManagement;