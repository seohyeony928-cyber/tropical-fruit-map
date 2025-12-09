import streamlit as st
import streamlit.components.v1 as components  # HTML 지도 출력을 위한 모듈
import os
import zipfile
import shutil

# -----------------------------------------------------------------------------
# 1. 페이지 설정 (기존 유지)
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# 스타일 설정 (기존 유지)
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 { font-size: 28px !important; }
    .stRadio p { font-size: 18px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# [새로 추가된 기능] 지도 압축 파일(maps.zip) 자동 해제
# -----------------------------------------------------------------------------
def unzip_maps():
    # 이미 파일이 준비되어 있으면 패스
    if os.path.exists("mango_map.html") and os.path.exists("papaya_map.html"):
        return

    # 업로드된 zip 파일 찾기 (이름이 달라도 찾을 수 있게)
    zip_file = None
    if os.path.exists("map.zip"):
        zip_file = "map.zip"
    elif os.path.exists("maps.zip"):
        zip_file = "maps.zip"

    if zip_file:
        try:
            # 압축 해제
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # [중요] 압축을 풀었는데 파일이 폴더 안에 숨어있을 경우를 대비해 꺼내오기
            # 현재 폴더를 다 뒤져서 mango_map.html이 보이면 밖으로 이동시킴
            for root, dirs, files in os.walk("."):
                if "mango_map.html" in files and root != ".":
                    shutil.move(os.path.join(root, "mango_map.html"), "mango_map.html")
                if "papaya_map.html" in files and root != ".":
                    shutil.move(os.path.join(root, "papaya_map.html"), "papaya_map.html")
                    
        except zipfile.BadZipFile:
            st.error("🚨 압축 파일이 손상되었습니다. 다시 압축해서 올려주세요.")
    else:
        st.warning(f"⚠️ 'map.zip' 파일을 찾을 수 없습니다. 파일함에 업로드되었는지 확인해주세요.")

# 압축 해제 실행
unzip_maps()
# -----------------------------------------------------------------------------
# 2. 사이드바 UI (기존 기능 모두 유지)
# -----------------------------------------------------------------------------
st.sidebar.header("옵션 선택")

# (1) 작물 선택
selected_fruit = st.sidebar.radio("작물을 선택하세요:", ["망고", "파파야"])

st.sidebar.markdown("---")

# (2) 연도 및 시나리오 설정 (기존 UI 유지)
# ※ 주의: 지도는 분석이 완료된 파일이므로, 슬라이더를 움직여도 지도가 즉시 변하진 않지만 
#         화면 구성 유지를 위해 남겨둡니다.
selected_year = st.sidebar.selectbox("예측 연도 선택", [2025, 2030, 2040, 2050])

st.sidebar.markdown("### 🌡️ 기후 변화 시나리오 설정")
temp_change = st.sidebar.slider("평균 기온 상승폭 (℃)", 0.0, 5.0, 1.5, 0.1)
rain_change = st.sidebar.slider("강수량 변화율 (%)", -20, 20, 0, 5)

# 선택된 옵션 정보 표시
st.sidebar.info(f"""
**설정된 시나리오:**
- 목표 연도: {selected_year}년
- 기온: +{temp_change}℃
- 강수량: {rain_change}%
""")

# -----------------------------------------------------------------------------
# 3. 메인 화면 및 지도 출력 (변경된 부분)
# -----------------------------------------------------------------------------
st.title("🍎 열대과일 적정 재배지 분석 결과")
st.write(f"기후 데이터 분석을 통해 도출된 **{selected_year}년 {selected_fruit}** 적정 재배지 지도입니다.")

# -------------------------------------------------------------------
# [변경] 기존의 REGION_DATA 및 folium 마커 생성 코드를 삭제하고
#        HTML 파일을 불러오는 함수로 대체했습니다.
# -------------------------------------------------------------------
def show_html_map(file_name):
    # 파일 존재 여부 확인
    if not os.path.exists(file_name):
        st.error(f"지도 파일({file_name})을 찾을 수 없습니다. maps.zip 파일을 확인해주세요.")
        return

    # HTML 파일 읽기 (한글 깨짐 방지를 위해 utf-8 지정)
    with open(file_name, 'r', encoding='utf-8') as f:
        map_html = f.read()
    
    # 스트림릿 컴포넌트로 HTML 출력 (높이 700px)
    components.html(map_html, height=700, scrolling=True)


# 선택된 작물에 따라 알맞은 지도 파일 보여주기
if selected_fruit == "망고":
    st.subheader("🥭 망고 재배지 분석 지도")
    show_html_map("mango_map.html")

elif selected_fruit == "파파야":
    st.subheader("🍈 파파야 재배지 분석 지도")
    show_html_map("papaya_map.html")


