import React, { useState } from 'react';
import axios from 'axios';

const SearchPanel = ({ onLocationSelect, placeholder, label }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        const value = e.target.value;
        setQuery(value);

        if (value.length > 3) {
            setLoading(true);
            try {
                // Sử dụng Nominatim API của OSM (miễn phí, không cần key)
                // Giới hạn tìm kiếm trong khu vực Hà Nội bằng viewbox
                const response = await axios.get(
                    `https://nominatim.openstreetmap.org/search?format=json&q=${value}&viewbox=105.80,21.05,105.90,20.95&bounded=1`
                );
                setResults(response.data);
            } catch (error) {
                console.error("Lỗi tìm kiếm địa điểm:", error);
            } finally {
                setLoading(false);
            }
        } else {
            setResults([]);
        }
    };

    const selectLocation = (item) => {
        const coords = {
            lat: parseFloat(item.lat),
            lng: parseFloat(item.lon)
        };
        onLocationSelect(coords); // Gửi tọa độ về App.js
        setQuery(item.display_name.split(',')[0]); // Hiển thị tên ngắn gọn
        setResults([]); // Đóng danh sách gợi ý
    };

    return (
        <div style={{ marginBottom: '15px', position: 'relative' }}>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: '#7f8c8d' }}>{label}</label>
            <input
                type="text"
                value={query}
                onChange={handleSearch}
                placeholder={placeholder}
                style={{
                    width: '100%',
                    padding: '8px 12px',
                    marginTop: '5px',
                    borderRadius: '6px',
                    border: '1px solid #ddd',
                    fontSize: '14px',
                    boxSizing: 'border-box'
                }}
            />
            
            {loading && <div style={{ fontSize: '11px', color: '#3498db' }}>Đang tìm kiếm...</div>}

            {results.length > 0 && (
                <ul style={{
                    position: 'absolute',
                    top: '60px',
                    left: 0,
                    right: 0,
                    backgroundColor: 'white',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    zIndex: 1001,
                    padding: 0,
                    margin: 0,
                    listStyle: 'none',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                    {results.map((item, index) => (
                        <li
                            key={index}
                            onClick={() => selectLocation(item)}
                            style={{
                                padding: '10px',
                                borderBottom: '1px solid #eee',
                                cursor: 'pointer',
                                fontSize: '13px'
                            }}
                            onMouseEnter={(e) => e.target.style.backgroundColor = '#f8f9fa'}
                            onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                        >
                            {item.display_name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SearchPanel;