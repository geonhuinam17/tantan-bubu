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
    
    /* 섹션 제목 스타일 */
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

    /* 메트릭 라벨 스타일 */
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #666 !important;
        margin-bottom: 10px !important;
    }

    /* [수정] 기간 선택 슬라이더 바 색상을 진한 회색으로 변경 */
    .stSlider [data-baseweb="slider"] > div:first-child {
        background: #6C757D !important;
    }
    .stSlider [data-baseweb="slider"] [data-testid="stTickBar"] {
        display: none;
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
    
    # 👸 왕비(분홍) / 🤴 왕(하늘) 포트폴리오
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
        months = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        start_m, end_m = st.select_slider("조회 월 범위 선택", options=months, value=(months[0], months[-1]))
        f_t = df_t[(df_t['날짜'] >= pd.to_datetime(start_m)) & (df_t['날짜'] <= pd.to_datetime(end_m))]
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=f_t['날짜'], y=f_t['순자산_만원'], mode='lines+markers+text',
            text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(f_t['순자산_만원'], f_t['증감'])],
            textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')
        ))
        fig_line.update_layout(
            yaxis=dict(range=[7000, f_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'),
            xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False),
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        # [수정] 중앙 노란색 배경 제거 및 투명 설정
        fig_pie.update_traces(textinfo="label+value+percent parent", insidetextorientation='horizontal')
        fig_pie.update_layout(
            margin=dict(t=0, l=0, r=0, b=0), 
            paper_bgcolor='rgba(0,0,0,0)',
            sunburstcolorway=["rgba(0,0,0,0)"] # 중앙 노드 색상 투명화
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# --- [탭 2] 월별 보기 ---
with tab2:
    st.markdown("<div class='section-title'>📆 이번 달 현금흐름 분석 (26.02 기준)</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("총 수입", f"{d['monthly_income']:,.0f}원")
    m2.metric("총 지출", f"{d['monthly_expense']:,.0f}원")
    savings_rate = (d['monthly_savings'] / d['monthly_income']) * 100
    m3.metric("저축률", f"{savings_rate:.1f}%", delta=f"{d['monthly_savings']:,.0f}원 저축")

    st.divider()
    
    st.markdown("<div class='section-title'>현금흐름 구조</div>", unsafe_allow_html=True)
    cf_data = pd.DataFrame({
        "구분": ["수입", "지출", "저축"],
        "금액": [d['monthly_income'], d['monthly_expense'], d['monthly_savings']]
    })
    fig_bar = px.bar(cf_data, x="구분", y="금액", color="구분", 
                     color_discrete_map={"수입": "#6C757D", "지출": "#FF69B4", "저축": "#5D4037"})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- [탭 3] 궁금증해결 ---
with tab3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    
    col_husband, col_wife = st.columns(2)
    
    with col_husband:
        # 남편이 가장 궁금해하는 것: 현금화 가능 자산
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        # 해외주식 + 가상화폐 + ISA 합계 (왕 데이터 기준)
        liquid_val = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|가상화폐|ISA'))]['금액'].sum()
        st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 30px; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); text-align: center;">
                <h1 style="color: #00BFFF; margin: 0;">₩ {liquid_val:,.0f}</h1>
                <p style="color: #666; margin-top: 10px;">지금 당장 현금화하여 사용할 수 있는 유동 자산입니다.</p>
            </div>
        """, unsafe_allow_html=True)

    with col_wife:
        # 아내가 가장 궁금해하는 것: 목표 달성률
        st.markdown("### 👸 왕비(건희) : 목표 달성 현황")
        net_increase = d['net_asset'] - d['base_net_asset']
        goal1 = 100000000 # 1억
        progress1 = min(net_increase / goal1, 1.0)
        
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {progress1*100:.1f}%**")
        st.progress(progress1)
        st.write(f"현재까지 순수하게 모은 돈: **{net_increase:,.0f}원**")
        
        if progress1 >= 1.0:
            st.balloons()
            st.success("🎉 축하합니다! 1차 목표인 1억 원을 달성했습니다!")
