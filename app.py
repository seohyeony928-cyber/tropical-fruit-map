import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
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
# ... (앞부분 임포트 코드는 그대로 유지) ...

# -----------------------------------------------------------------------------
# [최적화됨] 지도 압축 파일(maps.zip) 자동 해제 로직
# -----------------------------------------------------------------------------
# 파일이 이미 있는지 확인 (매번 압축 풀지 않게 하여 속도 향상)
if not (os.path.exists("mango_map.html") and os.path.exists("papaya_map.html")):
    # html 파일이 없을 때만 실행
    if os.path.exists("maps.zip"):
        with st.spinner("지도 데이터를 준비 중입니다... 잠시만 기다려 주세요!"):
            try:
                with zipfile.ZipFile("maps.zip", 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                # (폴더 안에 파일이 숨어있을 경우 밖으로 꺼내는 안전장치)
                for root, dirs, files in os.walk("."):
                    for file in ["mango_map.html", "papaya_map.html"]:
                        if file in files and root != ".":
                            shutil.move(os.path.join(root, file), file)
                
                st.success("지도 준비 완료!")
            except Exception as e:
                st.error(f"압축 파일 해제 중 오류 발생: {e}")
    else:
        # zip 파일도 없고 html 파일도 없는 경우
        st.warning("⚠️ 지도 파일(maps.zip)을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해주세요.")
        
# ... (나머지 코드는 그대로 유지) ...
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
@st.cache_data
def load_region_data():
    """CSV 파일을 읽어서 딕셔너리로 변환"""
    if os.path.exists("region_data.csv"):
        try:
            df = pd.read_csv("region_data.csv", encoding="utf-8")
        except:
            df = pd.read_csv("region_data.csv", encoding="cp949")
            
        # 딕셔너리 구조: {'거제시': {'temp': 16.0, 'rain': 1440}, ...}
        return df.set_index("region").T.to_dict()
    else:
        return {}

REGION_DATA = load_region_data()

#st.sidebar.title("🥭 열대과일 지도 서비스")
mode = st.sidebar.radio(
    "분석 방법을 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.title(f"{mode}")

# -----------------------------------------------------------------------------
# 4. 모드 1: 지역별 상세 분석 (기존 코드 유지 - Folium 사용)
# -----------------------------------------------------------------------------
if mode == "📍 지역별 상세 분석":
    col1, col2 = st.columns([1.5, 1])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")

    selected_region = st.selectbox("재배 희망 작물을 선택하세요", list(REGION_data.keys()))


    # [오른쪽] 정보 표시
    with col2:
        st.subheader("지역 상세 정보")
        selected_region = st.selectbox("분석할 지역을 선택하세요", list(REGION_DATA.keys()))
        
        if selected_region:
            region_info = REGION_DATA[selected_region]
            scores = SUITABILITY_DATA[selected_region]

            # 1. 등급 및 순위
            st.markdown("##### 🌱 추천 과일 순위 (현재 기준)")
            df_scores = pd.DataFrame(list(scores.items()), columns=["과일", "등급"])
            st.dataframe(df_scores, hide_index=True, use_container_width=True)
            
            st.divider()

            # 2. 기후 및 토양 정보
            st.markdown("##### 🌡️ 기후 및 토양 정보")
            st.metric(label="평균 기온", value=f"{region_info['temp']}°C")
            st.metric(label="토양 산도", value=f"{region_info['soil_ph']}pH")
            st.metric(label="연 강수량", value=f"{region_info['rain']}mm")

            st.divider()

            # 3. 미래 예측 의견
            st.markdown(f"##### 💡 종합 의견 ({selected_year}년 시나리오)")
            
            future_save = 15 + (selected_year - 2025) * 2 
            
            st.info(f"""
            이 지역은 **{selected_year}년** 기후 시나리오 적용 시, 
            겨울철 기온 유지 비용이 타 지역 대비 **약 {future_save}% 저렴**할 것으로 예상됩니다.
            (북상 효과 반영)
            """)

# -----------------------------------------------------------------------------
# 5. 모드 2: 작물별 적지 지도 (HTML 지도 연동으로 변경)
# -----------------------------------------------------------------------------
elif mode == "🍎 작물별 적지 지도":
    # 과일 선택
    selected_fruit = st.selectbox("재배 희망 작물을 선택하세요", list(FRUIT_INFO.keys()))
    
    # 상단: 과일 기본 정보 박스 (기존 유지)
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

    # 난이도 정보 박스 (기존 유지)
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
    
    # 사이드바 시나리오 (지도 모양은 안 바뀌지만 UI 유지)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")

    # -----------------------------------------------------------
    # [변경됨] 분석된 HTML 지도 보여주기
    # -----------------------------------------------------------
    st.subheader(f"🗺️ {selected_fruit} 적정 재배지 정밀 분석 지도")
    
    if selected_fruit == "망고":
        show_html_map("mango_map.html")
    elif selected_fruit == "파파야":
        show_html_map("papaya_map.html")
    else:
        st.info("이 작물에 대한 정밀 분석 지도는 준비 중입니다.")









