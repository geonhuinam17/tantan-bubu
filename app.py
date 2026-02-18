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
        background-color: #E9ECEF; /* 진한 회색 배경 */
    }
    
    .section-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #333333;
        margin-bottom: 15px;
    }

    .stMetric {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
        height: 160px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #666 !important;
        margin-bottom: 10px !important;
    }

    /* [수정] 슬라이더 배경 삭제 및 '선' 색상만 진한 회색으로 고정 */
    div[data-testid="stSlider"] {
        background-color: transparent !important; /* 배경 삭제 */
        padding: 0px !important;
    }
    
    /* 슬라이더 트랙(선) 색상 수정 */
    .stSlider [data-baseweb="slider"] > div {
        background-color: #dee2e6 !important; /* 기본 선 (연회색) */
    }
    .stSlider [data-baseweb="slider"] > div > div {
        background-color: #495057 !important; /* 선택된 구간의 선 (진한 회색) */
    }
    
    /* 슬라이더 핸들(동그라미) 색상 */
    .stSlider [role="slider"] {
        background-color: #495057 !important;
        border: 2px solid #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 세팅
@st.cache_data(ttl=300)
def get_final_data():
    summary = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
        "monthly_income": 11547372, "monthly_expense": 6125348, "monthly_savings": 5422024
    }
    
    portfolio = pd.DataFrame([
        {"소유주": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#00BFFF"},
        {"소유주": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#87CEEB"}
    ])
    
    trend_data = [
        {"날짜": "2025-08-01", "순자산": 75767585}, {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414}, {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717}, {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ]
    df_t = pd.DataFrame(trend_data)
    df_t['날짜'] = pd.to_datetime(df_t['날짜'])
    df_t['순자산_만원'] = (df_t['순자산'] / 10000).astype(int)
    df_t['증감'] = df_t['순자산_만원'].diff().fillna(0).astype(int)
    return summary, portfolio, df_t

d, df_p, df_t = get_final_data()

st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 ---
with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("총 자산", f"{d['current_assets']:,.0f}원")
    c2.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    c3.metric("순자산", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}원")

    st.divider()
    
    col_l, col_r = st.columns([1.2, 1])
    
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        f_t_base = df_t.copy()
        months = f_t_base['날짜'].dt.strftime('%Y-%m').tolist()
        
        # 차트 영역
        chart_placeholder = st.empty()

        # [수정] 하단 슬라이더 배치 (배경은 투명, 선만 진회색)
        start_m, end_m = st.select_slider("📅 조회 월 범위 선택", options=months, value=(months[0], months[-1]))
        f_t = f_t_base[(f_t_base['날짜'] >= pd.to_datetime(start_m)) & (f_t_base['날짜'] <= pd.to_datetime(end_m))]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=f_t['날짜'], y=f_t['순자산_만원'], mode='markers+lines+text',
            text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(f_t['순자산_만원'], f_t['증감'])],
            textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')
        ))
        fig_line.update_layout(
            yaxis=dict(range=[7000, f_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'),
            xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False),
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0)
        )
        chart_placeholder.plotly_chart(fig_line, use_container_width=True)
        
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        
        # [수정] 왕/왕비 비중 요약 표
        owner_summary = df_p.groupby("소유주")["금액"].sum().reset_index()
        total_inv = owner_summary["금액"].sum()
        owner_summary["비중"] = (owner_summary["금액"] / total_inv * 100).round(1).astype(str) + "%"
        owner_summary["금액(원)"] = owner_summary["금액"].apply(lambda x: f"{x:,.0f}")
        
        st.table(owner_summary[["소유주", "금액(원)", "비중"]].set_index("소유주"))

        # 파이차트
        fig_pie = px.pie(df_p, names='항목', values='금액',
                         color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_pie.update_traces(textinfo="label+percent", textposition="inside")
        fig_pie.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# 탭 2 & 탭 3은 기존 기획대로 유지
with tab2:
    st.markdown("<div class='section-title'>📆 이번 달 현금흐름 분석</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("총 수입", f"{d['monthly_income']:,.0f}원")
    m2.metric("총 지출", f"{d['monthly_expense']:,.0f}원")
    m3.metric("저축률", f"{(d['monthly_savings'] / d['monthly_income'] * 100):.1f}%")

with tab3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    c_h, c_w = st.columns(2)
    with c_h:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        liq = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|가상화폐|ISA'))]['금액'].sum()
        st.markdown(f"<div style='background-color:#FFF; padding:30px; border-radius:20px; text-align:center;'><h1>₩ {liq:,.0f}</h1></div>", unsafe_allow_html=True)
