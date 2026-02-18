import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (KoPub 돋움체 반영)
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubWorldDotum.css');
    
    html, body, [class*="css"] {
        font-family: 'KoPubWorldDotum', sans-serif !important;
        background-color: #F4F7F9;
    }
    
    /* [수정] 체크 표시한 상단 3개 제목과 하단 차트 제목의 폰트 스타일 통일 */
    .section-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #333333;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }

    /* 카드 스타일 */
    .stMetric, .card-style {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
    }
    
    /* 메트릭 내부 라벨(제목) 숨기기 (커스텀 제목 사용을 위함) */
    [data-testid="stMetricLabel"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 세팅 (25.08 ~ 26.02 실제 데이터)
@st.cache_data(ttl=300)
def get_final_refined_data():
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 108187566,
        "base_net_asset": 75767585,
    }
    
    # [수정] 👸 왕비 / 🤴 왕 (분홍/하늘 톤)
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

d, df_p, df_t = get_final_refined_data()

# 헤더
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🌳❤️")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

with tab1:
    # [수정] 상단 3개 카드 제목 폰트 크기/굵기 통일
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown("<span style='font-size:16px; font-weight:700; color:#666;'>총 자산</span>", unsafe_allow_html=True)
        st.metric("", f"{d['current_assets']:,.0f}원")
    with c2: 
        st.markdown("<span style='font-size:16px; font-weight:700; color:#666;'>총 부채</span>", unsafe_allow_html=True)
        st.metric("", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    with c3: 
        st.markdown("<span style='font-size:16px; font-weight:700; color:#666;'>순자산</span>", unsafe_allow_html=True)
        st.metric("", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}원")

    st.divider()
    
    # [수정] 차트 순서 변경: 순자산 성장 추이가 왼쪽으로
    col_l, col_r = st.columns([1.2, 1])
    
    with col_l:
        # [수정] 제목에서 (만원 단위) 삭제 및 폰트 통일
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        
        # 기간 선택 필터
        start_date, end_date = st.date_input("조회 기간", [df_t['날짜'].min(), df_t['날짜'].max()])
        filtered_t = df_t[(df_t['날짜'] >= pd.to_datetime(start_date)) & (df_t['날짜'] <= pd.to_datetime(end_date))]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=filtered_t['날짜'], y=filtered_t['순자산_만원'],
            mode='lines+markers+text',
            text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(filtered_t['순자산_만원'], filtered_t['증감'])],
            textposition="top center",
            line=dict(color='#5D4037', width=4),
            marker=dict(size=12, color='#5D4037')
        ))
        fig_line.update_layout(
            yaxis=dict(range=[7000, filtered_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'),
            xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False),
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_r:
        # [수정] 투자자산 구성 폰트 통일
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        
        # [수정] 글자 잘림 방지: 작은 칸은 밖으로 빼서 표시하거나 hover 활용 최적화
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        
        fig_pie.update_traces(
            textinfo="label+percent", # 금액 대신 레이블+퍼센트 중심 (공간 확보)
            insidetextorientation='horizontal'
        )
        
        fig_pie.update_layout(
            # 글자 크기 최소값 설정 및 넘치는 글자 자동 처리
            uniformtext
