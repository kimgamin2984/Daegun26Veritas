import pandas as pd

# 1. [필수 변경] 본인의 구글 시트 ID를 입력하세요
# 브라우저 단축키 오류가 날 수 있으니, 마우스로 상단 메뉴 [File] -> [Save]를 눌러 저장하세요!
SHEET_ID = "1T3RNtiowSwmIWUIRBAWqWQObZkJB8z9yxYy-iuZct-g" 
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

print("🔄 구글 시트에서 CCTV 데이터를 안전하게 원격 로드 중입니다...")

try:
    # 데이터 불러오기 (한글 깨짐 대비 utf-8 사용, 안 되면 cp949로 자동 전환)
    try:
        df = pd.read_csv(sheet_url, encoding='utf-8')
    except:
        df = pd.read_csv(sheet_url, encoding='cp949')
        
    print("✅ 데이터 로드 성공!")
    print(f"현재 데이터 크기: {df.shape[0]}행, {df.shape[1]}열")

    # --------------------------------------------------
    # 💡 [핵심 변형] 열 이름 대신 "순서(번호)"로 열을 선택합니다.
    # 공공데이터 특성상 보통 첫 번째나 두 번째 열에 위치와 대수가 있습니다.
    # --------------------------------------------------
    
    # 만약 구글 시트의 실제 순서와 다르다면 아래 숫자(0, 1)를 바꾸시면 됩니다.
    # 0은 첫 번째 열, 1은 두 번째 열, 2는 세 번째 열...
    LOCATION_COLUMN_INDEX = 0  # 설치 위치가 있는 열의 순서
    COUNT_COLUMN_INDEX = 1     # 카메라 대수가 있는 열의 순서

    # 실제 컴퓨터가 인식한 열 이름 가져오기
    col_location_name = df.columns[LOCATION_COLUMN_INDEX]
    col_count_name = df.columns[COUNT_COLUMN_INDEX]
    
    print(f"\n[자동 매칭 완료]")
    print(f"📍 위치 정보 열: '{col_location_name}' (시트의 {LOCATION_COLUMN_INDEX + 1}번째 열)")
    print(f"🔢 카메라 대수 열: '{col_count_name}' (시트의 {COUNT_COLUMN_INDEX + 1}번째 열)")

    # 2. 필요한 두 가지 열만 추출 및 이름 통일
    df_clean = df[[col_location_name, col_count_name]].copy()
    df_clean.columns = ['설치위치', '카메라대수']

    # 3. 결측치 처리 (빈 칸 채우기)
    df_clean['설치위치'] = df_clean['설치위치'].fillna('위치 불명')

    # 4. 카메라 대수 숫자 정제 (문자열, 콤마 제거 후 정수형 변환)
    df_clean['카메라대수'] = df_clean['카메라대수'].astype(str).str.replace(',', '', regex=True)
    df_clean['카메라대수'] = pd.to_numeric(df_clean['카메라대수'], errors='coerce')
    df_clean['카메라대수'] = df_clean['카메라대수'].fillna(0).astype(int)
    
    # 5. 대수 많은 순으로 정렬
    df_clean = df_clean.sort_values(by='카메라대수', ascending=False)

    print("\n📊 [전처리 완료 데이터 미리보기 (상위 5개)]")
    print(df_clean.head())

    # 6. 최종 결과 저장
    output_file = "CCTV_위치_및_대수.csv"
    df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n🎉 전처리가 성공적으로 끝나 '{output_file}' 파일로 저장되었습니다!")

except Exception as e:
    print(f"\n❌ 에러가 발생했습니다. 아래 메시지를 확인해 주세요.")
    print(f"에러 내용: {e}")