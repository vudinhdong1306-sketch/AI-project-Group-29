import pickle
from scipy.spatial import KDTree
import os
import sys
import numpy as np

# --- CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import hàm tính khoảng cách thực tế
try:
    from src.utils.geo_utils import haversine_distance
except ImportError:
    # Backup hàm tính nếu không import được để tránh crash
    import math
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

class SpatialIndex:
    def __init__(self, nodes_data=None):
        self.node_ids = []
        self.coords = []
        self.tree = None
        
        if nodes_data:
            self.build_index(nodes_data)

    def build_index(self, nodes_data):
        print("\n--- 🌳 Đang xây dựng chỉ mục không gian KDTree (Hai Ba Trung) ---")
        self.node_ids = []
        coords_list = []
        
        for node_id, coords in nodes_data.items():
            # coords có thể là [lat, lon] hoặc [lon, lat] tùy vào lúc parse
            # Chúng ta mặc định lưu trữ là [vĩ độ, kinh độ]
            lat, lon = float(coords[0]), float(coords[1])
            
            # Kiểm tra nhanh: Nếu số > 30 thường là Kinh độ (Lon) ở VN (khoảng 105)
            # Nếu coords[0] > coords[1] ở HN, có khả năng dữ liệu bị ngược Lon/Lat
            self.node_ids.append(str(node_id))
            coords_list.append([lat, lon])
        
        self.coords = np.array(coords_list)
        self.tree = KDTree(self.coords, leafsize=40)
        print(f"✅ Đã index thành công {len(self.node_ids)} nodes.")

    def find_nearest_node(self, lat, lon, max_distance_km=2.5):
        """
        Tìm node gần nhất. Tăng ngưỡng mặc định lên 2.5km để bao quát quận HBT tốt hơn.
        """
        if self.tree is None:
            return None
        
        # 1. Thực hiện truy vấn KDTree
        # Trả về dist (Euclidean) và index của node
        _, index = self.tree.query([float(lat), float(lon)])
        
        nearest_node_id = self.node_ids[index]
        n_lat, n_lon = self.coords[index]

        # 2. Tính khoảng cách thực tế (CỰC KỲ QUAN TRỌNG)
        real_dist = haversine_distance(float(lat), float(lon), n_lat, n_lon)

        # 3. Debug log để soi lỗi tọa độ
        if real_dist > max_distance_km:
            print(f"⚠️ Geofencing: Click({lat}, {lon}) -> Gần nhất({n_lat}, {n_lon})")
            print(f"   Khoảng cách: {real_dist:.2f}km (Vượt ngưỡng {max_distance_km}km)")
            return None
            
        return nearest_node_id

    def save_index(self, path):
        """Lưu trữ chỉ mục (Chỉ lưu dữ liệu cần thiết)"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data_to_save = {
            'node_ids': self.node_ids,
            'coords': self.coords,
            'tree': self.tree
        }
        with open(path, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"📂 Đã lưu Spatial Index thành công: {path}")

    @staticmethod
    def load_index(path):
        """Khôi phục lại đối tượng từ file"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                instance = SpatialIndex()
                instance.node_ids = data['node_ids']
                instance.coords = data['coords']
                instance.tree = data['tree']
                return instance
        return None

if __name__ == "__main__":
    # --- QUY TRÌNH RE-GENERATE ---
    processed_path = os.path.join(BASE_DIR, "data", "processed", "hbt_graph.pkl")
    index_save_path = os.path.join(BASE_DIR, "data", "processed", "spatial_index.pkl")

    if not os.path.exists(processed_path):
        print(f"❌ Không tìm thấy {processed_path}")
    else:
        with open(processed_path, 'rb') as f:
            graph_raw = pickle.load(f)
        
        # Lấy tọa độ nodes
        nodes = graph_raw.get('nodes', {})
        sp_index = SpatialIndex(nodes)
        sp_index.save_index(index_save_path)
        
        # TEST KIỂM TRA
        print(f"\n[TESTING]")
        # Thử điểm tại trung tâm quận HBT
        test_lat, test_lon = 21.011, 105.849 
        res = sp_index.find_nearest_node(test_lat, test_lon)
        print(f"📍 Test Vincom Bà Triệu: Node {res}")