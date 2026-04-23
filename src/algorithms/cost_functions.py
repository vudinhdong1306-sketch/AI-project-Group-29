import os
import sys

# Thêm đường dẫn gốc của project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.geo_utils import haversine_distance

class CostCalculator:
    def __init__(self, traffic_manager=None):
        self.traffic_manager = traffic_manager
        
        # ĐIỀU CHỈNH LẠI: Hệ số loại đường (Road Priority)
        # Thu hẹp khoảng cách giữa đường lớn và đường nhỏ để hệ số Tắc đường có tác dụng mạnh hơn
        self.road_priority = {
            'motorway': 0.8,
            'trunk': 0.85,
            'primary': 0.9,      # Các trục đường chính
            'secondary': 1.0,    # Đường tiêu chuẩn (mốc 1.0)
            'tertiary': 1.1,
            'unclassified': 1.2,
            'residential': 1.3,   # Đường dân cư
            'living_street': 1.4,
            'service': 1.5,       # Ngõ nhỏ
            'default': 1.0
        }

    def dynamic_cost(self, u, v, u_coord, v_coord, edge_data):
        """
        Công thức: Cost = Distance * Road_Priority * Traffic_Penalty
        """
        
        # 1. Lấy khoảng cách vật lý
        distance = edge_data.get('weight')
        if distance is None or distance == 0:
            distance = haversine_distance(u_coord[0], u_coord[1], v_coord[0], v_coord[1])
        
        # 2. Lấy hệ số loại đường
        road_type = edge_data.get('type', 'default')
        if isinstance(road_type, list):
            road_type = road_type[0]
        
        priority_factor = self.road_priority.get(road_type, self.road_priority['default'])

        # 3. Lấy hệ số động từ Traffic Manager
        traffic_factor = 1.0
        if self.traffic_manager:
            # LƯU Ý: Đảm bảo traffic_manager trả về giá trị > 1 khi tắc
            # và trả về float('inf') khi ngập nặng
            traffic_factor = self.traffic_manager.get_traffic_coefficient(u, v)
        
        # 4. Kiểm tra chặn đường (Ngập lụt)
        if traffic_factor >= 999999: # Sử dụng ngưỡng thay vì so sánh float('inf') trực tiếp cho an toàn
            return 999999999.0
            
        # 5. Tính toán chi phí cuối cùng
        # Nếu traffic_factor = 4 (Admin gán x4)
        # Cost = Distance * Priority * 4
        total_cost = distance * priority_factor * traffic_factor
        
        return total_cost

    def simple_distance_cost(self, u, v, u_coord, v_coord, edge_data):
        """Hàm chi phí thuần khoảng cách vật lý"""
        distance = edge_data.get('weight')
        if not distance or distance == 0:
            distance = haversine_distance(u_coord[0], u_coord[1], v_coord[0], v_coord[1])
        return distance