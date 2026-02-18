import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 UI 스타일링
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubWorldDotum.css');
    
    html, body, [class*="css"] {
        font-family: 'KoPubWorldDotum', sans-serif !important;
        background-color: #F4F7F9; /* 연한 회색 배경 */
    }
    
    /* 카드 스타일: 하얀색 배경 + 둥근 모서리 + 그림자 */
    .stMetric, .card-style {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    /* 상단 요약 카드 높이 통일 */
    [data-testid="stMetric"] {
        height: 160px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 실제 데이터 (25.08 ~ 26.02)
@st.cache_data(ttl=300)
def get_verified_data():
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 108187566,
        "base_net_asset": 75767585,
        "monthly_income": 11547372,
        "monthly_expense": 6125348,
        "monthly_savings": 5422024,
    }
    
    # [수정] 👸 건희 / 🤴 동현 자산 (연두색 제거, 분홍/하늘 톤)
    portfolio = pd.DataFrame([
        {"소유주": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#00BFFF"},
        {"소유주": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#87CEEB"}
    ])
    
    # [수정] 실제 월별 순자산 데이터 (X축 날짜 포맷 최적화)
    trend_data = [
        {"날짜": "2025-08-01", "순자산": 75767585},
        {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414},
        {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717},
        {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ]
    df_t = pd.DataFrame(trend_data)
    df_t['날짜'] = pd.to_datetime(df_t['날짜'])
    df_t['순자산_만원'] = (df_t['순자산'] / 10000).astype(int)
    df_t['증감'] = df_t['순자산_만원'].diff().fillna(0).astype(int)
    return summary, portfolio, df_t

d, df_p, df_t = get_verified_data()

# 헤더
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🌳❤️")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

with tab1:
    st.subheader("📍 현재 위치 요약")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("총 자산", f"{d['current_assets']:,.0f}원")
    with c2: st.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    with c3: st.metric("순자산", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}원")

    st.divider()
    
    col_l, col_r = st.columns([1, 1.2])
    
    with col_l:
        st.write("**투자 자산 구성 (👸👸🤴🤴)**")
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_pie.update_traces(textinfo="label+percent root+value", insidetextorientation='horizontal')
        fig_pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_r:
        # [핵심 수정] 진한 갈색 그래프 + 기간 선택
        st.write("**순자산 성장 추이 (만원 단위)**")
        
        # 기간 선택 필터 (최근 1년 기본)
        start_date, end_date = st.date_input("조회 기간 선택", 
                                            [df_t['날짜'].min(), df_t['날짜'].max()],
                                            min_value=df_t['날짜'].min(),
                                            max_value=df_t['날짜'].max())
        
        filtered_t = df_t[(df_t['날짜'] >= pd.to_datetime(start_date)) & (df_t['날짜'] <= pd.to_datetime(end_date))]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=filtered_t['날짜'], y=filtered_t['순자산_만원'],
            mode='lines+markers+text',
            text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(filtered_t['순자산_만원'], filtered_t['증감'])],
            textposition="top center",
            line=dict(color='#5D4037', width=4), # 진한 갈색 적용
            marker=dict(size=12, color='#5D4037', symbol='circle')
        ))
        
        fig_line.update_layout(
            yaxis=dict(title="단위: 만원", range=[7000, filtered_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'),
            xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False), # 매월 표시
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)

# 탭 2, 3 로직 (기존 기획 유지)
with tab2:
    st.subheader("📆 이번 달 현금흐름 요약")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("이번 달 수입", f"{d['monthly_income']:,.0f}원")
    col_m2.metric("이번 달 지출", f"{d['monthly_expense']:,.0f}원")
    col_m3.metric("저축률", f"{(d['monthly_savings']/d['monthly_income']*100):.1f}%")

with tab3:
    st.subheader("💡 궁금증해결 전용 섹션")
    st.markdown("### 🤴 왕(동현) : 즉시 현금화 가능 자산")
    liquid = df_p[df_p['소유주'] == "🤴 왕"]['금액'].sum()
    st.markdown(f"<div class='card-style'><h2>💰 ₩ {liquid:,.0f}</h2><p>지금 당장 쓸 수 있는 소중한 비상금입니다.</p></div>", unsafe_allow_html=True)
