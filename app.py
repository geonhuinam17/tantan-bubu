import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #f0f2f6; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 (소유주 구분 및 만원 단위 반영)
@st.cache_data(ttl=300)
def get_data():
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 105000000,
        "base_net_asset": 75760000,
        "monthly_income": 11547372,
        "monthly_expense": 6125348,
        "monthly_savings": 5422024,
        "baby_prep_percent": 68
    }
    
    # [수정 4] 소유주별 포트폴리오 데이터 (분홍-아내 / 하늘-남편)
    portfolio = pd.DataFrame([
        {"소유주": "건희(아내)", "항목": "해외주식(진)", "금액": 35000000, "색상": "#FF1493"},
        {"소유주": "건희(아내)", "항목": "연금저축", "금액": 16800000, "색상": "#FF69B4"},
        {"소유주": "건희(아내)", "항목": "ISA", "금액": 5000000, "색상": "#FFB6C1"},
        {"소유주": "건희(아내)", "항목": "보험", "금액": 3070000, "색상": "#FFC0CB"},
        {"소유주": "동현(남편)", "항목": "해외주식(진)", "금액": 31030000, "색상": "#00BFFF"},
        {"소유주": "동현(남편)", "항목": "가상화폐", "금액": 6100000, "색상": "#87CEEB"},
        {"소유주": "동현(남편)", "항목": "ISA", "금액": 5130000, "색상": "#ADD8E6"}
    ])
    
    # [수정 5] 시계열 데이터 (만원 단위 계산 및 증감분 포함)
    trend = pd.DataFrame({
        "날짜": pd.to_datetime(["2025-03-01", "2025-05-01", "2025-08-01", "2025-10-01", "2025-12-01", "2026-01-01", "2026-02-01"]),
        "순자산": [72000000, 75000000, 75760000, 89000000, 98000000, 105000000, 112740391]
    })
    trend['순자산_만원'] = (trend['순자산'] / 10000).astype(int)
    trend['증감'] = trend['순자산_만원'].diff().fillna(0).astype(int)
    trend['라벨'] = trend.apply(lambda x: f"{x['순자산_만원']:,}만\n(+{x['증감']:,})" if x['증감'] > 0 else f"{x['순자산_만원']:,}만", axis=1)
    
    return summary, portfolio, trend

d, df_p, df_t = get_data()

# [수정 1, 2] 헤더 및 부제목 수정
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🌳❤️")

# [수정 3] 탭 이름 변경
tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 ---
with tab1:
    st.subheader("📍 현재 위치 요약")
    c1, c2, c3 = st.columns(3)
    c1.metric("총 자산", f"{d['current_assets']:,.0f}원")
    c2.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    c3.metric("순자산", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}")
    
    st.divider()
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # [수정 4] 소유주별 색상 분기 및 금액/퍼센트 표시
        st.write("**투자 자산 구성 (소유주별)**")
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        
        # 금액과 퍼센트가 차트 안에 보이도록 설정
        fig_pie.update_traces(textinfo="label+percent root+value")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_right:
        # [수정 5] 최근 1년 단위 시계열 차트 및 만원 단위 고정 표시
        st.write("**순자산 성장 추이 (최근 1년)**")
        
        # 기간 선택 필터
        date_range = st.date_input("조회 기간 선택", 
                                   value=[df_t['날짜'].min(), df_t['날짜'].max()],
                                   min_value=df_t['날짜'].min(), 
                                   max_value=df_t['날짜'].max())
        
        filtered_t = df_t[(df_t['날짜'] >= pd.to_datetime(date_range[0])) & (df_t['날짜'] <= pd.to_datetime(date_range[1]))]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=filtered_t['날짜'], y=filtered_t['순자산_만원'],
            mode='lines+markers+text',
            text=filtered_t['라벨'],
            textposition="top center",
            line=dict(color='#FF4B4B', width=4),
            marker=dict(size=10)
        ))
        
        fig_line.update_layout(
            yaxis=dict(title="단위: 만원", range=[7000, filtered_t['순자산_만원'].max() * 1.2]),
            xaxis=dict(tickformat="%y.%m"),
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- [탭 2, 3은 이전 로직 유지하되 명칭만 변경됨] ---
with tab2:
    st.info("월별 수입/지출 상세 분석 페이지입니다.")

with tab3:
    st.success("남편/아내의 핵심 궁금증을 해결하는 전용 공간입니다.")
