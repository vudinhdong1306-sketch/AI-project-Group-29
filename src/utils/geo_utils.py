import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Tính khoảng cách giữa hai điểm trên mặt cầu (Trái Đất) theo Kilômét.
    Sử dụng đồng bộ cho logic Geofencing và trọng số đồ thị.
    """
    try:
        # ĐỔI THÀNH KM: Bán kính Trái Đất ~ 6371 km
        R = 6371.0 
        
        # Ép kiểu float và chuyển sang radian
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        
        a = max(0, min(1, a))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Kết quả sẽ là Kilômét (Ví dụ: 0.005 km thay vì 5 mét)
        return R * c
        
    except (TypeError, ValueError):
        return float('inf')