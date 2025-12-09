import streamlit as st
import pandas as pd
import os                        
import zipfile                     
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 데이터 정의
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="열대과일 적정재배지 지도")

# CSS 주입 (글자 크기 등 스타일링)
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 { font-size: 28px !important; }
    .stRadio p { font-size: 18px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def unzip_maps():
    # 파일이 이미 압축 해제되어 있다면 건너뜀
    if os.path.exists("mango_map.html") and os.path.exists("papaya_map.html"):
        return

    # maps.zip 파일이 있으면 압축 해제
    if os.path.exists("maps.zip"):
        with zipfile.ZipFile("maps.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
    else:
        # 파일이 없을 경우 경고 (업로드가 잘 되었는지 확인용)
        st.warning("지도 데이터(maps.zip)가 보이지 않습니다. 파일함에 업로드했는지 확인해주세요.")

# 함수 실행
unzip_maps()

# [수정된 함수] 시나리오 데이터 생성 함수 (망고, 파파야, 포도 통합)
def get_scenario_data(year):
    scenario_list = []
    
    # ---------------------------------------------------------
    # 1. 망고 (Mango) - 기온 상승 시 재배지 북상 (좋아짐)
    # ---------------------------------------------------------
    # 제주: 이미 최적 -> 유지 및 비용 절감
    scenario_list.append({
        "region": "제주 서귀포", "fruit": "망고", "lat": 33.25, "lon": 126.56,
        "grade": "1등급 (최적)", "cause": "생육 적온 충족", 
        "save": 30 + (year - 2025) 
    })
    
    # 해남: 2030년 이후 최적으로 변경
    grade_hm_mango = "1등급 (최적)" if year >= 2030 else "2등급 (적합)"
    scenario_list.append({
        "region": "전남 해남", "fruit": "망고", "lat": 34.57, "lon": 126.59,
        "grade": grade_hm_mango, 
        "cause": "기온 상승으로 적지 편입" if year >= 2030 else "겨울철 보온 필요", 
        "save": 15 + (year - 2025) * 1.5
    })

    # 통영: 2035년 이후 최적으로 변경
    grade_ty_mango = "1등급 (최적)" if year >= 2035 else "2등급 (적합)"
    scenario_list.append({
        "region": "경남 통영", "fruit": "망고", "lat": 34.85, "lon": 128.43,
        "grade": grade_ty_mango,
        "cause": "최적지 전환" if year >= 2035 else "일조량 양호",
        "save": 10 + (year - 2025) * 2
    })

    # ---------------------------------------------------------
    # 2. 파파야 (Papaya) - 고온 작물, 기온 상승 시 내륙 가능성 확대
    # ---------------------------------------------------------
    # 제주: 2028년 이후 2등급 -> 1등급 상승 가정
    grade_jj_papaya = "1등급 (최적)" if year >= 2028 else "2등급 (적합)"
    scenario_list.append({
        "region": "제주 서귀포", "fruit": "파파야", "lat": 33.25, "lon": 126.56,
        "grade": grade_jj_papaya,
        "cause": "아열대 기후 정착" if year >= 2028 else "시설 재배 필요",
        "save": 20 + (year - 2025)
    })

    # 해남: 2032년 이후 3등급 -> 2등급 상승 가정
    grade_hm_papaya = "2등급 (적합)" if year >= 2032 else "3등급 (가능)"
    scenario_list.append({
        "region": "전남 해남", "fruit": "파파야", "lat": 34.57, "lon": 126.59,
        "grade": grade_hm_papaya,
        "cause": "온난화로 노지 재배 가능성" if year >= 2032 else "겨울철 가온 필수",
        "save": 5 + (year - 2025)
    })

    # 통영: 2030년 이후 3등급 -> 2등급 상승 가정
    grade_ty_papaya = "2등급 (적합)" if year >= 2030 else "3등급 (가능)"
    scenario_list.append({
        "region": "경남 통영", "fruit": "파파야", "lat": 34.85, "lon": 128.43,
        "grade": grade_ty_papaya,
        "cause": "해양성 기후 이점" if year >= 2030 else "일조량 부족 주의",
        "save": 8 + (year - 2025)
    })

    # ---------------------------------------------------------
    # 3. 포도 (Grape) - 온대 작물, 너무 더우면 불리함
    # ---------------------------------------------------------
    # 제주: 기온 상승 시 착색 불량 등으로 등급 하락 (3등급 -> 등급 외)
    grade_jj_grape = "3등급 (가능)" if year < 2030 else "등급 외 (부적합)"
    scenario_list.append({
        "region": "제주 서귀포", "fruit": "포도", "lat": 33.25, "lon": 126.56,
        "grade": grade_jj_grape,
        "cause": "고온으로 인한 착색 불량 우려" if year >= 2030 else "평년 기온 유지",
        "save": 0  
    })

    # 해남: 적합 유지
    scenario_list.append({
        "region": "전남 해남", "fruit": "포도", "lat": 34.57, "lon": 126.59,
        "grade": "2등급 (적합)",
        "cause": "배수 양호하나 고온 주의",
        "save": 5 + (year - 2025)
    })

    # 통영: 최적 유지
    scenario_list.append({
        "region": "경남 통영", "fruit": "포도", "lat": 34.85, "lon": 128.43,
        "grade": "1등급 (최적)",
        "cause": "풍부한 일조량과 해풍",
        "save": 10 + (year - 2025)
    })
    
    return pd.DataFrame(scenario_list)

# -----------------------------------------------------------------------------
# 2. 사이드바 UI
# -----------------------------------------------------------------------------
st.sidebar.title("🥭 열대과일 지도 서비스")
mode = st.sidebar.radio(
    "분석 모드를 선택하세요",
    ["📍 지역별 상세 분석", "🍎 작물별 적지 지도"]
)

st.title(f"{mode}")

# -----------------------------------------------------------------------------
# 3. 모드 1: 지역별 상세 분석
# -----------------------------------------------------------------------------
if mode == "📍 지역별 상세 분석":
    col1, col2 = st.columns([1.5, 1])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")

    # [왼쪽] 지도 표시
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
# 4. 모드 2: 작물별 적지 지도
# -----------------------------------------------------------------------------
elif mode == "🍎 작물별 적지 지도":
    # 과일 선택 (포도 포함됨)
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

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏳ 미래 시나리오 설정")
    selected_year = st.sidebar.slider("예측 연도 (RCP 8.5)", 2025, 2035, step=2)
    st.sidebar.info(f"현재 **{selected_year}년** 기준 데이터를 보여줍니다.")

    # 하단: 지도 (슬라이더 연동 + 팝업 강화)
    st.subheader(f"🗺️ {selected_fruit} 전국 재배 적지 등급 ({selected_year}년)")
    
    m2 = folium.Map(location=[34.0, 127.5], zoom_start=7)

    # 시나리오 데이터 가져오기 (망고, 파파야, 포도 모두 처리)
    df_scenario = get_scenario_data(selected_year)
    
    # 선택한 과일 데이터만 필터링
    df_map = df_scenario[df_scenario['fruit'] == selected_fruit]

    # 데이터 매핑 및 표시
    if df_map.empty:
         # 안전장치: 데이터가 없을 경우 기존 정적 데이터 사용
         for region, coords in REGION_DATA.items():
            grade = SUITABILITY_DATA[region].get(selected_fruit, "정보 없음")
            color = "blue" if "1등급" in grade else ("green" if "2등급" in grade else "orange")
            
            folium.CircleMarker(
                location=[coords['lat'], coords['lon']], radius=15, color=color, fill=True, fill_color=color,
                tooltip=f"{region}: {grade}"
            ).add_to(m2)
    else:
        # 시나리오 데이터가 있을 경우 (정상 작동)
        for idx, row in df_map.iterrows():
            # 색상 및 크기 로직
            if "1등급" in row['grade']:
                color = "blue"
                radius = 20
            elif "2등급" in row['grade']:
                color = "green"
                radius = 15
            else: # 3등급 또는 등급 외
                color = "orange"
                radius = 10

            # 팝업 HTML 생성
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
    st.caption("🔵 파란색: 1등급(최적) | 🟢 초록색: 2등급(적합) | 🟠 주황색: 3등급(가능/부적합)") 
 
    st_folium(m2, height=500, width="100%")
    
    st.caption(f"📌 **{selected_year}년 분석:** 기후 변화 시나리오(RCP 8.5)를 적용하여 북상하는 재배 적지를 예측한 결과입니다.")

