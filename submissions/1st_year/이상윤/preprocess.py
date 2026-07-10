import pandas as pd

# 1. [필수 변경] 어린이 보호구역 구글 시트 ID를 입력하세요
SHEET_ID = "1zNLxcgyDbcm-lf_cuLVn9mswYYyjdyZ9O22Ug71tuOw" 
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

print("🔄 구글 시트에서 어린이 보호구역 데이터를 가져오는 중입니다...")

try:
    # 데이터 불러오기 (한글 깨짐 방지)
    try:
        df = pd.read_csv(sheet_url, encoding='utf-8')
    except:
        df = pd.read_csv(sheet_url, encoding='cp949')
        
    print("✅ 데이터 로드 성공!")
    
    # --------------------------------------------------
    # 🔍 [내가 확인할 부분] 내 구글 시트 1행의 글자와 똑같은지 확인하세요.
    # 만약 이름이 다르면 오른쪽 따옴표 안의 글자만 시트와 똑같이 고쳐주세요!
    # --------------------------------------------------
    COL_NUM_ADDR  = '소재지지번주소'   # 또는 '지번주소', '소재지주소' 등
    COL_LAT       = '위도'           # 또는 'Y좌표' 등
    COL_LON       = '경도'           # 또는 'X좌표' 등

    target_cols = [COL_NUM_ADDR, COL_LAT, COL_LON]
    
    # 설정한 열 이름이 실제 시트에 다 있는지 체크
    missing_cols = [col for col in target_cols if col not in df.columns]
    
    if missing_cols:
        print(f"\n❌ [오류] 시트에서 찾을 수 없는 열 이름이 있습니다: {missing_cols}")
        print("현재 구글 시트에 적혀있는 실제 열 이름 전체 목록을 보여드릴게요.")
        print("이 목록을 보시고 코드 상단의 COL_... 변수 이름을 똑같이 수정해 주세요!")
        print("-" * 50)
        print(df.columns.tolist())
        print("-" * 50)
        raise ValueError("열 이름 불일치")

    # 2. 필요한 3개 열만 쏙 빼오기
    df_clean = df[target_cols].copy()
    df_clean.columns = ['지번주소', '위도', '경도']

    # 3. 결측치 처리 (주소가 없으면 삭제하거나 '정보없음' 처리, 위경도는 0.0)
    df_clean = df_clean.dropna(subset=['지번주소']) # 주소가 없는 유령 데이터는 삭제
    df_clean['위도'] = df_clean['위도'].fillna(0.0)
    df_clean['경도'] = df_clean['경도'].fillna(0.0)

    print("\n📊 [전처리 완료 데이터 미리보기 (상위 5개)]")
    print(df_clean.head())

    # 4. 코드스페이스에 파일로 저장
    output_file = "어린이보호구역_위치현황.csv"
    df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n🎉 전처리 완료! 왼쪽 파일 목록에 '{output_file}' 파일이 생성되었습니다.")

except Exception as e:
    if str(e) != "열 이름 불일치":
        print(f"\n❌ 에러 발생: {e}")