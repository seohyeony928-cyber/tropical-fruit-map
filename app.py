import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 가짜 데이터(Mock Data) 생성
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# (실제 프로젝트에서는 엑셀/CSV 파일에서 불러와야 할 부분입니다)
REGION_DATA = {
    "제주 서귀포": {"lat": 33.25, "lon": 126.56, "temp": 16.6, "soil_ph": 6.5, "rain": 1800},
    "전남 해남": {"lat": 34.57, "lon": 126.59, "temp": 14.2, "soil_ph": 6.2, "rain": 1400},
    "경남 통영": {"lat": 34.85, "lon": 128.43, "temp": 14.8, "soil_ph": 6.0, "rain": 1450},
}

FRUIT_INFO = {
    "망고": {"optimal_temp": "20~30도","watery":"65~85%","flower":"2~4월", "link": "https://www.nihhs.go.kr/", "desc": "일조량이 풍부해야 당도가 높음"},
    "파파야": {"optimal_temp": "25~30도", "watery":"60~70%","flower":"상시 개화","link": "https://www.nihhs.go.kr/", "desc": "고온다습한 환경 선호"},
}

# 지역별 과일 적합도 점수 (예시)
SUITABILITY_DATA = {
    "제주 서귀포": {"망고": "1등급 (최적)", "파파야": "2등급 (적합)"},
    "전남 해남": {"망고": "2등급 (적합)", "파파야": "3등급 (가능)"},
    "경남 통영": {"망고": "2등급 (적합)", "파파야": "3등급 (가능)"},
}

# 과일 재배 난이도 / 각 항목 별로
LEVEL_DATA = {
    "망고" : {"watery":"상", "temperature":"상", "fruits":"중","bug":"상","price":"상"},
    "파파야" : {"watery":"중", "temperature":"중", "fruits":"하","bug":"중","price":"중"}
}
# -----------------------------------------------------------------------------
# 2. 사이드바 (분석 모드 선택)
# -----------------------------------------------------------------------------
st.sidebar.title("🥭 열대과일 지도 서비스")
mode = st.sidebar.radio(
    "분석 모드를 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.title(f"{mode}")

# -----------------------------------------------------------------------------
# 3. 모드 1: 지역별 상세 분석 (Region Click -> Info)
# -----------------------------------------------------------------------------
if mode == "📍 지역별 상세 분석":
    col1, col2 = st.columns([1.5, 1]) # 지도(1.5) : 정보창(1) 비율

    # [왼쪽] 지도 표시
    with col1:
        st.subheader("지도에서 지역 선택")
        # 기본 맵 생성 (대한민국 중심)
        m = folium.Map(location=[34.0, 127.5], zoom_start=7)

        # 각 지역에 마커 추가
        for region, coords in REGION_DATA.items():
            folium.Marker(
                [coords['lat'], coords['lon']],
                tooltip=region,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
        
        # 지도 출력 및 클릭 데이터 받기 (클릭 감지는 고급 기능이라 여기선 Selectbox로 대체 연동)
        st_folium(m, height=500, width="100%")

    # [오른쪽] 정보 표시
    with col2:
        st.subheader("지역 상세 정보")
        selected_region = st.selectbox("분석할 지역을 선택하세요", list(REGION_DATA.keys()))
        
        if selected_region:
            region_info = REGION_DATA[selected_region]
            scores = SUITABILITY_DATA[selected_region]

            # 1. 등급 및 순위 (가장 위에 표시)
            st.markdown("##### 🌱 추천 과일 순위")
            df_scores = pd.DataFrame(list(scores.items()), columns=["과일", "등급"])
            st.dataframe(df_scores, hide_index=True, use_container_width=True)
            
            st.divider() # 구분선

            # 2. 기후 및 토양 정보 (중간에 표시)
            st.markdown("##### 🌡️ 기후 및 토양 정보")
            st.metric(label="평균 기온", value=f"{region_info['temp']}°C")
            st.metric(label="토양 산도", value=f"{region_info['soil_ph']}pH")
            st.metric(label="연 강수량", value=f"{region_info['rain']}mm")

            st.divider() # 구분선

            # 3. 종합 의견 (맨 아래 표시)
            st.markdown("##### 💡 종합 의견")
            st.info("이 지역은 겨울철 기온 유지 비용이 타 지역 대비 15% 저렴할 것으로 예상됩니다.")
# -----------------------------------------------------------------------------
# 4. 모드 2: 작물별 적지 지도 (Fruit Select -> Heatmap)
# -----------------------------------------------------------------------------
elif mode == "🍎 작물별 적지 지도":
    # 과일 선택
    selected_fruit = st.selectbox("재배 희망 작물을 선택하세요", list(FRUIT_INFO.keys()))
    
    # 상단: 과일 기본 정보 및 매뉴얼 링크
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
    level = LEVEL_DATA[selected_fruit]
    st.markdown(f"""
    <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; margin-bottom:20px'>
        <h4>{selected_fruit} 재배 난이도 </h4>
        <ul>
            <li><b>습도:</b> {info['watery']}</li>
            <li><b>온도:</b> {info['temperature']}</li>
            <li><b>수확시기:</b> {info['fruits']}</li>
            <li><b>병충해:</b> {info['bug']}</li>
            <li><b>수익:</b> {info['price']}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 국립원예특작과학원 링크 버튼
    st.link_button(f"📖 {selected_fruit} 재배 매뉴얼 보러가기 (국립원예특작과학원)", info['link'])

    st.divider()

    # 하단: 적합도 히트맵 (여기서는 색상 마커로 표현)
    st.subheader(f"🗺️ {selected_fruit} 전국 재배 적지 등급")
    
    m2 = folium.Map(location=[34.0, 127.5], zoom_start=7)

    for region, coords in REGION_DATA.items():
        grade = SUITABILITY_DATA[region][selected_fruit]
        
        # 등급에 따른 마커 색상 변경
        if "1등급" in grade:
            color = "blue" # 최적
            radius = 20
        elif "2등급" in grade:
            color = "green" # 적합
            radius = 15
        elif "3등급" in grade:
            color = "orange" # 가능
            radius = 10
        else:
            color = "red" #불가능
            radius = 10
            
        folium.CircleMarker(
            location=[coords['lat'], coords['lon']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            tooltip=f"{region}: {grade}"
        ).add_to(m2)

    # 범례 설명
    st.caption("🔵 파란색: 1등급(최적) | 🟢 초록색: 2등급(적합) | 🟠 주황색: 3등급(가능)| 🔴 빨강색: 4등급(불가능)") 
 

    st_folium(m2, height=500, width="100%")













