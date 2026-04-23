import os
import sys

# Xác định đường dẫn gốc tuyệt đối
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Thêm cả thư mục gốc và thư mục src vào bộ nhớ Python
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

# Import theo đúng cấu trúc thư mục
try:
    from src.data_processing.osm_parser import OSMParser
    from src.data_processing.spatial_index import SpatialIndex
    print("✅ Hệ thống đã nhận diện được các module.")
except ImportError as e:
    print(f"❌ Lỗi Import: {e}")
    print("💡 Mẹo: Đảm bảo bạn đang đứng ở thư mục gốc 'HBT_pathing AI project' khi chạy.")
    sys.exit(1)

def init_project():
    print("\n--- KHỞI TẠO DỮ LIỆU DỰ ÁN ---")
    raw_osm = os.path.join(BASE_DIR, "data", "raw", "map.osm")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    
    os.makedirs(processed_dir, exist_ok=True)

    if not os.path.exists(raw_osm):
        print(f"❌ Không tìm thấy: {raw_osm}")
        return

    print("Step 1: Parsing OSM...")
    parser = OSMParser(raw_osm)
    graph, nodes = parser.parse()
    
    if graph:
        parser.save(os.path.join(processed_dir, "hbt_graph.pkl"))
        print("Step 2: Building Spatial Index...")
        sp_index = SpatialIndex(nodes)
        sp_index.save_index(os.path.join(processed_dir, "spatial_index.pkl"))
        print("\n🎉 THÀNH CÔNG! Dữ liệu đã sẵn sàng.")
    else:
        print("❌ Lỗi trong quá trình xử lý.")

if __name__ == "__main__":
    init_project()