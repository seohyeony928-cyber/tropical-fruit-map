import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 스타일링
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# 글씨 크기 조정을 위한 CSS 주입
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 { font-size: 28px !important; }
    .stRadio p { font-size: 18px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 데이터 준비 (시나리오 데이터 + 기존 정적 데이터)
# -----------------------------------------------------------------------------

# (1) 시나리오 데이터 (연도별 변화를 보여주기 위해 DataFrame으로 구성)
# 실제로는 CSV 파일 등을 로드해서 사용
@st.cache_data
def load_scenario_data():
    data = [
        # --- 2025년 데이터 (현재) ---
        {"year": 2025, "region": "제주 서귀포", "lat": 33.25, "lon": 126.56, "fruit": "망고", "grade": "1등급 (최적)", "cause": "생육 적온 충족", "save": 30},
        {"year": 2025, "region": "전남 해남", "lat": 34.57, "lon": 126.59, "fruit": "망고", "grade": "2등급 (적합)", "cause": "겨울철 보온 필요", "save": 15},
        {"year": 2025, "region": "경남 통영", "lat": 34.85, "lon": 128.43, "fruit": "망고", "grade": "2등급 (적합)", "cause": "일조량 양호하나 기온 유의", "save": 10},
        {"year": 2025, "region": "경북 대구", "lat": 35.87, "lon": 128.60, "fruit": "망고", "grade": "4등급 (불가능)", "cause": "동절기 저온 피해 우려", "save": 0},

        # --- 2030년 데이터 (온난화 진행) ---
        {"year": 2030, "region": "제주 서귀포", "lat": 33.25, "lon": 126.56, "fruit": "망고", "grade": "1등급 (최적)", "cause": "최적 생육 환경", "save": 35},
        {"year": 2030, "region": "전남 해남", "lat": 34.57, "lon": 126.59, "fruit": "망고", "grade": "1등급 (최적)", "cause": "기온 상승으로 적지 편입", "save": 25},
        {"year": 2030, "region": "경남 통영", "lat": 34.85, "lon": 128.43, "fruit": "망고", "grade": "2등급 (적합)", "cause": "생육 여건 개선", "save": 20},
        {"year": 2030, "region": "경북 대구", "lat": 35.87, "lon": 128.60, "fruit": "망고", "grade": "3등급 (가능)", "cause": "시설 재배 시 가능", "save": 5},
        
        # --- 2035년 데이터 (북상 완료) ---
        {"year": 2035, "region": "제주 서귀포", "lat": 33.25, "lon": 126.56, "fruit": "망고", "grade": "1등급 (최적)", "cause": "고온 주의 요망", "save": 38},
        {"year": 2035, "region": "전남 해남", "lat": 34.57, "lon": 126.59, "fruit": "망고", "grade": "1등급 (최적)", "cause": "노지 재배 가능성 확대", "save": 30},
        {"year": 2035, "region": "경남 통영", "lat": 34.85, "lon": 128.43, "fruit": "망고", "grade": "1등급 (최적)", "cause": "최적지 전환", "save": 28},
        {"year": 2035, "region": "경북 대구", "lat": 35.87, "lon": 128.60, "fruit": "망고", "grade": "2등급 (적합)", "cause": "안정적 재배권 진입", "save": 15},
    ]
    # 파파야 데이터 등도 같은 방식으로 추가 가능
    return pd.DataFrame(data)

df_scenario = load_scenario_data()

# (2) 정적 참조 데이터 (기존 코드 유지)
REGION_DATA = {
    "제주 서귀포": {"lat": 33.25, "lon": 126.56, "temp": 16.6, "soil_ph": 6.5, "rain": 1800},
    "전남 해남": {"lat": 34.57, "lon": 126.59, "temp": 14.2, "soil_ph": 6.2, "rain": 1400},
    "경남 통영": {"lat": 34.85, "lon": 128.43, "temp": 14.8, "soil_ph": 6.0, "rain": 1450},
    "경북 대구": {"lat": 35.87, "lon": 128.60, "temp": 14.1, "soil_ph": 5.8, "rain": 1100},
}

FRUIT_INFO = {
    "망고": {"optimal_temp": "20~30도","watery":"65~85%","flower":"2~4월", "link": "https://www.nihhs.go.kr/", "desc": "일조량이 풍부해야 당도가 높음"},
    "파파야": {"optimal_temp": "25~30도", "watery":"60~70%","flower":"상시 개화","link": "https://www.nihhs.go.kr/", "desc": "고온다습한 환경 선호"},
}

LEVEL_DATA = {
    "망고" : {"watery":"상", "temperature":"상", "fruits":"중","bug":"상","price":"상"},
    "파파야" : {"watery":"중", "temperature":"중", "fruits":"하","bug":"중","price":"중"}
}

# -----------------------------------------------------------------------------
# 3. 사이드바 UI
# -----------------------------------------------------------------------------
st.sidebar.title("🥭 열대과일 지도 서비스")

mode = st.sidebar.radio(
    "분석 모드를 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.sidebar.markdown("---")

# ★ [NEW] 기후 변화 시나리오 슬라이더 추가
st.sidebar.markdown("### ⏳ 기후 시나리오 설정")
selected_year = st.sidebar.slider(
    "예측 연도 (RCP 8.5)", 
    min_value=2025, 
    max_value=2035, 
    step=5,
    help="슬라이더를 움직이면 미래의 기후 변화에 따른 적지 변화를 볼 수 있습니다."
)
st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 분석 중입니다.")


# -----------------------------------------------------------------------------
# 4. 메인 화면 로직
# -----------------------------------------------------------------------------
st.title(f"{mode}")

# --- 모드 1: 지역별 상세 분석 ---
if mode == "📍 지역별 상세 분석":
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader(f"🗺️ 지도 ({selected_year}년 기준)")
        m = folium.Map(location=[35.5, 127.5], zoom_start=7)

        # 지도 마커 (기본 지역 표시)
        for region, coords in REGION_DATA.items():
            folium.Marker(
                [coords['lat'], coords['lon']],
                tooltip=region,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        
        st_folium(m, height=500, width="100%")

    with col2:
        st.subheader("지역 상세 정보")
        selected_region = st.selectbox("분석할 지역을 선택하세요", list(REGION_DATA.keys()))
        
        if selected_region:
            region_static = REGION_DATA[selected_region]
            
            # 선택한 연도/지역에 맞는 시나리오 데이터 필터링
            scenario_row = df_scenario[
                (df_scenario['year'] == selected_year) & 
                (df_scenario['region'] == selected_region)
            ]

            # 1. 시나리오 기반 예측 결과 (최우선 표시)
            st.markdown(f"##### 🌱 {selected_year}년 재배 예측")
            if not scenario_row.empty:
                # 데이터가 있으면 표시
                row = scenario_row.iloc[0]
                st.success(f"**망고 등급:** {row['grade']}")
                st.write(f"**판정 사유:** {row['cause']}")
                st.write(f"**💰 예상 절감 비용:** 타 지역 대비 {row['save']}% 절감")
            else:
                st.warning("해당 연도의 예측 데이터가 없습니다.")
            
            st.divider()

            # 2. 정적 기후 데이터 (기존 코드 유지)
            st.markdown("##### 🌡️ 기본 기후 및 토양 정보")
            st.metric(label="평균 기온", value=f"{region_static['temp']}°C")
            st.metric(label="토양 산도", value=f"{region_static['soil_ph']}pH")
            st.metric(label="연 강수량", value=f"{region_static['rain']}mm")


# --- 모드 2: 작물별 적지 지도 (핵심 기능 강화) ---
elif mode == "🍎 작물별 적지 지도":
    selected_fruit = st.selectbox("재배 희망 작물을 선택하세요", list(FRUIT_INFO.keys()))
    
    # (1) 과일 정보 박스 (기존 디자인 유지)
    info = FRUIT_INFO[selected_fruit]
    level = LEVEL_DATA.get(selected_fruit, {}) # 안전하게 가져오기

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; height:200px;'>
            <h4 style='margin-top:0;'>{selected_fruit} 적정 생육 조건</h4>
            <ul>
                <li><b>적정 온도:</b> {info['optimal_temp']}</li>
                <li><b>적정 습도:</b> {info['watery']}</li>
                <li><b>특징:</b> {info['desc']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        if level:
            st.markdown(f"""
            <div style='background-color:#fff3e0; padding:15px; border-radius:10px; height:200px;'>
                <h4 style='margin-top:0;'>⚠️ 재배 난이도 분석</h4>
                <ul>
                    <li><b>초기투자비용:</b> {level.get('price', '중')}</li>
                    <li><b>온도관리:</b> {level.get('temperature', '중')}</li>
                    <li><b>병충해:</b> {level.get('bug', '중')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    st.link_button(f"📖 {selected_fruit} 공식 재배 매뉴얼 (농촌진흥청)", info['link'])

    st.divider()

    # (2) ★ 시나리오 지도 시각화 (Folium) ★
    st.subheader(f"🌏 {selected_year}년 {selected_fruit} 재배 적지 지도 (시나리오)")
    
    # 데이터 필터링
    map_data = df_scenario[
        (df_scenario['year'] == selected_year) & 
        (df_scenario['fruit'] == selected_fruit)
    ]

    m2 = folium.Map(location=[35.5, 127.5], zoom_start=7)

    # 데이터가 없을 경우 처리
    if map_data.empty:
        st.warning(f"{selected_year}년 {selected_fruit}에 대한 시나리오 데이터가 아직 없습니다.")
    else:
        for idx, row in map_data.iterrows():
            # 등급별 색상 지정
            if "1등급" in row['grade']:
                color, fill_color = "blue", "#4285F4"
                radius = 18
            elif "2등급" in row['grade']:
                color, fill_color = "green", "#34A853"
                radius = 14
            elif "3등급" in row['grade']:
                color, fill_color = "orange", "#FBBC05"
                radius = 10
            else:
                color, fill_color = "red", "#EA4335"
                radius = 8

            # ★ 팝업 HTML 디자인 (경제성, 저해인자 포함) ★
            popup_html = f"""
            <div style="width:220px; font-family:sans-serif;">
                <h4 style="margin:5px 0;">{row['region']}</h4>
                <p style="font-size:12px; color:gray;">{selected_year}년 예측 시나리오</p>
                <hr style="margin:5px 0;">
                <b>📊 등급:</b> <span style="color:{color}; font-weight:bold">{row['grade']}</span><br>
                <b>🛑 주요 요인:</b> {row['cause']}<br>
                <br>
                <div style="background-color:#f8f9fa; padding:8px; border-radius:5px; font-size:12px;">
                    💰 <b>난방비 절감 효과:</b><br>
                    타 지역 대비 <span style="color:blue; font-weight:bold">{row['save']}%</span> 절감 예상
                </div>
            </div>
            """

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                color=color,
                weight=2,
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['region']} ({row['grade']})"
            ).add_to(m2)

        st_folium(m2, height=600, width="100%")
        
        # 범례
        st.caption(f"📌 **{selected_year}년 분석:** 기후 변화 시나리오(RCP 8.5)를 적용하여 북상하는 재배 적지를 예측한 결과입니다.")
