import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os
import zipfile
import shutil

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# 스타일 설정
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 { font-size: 28px !important; }
    .stRadio p { font-size: 18px !important; font-weight: bold; }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 지도 압축 파일(maps.zip) 자동 해제 (Mode 2용)
# -----------------------------------------------------------------------------
def unzip_map_file(zip_name, html_name):
    """zip 파일이 있으면 압축을 풀어서 html 파일을 꺼내는 함수"""
    # 이미 html 파일이 있으면 압축 풀기 건너뜀 (속도 향상)
    if not os.path.exists(html_name):
        if os.path.exists(zip_name):
            try:
                with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                # 혹시 폴더 안에 파일이 생겼을 경우 밖으로 꺼내기
                for root, dirs, files in os.walk("."):
                    if html_name in files and root != ".":
                        shutil.move(os.path.join(root, html_name), html_name)
                
            except Exception as e:
                st.error(f"{zip_name} 압축 해제 중 오류: {e}")

# 앱 실행 시 바로 압축 해제 시도
with st.spinner("지도 데이터를 준비 중입니다..."):
    unzip_map_file("mango_map.zip", "mango_map.html")
    unzip_map_file("papaya_map.zip", "papaya_map.html")
# -----------------------------------------------------------------------------
# 2. 데이터 불러오기 (수정됨: weather_final.csv 읽기)
# -----------------------------------------------------------------------------
@st.cache_data
def load_weather_data():
    """기후 데이터(weather_final.csv) 로드"""
    file_name = "weather_final.csv"
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name, encoding="utf-8")
        except:
            df = pd.read_csv(file_name, encoding="cp949")
        return df.set_index("region").T.to_dict()
    return {}

@st.cache_data
def load_suitability_data():
    """적합도 데이터(suitabilty_data.csv) 로드"""
    file_name = "suitabilty_data.csv"
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name, encoding="utf-8")
        except:
            df = pd.read_csv(file_name, encoding="cp949")
        return df.set_index("region").T.to_dict()
    return {}

# 두 개의 딕셔너리로 각각 저장
REGION_DATA = load_weather_data()
SUITABILITY_DATA = load_suitability_data()
# -----------------------------------------------------------------------------
# 함수: HTML 지도 파일 열기 (Mode 2용)
# -----------------------------------------------------------------------------
def show_html_map(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=600, scrolling=True)
    else:
        st.error(f"⚠️ '{file_name}' 파일을 찾을 수 없습니다.")

# -----------------------------------------------------------------------------
# 과일 정보 상수
# -----------------------------------------------------------------------------
FRUIT_INFO = {
    "망고": {
        "optimal_temp": "24~30℃",
        "watery": "적정 습도 50~60%",
        "flower": "1~3월",
        "desc": "고온다습한 환경을 좋아하며, 겨울철 최저온도 10℃ 이상 유지 필요.",
        "link": "https://www.nongsaro.go.kr/"
    },
    "파파야": {
        "optimal_temp": "25~30℃",
        "watery": "배수가 잘 되는 토양 필요",
        "flower": "연중 개화 가능",
        "desc": "성장이 매우 빠르며, 서리에 매우 취약함.",
        "link": "https://www.nongsaro.go.kr/"
    }
}

LEVEL_DATA = {
    "망고": {"watery": "중", "temperature": "상", "fruits": "1년 1회", "bug": "중", "price": "상"},
    "파파야": {"watery": "하", "temperature": "상", "fruits": "연중 수확", "bug": "하", "price": "중"}
}

# -----------------------------------------------------------------------------
# 메인 앱 로직
# -----------------------------------------------------------------------------
mode = st.sidebar.radio(
    "분석 방법을 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.title(f"{mode}")

# =============================================================================
# 모드 1: 지역별 상세 분석 (대시보드 형태)
# =============================================================================
if mode == "📍 지역별 상세 분석":
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")
    
    # 데이터 파일이 없는 경우 에러 처리
    if not REGION_DATA:
        st.error("⚠️ 'weather_final.csv' 파일을 찾을 수 없습니다.")
    else:
        # 1. 지역 선택 (기후 데이터에 있는 지역 목록 사용)
        selected_region = st.selectbox("🔎 분석하고 싶은 지역을 선택하세요:", list(REGION_DATA.keys()))

        if selected_region:
            # (1) 기후 데이터 가져오기
            weather = REGION_DATA[selected_region]
            current_temp = weather.get('temp', 0)
            current_rain = weather.get('rain', 0)
            
            # (2) 적합도 데이터 가져오기 (없을 수도 있으므로 get 사용)
            suitability = SUITABILITY_DATA.get(selected_region, {})
            mango_res = f"{suitability.get('mango_suitability', '-')} ({suitability.get('mango_grade', '정보없음')})"
            papaya_res = f"{suitability.get('papaya_suitability', '-')} ({suitability.get('papaya_grade', '정보없음')})"

            st.divider()

            # 2. 핵심 지표 출력
            st.subheader(f"📊 {selected_region} 분석 결과 (2024년 기준)")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("연평균 기온", f"{current_temp:.1f}℃")
            with c2:
                st.metric("연 강수량", f"{int(current_rain)}mm")
            with c3:
                st.metric("🥭 망고 적합도", mango_res)
                st.metric("🍈 파파야 적합도", papaya_res)

            st.divider()

            """)
            # 3. 미래 예측 시나리오 (선택한 연도에 맞춰 계산)
            st.subheader(f"🔮 {selected_year}년 미래 예측 시나리오")
            
            # 미래 기온 상승 시뮬레이션 (1년에 0.1도 상승 가정)
            temp_increase = (selected_year - 2024) * 0.1
            future_temp = round(current_temp + temp_increase, 1)
            
            # 절감 비용 계산 (기온이 높을수록 난방비 절감)
            if future_temp > 10:
                cost_save = int((future_temp - 10) * 5)
            else:
                cost_save = 0
            
            # 결과 박스 표시
            st.info(f"""
            지구온난화 시나리오(RCP 8.5)에 따르면, **{selected_year}년**에는 
            **{selected_region}**의 연평균 기온이 **약 {future_temp}℃**까지 상승할 것으로 예상됩니다.
            
            이에 따라 겨울철 난방 비용이 현재보다 **약 {cost_save}% 절감**되어 
            아열대 작물 재배 경제성이 향상될 것입니다.
            """)

# =============================================================================
# 모드 2: 작물별 적지 지도 (HTML 지도)
# =============================================================================
elif mode == "🍎 작물별 적지 지도":
    # 과일 선택
    selected_fruit = st.selectbox("재배 희망 작물을 선택하세요", list(FRUIT_INFO.keys()))
    
    # 상단: 과일 기본 정보 박스
    info = FRUIT_INFO[selected_fruit]
    st.markdown(f"""
    <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px'>
        <h4>{selected_fruit} 적정 생육 조건</h4>
        <ul>
            <li><b>적정 온도:</b> {info['optimal_temp']}</li>
            <li><b>적정 습도:</b> {info['watery']}</li>
            <li><b>국내 개화 시기:</b> {info['flower']}</li>
            <li><b>특징:</b> {info['desc']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 난이도 정보 박스
    level = LEVEL_DATA[selected_fruit]
    st.markdown(f"""
    <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px'>
        <h4>{selected_fruit} 재배 난이도 </h4>
        <ul>
            <li><b>습도관리:</b> {level['watery']}</li>
            <li><b>온도관리:</b> {level['temperature']}</li>
            <li><b>수확시기:</b> {level['fruits']}</li>
            <li><b>병충해:</b> {level['bug']}</li>
            <li><b>수익성:</b> {level['price']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 링크 버튼
    st.link_button(f"📖 {selected_fruit} 재배 매뉴얼 보러가기 (국립원예특작과학원)", info['link'])

    st.divider()
    
    # 사이드바 시나리오
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")

    # -----------------------------------------------------------
    # 분석된 HTML 지도 보여주기
    # -----------------------------------------------------------
    st.subheader(f"🗺️ {selected_fruit} 적정 재배지 정밀 분석 지도")
    
    if selected_fruit == "망고":
        show_html_map("mango_map.html")
    elif selected_fruit == "파파야":
        show_html_map("papaya_map.html")
    else:
        st.info("이 작물에 대한 정밀 분석 지도는 준비 중입니다.")




