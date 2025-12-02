import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 기존 데이터 (작성자님 코드 유지)
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# CSS 주입 (글자 크기 등 스타일링)
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 { font-size: 28px !important; }
    .stRadio p { font-size: 18px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# [기존 데이터] 지역 데이터
REGION_DATA = {
    "제주 서귀포": {"lat": 33.25, "lon": 126.56, "temp": 16.6, "soil_ph": 6.5, "rain": 1800},
    "전남 해남": {"lat": 34.57, "lon": 126.59, "temp": 14.2, "soil_ph": 6.2, "rain": 1400},
    "경남 통영": {"lat": 34.85, "lon": 128.43, "temp": 14.8, "soil_ph": 6.0, "rain": 1450},
}

# [기존 데이터] 과일 정보
FRUIT_INFO = {
    "망고": {"optimal_temp": "20~30도","watery":"65~85%","flower":"2~4월", "link": "https://www.nihhs.go.kr/", "desc": "일조량이 풍부해야 당도가 높음"},
    "파파야": {"optimal_temp": "25~30도", "watery":"60~70%","flower":"상시 개화","link": "https://www.nihhs.go.kr/", "desc": "고온다습한 환경 선호"},
}

# [기존 데이터] 현재 기준 적합도
SUITABILITY_DATA = {
    "제주 서귀포": {"망고": "1등급 (최적)", "파파야": "2등급 (적합)"},
    "전남 해남": {"망고": "2등급 (적합)", "파파야": "3등급 (가능)"},
    "경남 통영": {"망고": "2등급 (적합)", "파파야": "3등급 (가능)"},
}

# [기존 데이터] 난이도 정보
LEVEL_DATA = {
    "망고" : {"watery":"상", "temperature":"상", "fruits":"중","bug":"상","price":"상"},
    "파파야" : {"watery":"중", "temperature":"중", "fruits":"하","bug":"중","price":"중"}
}

# [추가 데이터] 시나리오 데이터 생성 함수 (슬라이더 연동용)
# 기존 지역 데이터를 바탕으로 연도별 변화를 가상으로 생성합니다.
def get_scenario_data(year):
    # 연도가 지날수록(2025 -> 2035) 등급이 좋아지고 비용이 절감되는 로직
    scenario_list = []
    
    # 1. 제주 서귀포 (이미 최적 -> 유지)
    scenario_list.append({
        "region": "제주 서귀포", "fruit": "망고", "lat": 33.25, "lon": 126.56,
        "grade": "1등급 (최적)", "cause": "생육 적온 충족", 
        "save": 30 + (year - 2025)  # 연도별로 절감률 증가
    })
    
    # 2. 전남 해남 (적합 -> 최적으로 변화)
    grade = "1등급 (최적)" if year >= 2030 else "2등급 (적합)"
    scenario_list.append({
        "region": "전남 해남", "fruit": "망고", "lat": 34.57, "lon": 126.59,
        "grade": grade, 
        "cause": "기온 상승으로 적지 편입" if year >= 2030 else "겨울철 보온 필요", 
        "save": 15 + (year - 2025) * 1.5
    })

    # 3. 경남 통영 (적합 -> 최적으로 변화)
    grade_ty = "1등급 (최적)" if year >= 2035 else "2등급 (적합)"
    scenario_list.append({
        "region": "경남 통영", "fruit": "망고", "lat": 34.85, "lon": 128.43,
        "grade": grade_ty,
        "cause": "최적지 전환" if year >= 2035 else "일조량 양호",
        "save": 10 + (year - 2025) * 2
    })
    
    # 파파야 데이터 등도 필요하면 추가 (여기선 망고 위주 예시)
    return pd.DataFrame(scenario_list)

# -----------------------------------------------------------------------------
# 2. 사이드바
# -----------------------------------------------------------------------------
st.sidebar.title("🥭 열대과일 지도 서비스")
mode = st.sidebar.radio(
    "분석 모드를 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.sidebar.markdown("---")

# [추가 기능] 슬라이더: 기존 기능 아래에 배치하여 간섭 최소화
st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=5)
st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")


st.title(f"{mode}")

# -----------------------------------------------------------------------------
# 3. 모드 1: 지역별 상세 분석 (기존 레이아웃 100% 유지 + 시나리오 정보 추가)
# -----------------------------------------------------------------------------
if mode == "📍 지역별 상세 분석":
    col1, col2 = st.columns([1.5, 1])

    # [왼쪽] 지도 표시 (기존 코드 유지)
    with col1:
        st.subheader("지도에서 지역을 선택하시오")
        m = folium.Map(location=[34.0, 127.5], zoom_start=7)

        for region, coords in REGION_DATA.items():
            folium.Marker(
                [coords['lat'], coords['lon']],
                tooltip=region,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        
        st_folium(m, height=500, width="100%")

    # [오른쪽] 정보 표시
    with col2:
        st.subheader("지역 상세 정보")
        selected_region = st.selectbox("분석할 지역을 선택하세요", list(REGION_DATA.keys()))
        
        if selected_region:
            region_info = REGION_DATA[selected_region]
            scores = SUITABILITY_DATA[selected_region]

            # 1. 등급 및 순위 (기존 코드)
            st.markdown("##### 🌱 추천 과일 순위 (현재 기준)")
            df_scores = pd.DataFrame(list(scores.items()), columns=["과일", "등급"])
            st.dataframe(df_scores, hide_index=True, use_container_width=True)
            
            st.divider()

            # 2. 기후 및 토양 정보 (기존 코드)
            st.markdown("##### 🌡️ 기후 및 토양 정보")
            st.metric(label="평균 기온", value=f"{region_info['temp']}°C")
            st.metric(label="토양 산도", value=f"{region_info['soil_ph']}pH")
            st.metric(label="연 강수량", value=f"{region_info['rain']}mm")

            st.divider()

            # [추가 기능] 종합 의견에 '미래 예측' 정보 통합
            st.markdown(f"##### 💡 종합 의견 ({selected_year}년 시나리오)")
            
            # 슬라이더 연도에 따른 절감률 계산 (예시 로직)
            future_save = 15 + (selected_year - 2025) * 2 
            
            st.info(f"""
            이 지역은 **{selected_year}년** 기후 시나리오 적용 시, 
            겨울철 기온 유지 비용이 타 지역 대비 **약 {future_save}% 저렴**할 것으로 예상됩니다.
            (북상 효과 반영)
            """)

# -----------------------------------------------------------------------------
# 4. 모드 2: 작물별 적지 지도 (기존 UI 유지 + 지도만 업그레이드)
# -----------------------------------------------------------------------------
elif mode == "🍎 작물별 적지 지도":
    # 과일 선택
    selected_fruit = st.selectbox("재배 희망 작물을 선택하세요", list(FRUIT_INFO.keys()))
    
    # [기존 UI 복구] 상단: 과일 기본 정보 박스
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

    # [기존 UI 복구] 난이도 정보 박스
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
    
    # [기존 UI 복구] 링크 버튼
    st.link_button(f"📖 {selected_fruit} 재배 매뉴얼 보러가기 (국립원예특작과학원)", info['link'])

    st.divider()

    # [기능 업그레이드] 하단: 지도 (슬라이더 연동 + 팝업 강화)
    st.subheader(f"🗺️ {selected_fruit} 전국 재배 적지 등급 ({selected_year}년)")
    
    m2 = folium.Map(location=[34.0, 127.5], zoom_start=7)

    # 슬라이더 연도에 맞는 데이터 가져오기
    df_scenario = get_scenario_data(selected_year)
    
    # 선택한 과일 데이터만 필터링
    df_map = df_scenario[df_scenario['fruit'] == selected_fruit]

    # 데이터가 없으면 기존 정적 데이터(SUITABILITY_DATA)를 기반으로 표시 (오류 방지)
    if df_map.empty:
         for region, coords in REGION_DATA.items():
            grade = SUITABILITY_DATA[region].get(selected_fruit, "정보 없음")
            # 기존 색상 로직
            color = "blue" if "1등급" in grade else ("green" if "2등급" in grade else "orange")
            
            folium.CircleMarker(
                location=[coords['lat'], coords['lon']], radius=15, color=color, fill=True, fill_color=color,
                tooltip=f"{region}: {grade}"
            ).add_to(m2)
    else:
        # 시나리오 데이터가 있으면 그에 맞춰 표시 (풍부한 팝업 포함)
        for idx, row in df_map.iterrows():
            # 색상 로직
            if "1등급" in row['grade']:
                color = "blue"
                radius = 20
            elif "2등급" in row['grade']:
                color = "green"
                radius = 15
            else:
                color = "orange"
                radius = 10

            # ★ 업그레이드된 팝업 (HTML)
            popup_html = f"""
            <div style="width:200px">
                <h4>{row['region']}</h4>
                <p style="font-size:12px; color:gray;">{selected_year}년 예측</p>
                <hr>
                <b>등급:</b> {row['grade']}<br>
                <b>사유:</b> {row['cause']}<br>
                <br>
                <span style="color:blue; font-weight:bold">💰 난방비 절감: {row['save']}%</span>
            </div>
            """

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['region']} ({row['grade']})"
            ).add_to(m2)

    # 범례 설명
    st.caption("🔵 파란색: 1등급(최적) | 🟢 초록색: 2등급(적합) | 🟠 주황색: 3등급(가능)") 
 
    st_folium(m2, height=500, width="100%")변화 시나리오(RCP 8.5)를 적용하여 북상하는 재배 적지를 예측한 결과입니다.")

