import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 KoPub 돋움체/고급 UI 스타일링
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    /* KoPub World 돋움체 웹폰트 로드 */
    @import url('https://webfontworld.github.io/kopub/KoPubWorldDotum.css');
    
    html, body, [class*="css"] {
        font-family: 'KoPubWorldDotum', sans-serif !important;
        background-color: #F4F7F9; /* 서비스 느낌의 연한 회색 배경 */
    }
    
    /* 카드 스타일 커스텀 */
    .stMetric, .card-style {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
        height: 180px; /* 요약 카드 높이 통일 */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 탭 디자인 수정 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 0 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 실제 데이터셋 (26.02 기준)
@st.cache_data(ttl=300)
def get_final_data():
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 108187566,
        "base_net_asset": 75767585,
        "monthly_income": 11547372,
        "monthly_expense": 6125348,
        "monthly_savings": 5422024,
        "baby_prep_percent": 68
    }
    
    # [수정 2, 4] 왕/왕비 이모지 및 색상/글씨 커스텀
    portfolio = pd.DataFrame([
        {"소유주": "👸 건희", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 건희", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 건희", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 건희", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 건희", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 동현", "항목": "해외주식 ", "금액": 34809457, "색상": "#00BFFF"},
        {"소유주": "🤴 동현", "항목": "ISA ", "금액": 1480945, "색상": "#87CEEB"}
    ])
    
    # [수정 5] 만원 단위 트렌드 데이터
    trend_data = [
        {"날짜": "25.08", "순자산": 75767585},
        {"날짜": "25.09", "순자산": 84854400},
        {"날짜": "25.10", "순자산": 91706414},
        {"날짜": "25.11", "순자산": 90894166},
        {"날짜": "25.12", "순자산": 96985717},
        {"날짜": "26.01", "순자산": 108187566},
        {"날짜": "26.02", "순자산": 112740391}
    ]
    df_t = pd.DataFrame(trend_data)
    df_t['순자산_만원'] = (df_t['순자산'] / 10000).astype(int)
    df_t['증감'] = df_t['순자산_만원'].diff().fillna(0).astype(int)
    return summary, portfolio, df_t

d, df_p, df_t = get_final_data()

# [수정 1, 2] 헤더 섹션
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🌳❤️")

# [수정 3] 탭 이름 변경
tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 ---
with tab1:
    # [수정 1] 카드 높이 통일 및 요약
    st.subheader("📍 현재 위치 요약")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("총 자산", f"{d['current_assets']:,.0f}원")
    with c2: st.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    with c3: st.metric("순자산", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}원")

    st.divider()
    
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        # [수정 4] 자산 구성: 색상 고정, 글씨 수평, 크기 고정
        st.write("**투자 자산 구성 (👸🤴)**")
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_pie.update_traces(
            textinfo="label+percent root+value",
            insidetextorientation='horizontal' # 글씨 기울기 고정
        )
        fig_pie.update_layout(
            uniformtext_minsize=12, uniformtext_mode='hide', # 글씨 크기 균일화
            margin=dict(t=0, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_right:
        # [수정 5] 만원 단위 추이: 70M 시작, 수치 고정
        st.write("**순자산 성장 추이 (만원 단위)**")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_t['날짜'], y=df_t['순자산_만원'],
            mode='lines+markers+text',
            text=[f"{v:,}만\n(+{d:,})" if d > 0 else f"{v:,}만" for v, d in zip(df_t['순자산_만원'], df_t['증감'])],
            textposition="top center",
            line=dict(color='#FF4B4B', width=4),
            marker=dict(size=12, color='#FF4B4B')
        ))
        fig_line.update_layout(
            yaxis=dict(title="단위: 만원", range=[7000, df_t['순자산_만원'].max() * 1.1]),
            xaxis=dict(showgrid=False),
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)

# --- [탭 2] 월별 보기 ---
with tab2:
    st.subheader("📆 월별 수입 및 지출 분석")
    m1, m2, m3 = st.columns(3)
    m1.metric("이번 달 수입", f"{d['monthly_income']:,.0f}원")
    m2.metric("이번 달 지출", f"{d['monthly_expense']:,.0f}원")
    m3.metric("저축률", f"{(d['monthly_savings']/d['monthly_income']*100):.1f}%")
    
    st.write("**현금흐름 구조**")
    cf_df = pd.DataFrame({"항목": ["수입", "지출", "저축"], "금액": [d['monthly_income'], d['monthly_expense'], d['monthly_savings']]})
    st.bar_chart(cf_df.set_index("항목"))

# --- [탭 3] 궁금증해결 ---
with tab3:
    st.subheader("💡 궁금증해결 전용 공간")
    # 남편 섹션
    st.markdown("### 🤴 동현 : 당장 쓸 수 있는 돈")
    liquid = df_p[df_p['소유주'] == "🤴 동현"]['금액'].sum()
    st.markdown(f"<div class='card-style'><h2>💰 ₩ {liquid:,.0f}</h2><p>남편 계좌 내 유동 자산 합계입니다.</p></div>", unsafe_allow_html=True)
    
    st.divider()
    
    # 아내 섹션
    st.markdown("### 👸 건희 : 목표 달성률")
    growth = d['net_asset'] - d['base_net_asset']
    p1 = min(growth / 100000000, 1.0)
    st.write(f"**🎯 1차 목표 (+1억) 달성률: {p1*100:.1f}%**")
    st.progress(p1)
    st.info(f"👶 사랑이 탄생일까지 자산 목표를 향해 달리고 있어요! (D-34)")
