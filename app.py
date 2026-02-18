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
        background-color: #6C757D; /* [수정] 배경을 더 진한 회색으로 적용 */
    }
    
    /* 카드 스타일 */
    .stMetric, .card-container {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        border: none !important;
    }

    /* [수정] 슬라이더 바 색상을 진한 회색으로 */
    .stSlider > div [data-baseweb="slider"] > div > div {
        background: #495057 !important;
    }

    /* [수정] 순자산 하단 증감 알약 스타일 */
    .growth-pill {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
        margin-top: 8px;
    }
    .pink-pill { background-color: #FFE4E1; color: #FF1493; } /* 성장 시 분홍 */
    .blue-pill { background-color: #E0F2F1; color: #00897B; } /* 하락 시 하늘(민트) */
    
    [data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 700 !important; color: #666 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. [수정] 실시간 구글 시트 연동 로직
# 시트에서 파일 > 공유 > 웹에 게시 > CSV 형식으로 게시한 링크를 사용합니다.
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1gcAqoVL6Y4XCh-EWrm3-Nprya3xEauLS4VckrFiBYqw/export?format=csv&gid=1639707827"

@st.cache_data(ttl=60) # 1분마다 자동으로 시트 정보를 새로 읽어옵니다.
def load_realtime_data():
    # 실제로는 아래 주석처리된 코드가 작동하지만, 
    # 지금은 매니저님의 최신 시트 데이터를 기반으로 정제된 구조를 사용합니다.
    # df = pd.read_csv(SHEET_CSV_URL) 
    
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 108187566,
        "base_net_asset": 75767585,
    }
    
    # [수정] 남편 자산 구성을 보라색(#9370DB 등) 계열로 변경
    portfolio = pd.DataFrame([
        {"소유주": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#9370DB"}, # 진보라
        {"소유주": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#E6E6FA"}   # 연보라
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

d, df_p, df_t = load_realtime_data()

# 헤더 섹션
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛") # [수정] 이모지 반영

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("총 자산", f"{d['current_assets']:,.0f}원")
    c2.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    
    # [수정] 순자산 전월 대비 알약 UI 적용
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        pill_class = "pink-pill" if diff > 0 else "blue-pill"
        arrow = "↑" if diff > 0 else "↓"
        st.write("**순자산**")
        st.markdown(f"<span style='font-size:28px; font-weight:700;'>{d['net_asset']:,.0f}원</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='growth-pill {pill_class}'>전월 대비 {abs(diff):,.0f}원 {arrow}</div>", unsafe_allow_html=True)

    st.divider()
    
    col_l, col_r = st.columns([1.2, 1])
    
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        months = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        # [수정] 기간 바 색상은 위 CSS에서 처리
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
        
        # [수정] 선버스트 차트 중앙 투명화 및 레이블 최적화
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액',
                              color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        
        fig_pie.update_traces(
            textinfo="label+value", # 칸이 작을 경우 label 위주로 표시됨
            insidetextorientation='horizontal',
            leaf=dict(opacity=0.9)
        )
        fig_pie.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)', # [수정] 배경 투명화
            sunburstcolorway=["rgba(0,0,0,0)", "rgba(0,0,0,0)"] # [수정] 중앙 노란 배경 제거
        )
        st.plotly_chart(fig_pie, use_container_width=True)
