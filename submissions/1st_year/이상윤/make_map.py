import pandas as pd
import folium
from sklearn.cluster import DBSCAN
import numpy as np

print("⏳ 전처리된 데이터들을 분석하는 중입니다...")

# 1. 파일 불러오기
try:
    df_cctv = pd.read_csv("CCTV_위경도_주소_대수.csv", encoding='utf-8-sig')
    df_child = pd.read_csv("어린이보호구역_위치현황.csv", encoding='utf-8-sig')
    df_parking = pd.read_csv("불법주정차_신고위치_현황.csv", encoding='utf-8-sig')
except FileNotFoundError as e:
    print(f"❌ 파일을 찾을 수 없습니다: {e}\nCSV 파일명을 확인하세요.")
    exit()

# 유효한 위경도 데이터만 필터링 (대구 지역 범위)
df_cctv_valid = df_cctv[df_cctv['위도'].between(35.5, 36.2) & df_cctv['경도'].between(128.2, 128.9)].copy()
df_child_valid = df_child[df_child['위도'].between(35.5, 36.2) & df_child['경도'].between(128.2, 128.9)].copy()

# 대구 중심 지도 생성
m = folium.Map(location=[35.8714, 128.6014], zoom_start=12)

# --------------------------------------------------
# 🟢 1. 안전 구역 군집화 (CCTV + 스쿨존 좌표 결합)
# --------------------------------------------------
print("🟢 안전 구역(CCTV, 스쿨존) 밀집 지역 계산 중...")
safe_coords = np.vstack([
    df_cctv_valid[['위도', '경도']].values,
    df_child_valid[['위도', '경도']].values
])

# eps=0.003은 약 300m 반경, min_samples=2는 2개 이상 모여있을 때 군집으로 인정
db_safe = DBSCAN(eps=0.003, min_samples=2).fit(safe_coords)
safe_labels = db_safe.labels_

# 군집별로 원 그리기
for label in set(safe_labels):
    if label == -1: continue # 노이즈 제외
    
    cluster_points = safe_coords[safe_labels == label]
    center_lat = np.mean(cluster_points[:, 0])
    center_lon = np.mean(cluster_points[:, 1])
    count = len(cluster_points)
    
    # 뭉쳐있는 개수가 많을수록 원을 더 찐하게 (투명도 opacity 조절, 최대 0.8)
    opacity = min(0.8, 0.2 + (count * 0.05))
    
    # 여러 군집 점들을 포괄하는 대략적인 반지름 계산 (미터 단위)
    radius = max(100, min(500, count * 30))
    
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius,
        popup=f"<b>🟢 정밀 안전 구역</b><br>보안/보호 시설 밀집: {count}개소",
        color="#008000",
        fill=True,
        fill_color="#4DFF4D",
        fill_opacity=opacity,
        stroke=False
    ).add_to(m)

# --------------------------------------------------
# 🔴 2. 위험 구역 판단 및 원 시각화
# --------------------------------------------------
print("🔴 위험 구역 분석 및 지도 시각화 중...")

# 텍스트 주소 기반 매칭 기법을 사용하여 불법주정차 다발 구역 매핑
# 안전 시설 인근에 불법주정차가 얼마나 일어나는지 역추적합니다.
for idx, row in df_parking.head(100).iterrows(): # 상위 100개 다발 지역 매칭
    parking_addr = str(row['신고위치'])
    count = int(row['신고횟수'])
    
    # CCTV나 스쿨존 주소 중 불법주정차 단속 주소와 겹치는 단어(동 이름, 도로명 등)가 있는지 탐색
    matched_cctv = df_cctv_valid[df_cctv_valid['도로명주소'].str.contains(parking_addr[:8], na=False, regex=False)]
    
    if not matched_cctv.empty:
        # 겹치는 구역의 좌표를 가져와 위험 원 생성
        ref_lat = matched_cctv.iloc[0]['위도']
        ref_lon = matched_cctv.iloc[0]['경도']
        
        # 신고 횟수가 많을수록 투명도를 진하게 설정
        opacity = min(0.9, 0.3 + (count * 0.02))
        radius = max(150, min(600, count * 5))
        
        folium.Circle(
            location=[ref_lat, ref_lon],
            radius=radius,
            popup=f"<b>⚠️ 정밀 위험 구역 (불법주정차)</b><br>위치: {parking_addr}<br>신고 건수: {count}건",
            color="#FF0000",
            fill=True,
            fill_color="#FF4D4D",
            fill_opacity=opacity,
            stroke=False
        ).add_to(m)

# 3. 저장
output_map = "대구_정밀_위험도_분석지도.html"
m.save(output_map)

print(f"\n🎉 분석 완료! 고해상도 격자형 지도 '{output_map}' 파일이 생성되었습니다.")
print("다운로드하여 확대해 보시면 동네 골목골목마다 뭉쳐있는 원들을 확인할 수 있습니다!")