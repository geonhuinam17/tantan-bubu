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
        background-color: #6C757D !important; /* 확실한 진회색 배경 */
    }
    
    /* 섹션 제목 스타일 */
    .section-title { font-size: 20px; font-weight: 700; color: #333; margin-bottom: 15px; }

    /* 카드 스타일 */
    .stMetric, .card-container {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        border: none !important;
    }

    /* [수정 1] 기간 선택 바 '선'만 진한 회색으로 변경 */
    .stSlider [data-baseweb="slider"] > div:first-child {
        background-color: #495057 !important; /* 트랙 색상 */
    }
    .stSlider [data-baseweb="slider"] > div > div {
        background-color: #343A40 !important; /* 활성화된 선 색상 */
    }

    /* [수정 7] 순자산 증감 알약 스타일 */
    .growth-pill {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
        margin-top: 8px;
    }
    .pink-pill { background-color: #FFE4E1; color: #FF1493; } /* 성장 시 분홍 */
    .blue-pill { background-color: #E0F2F1; color: #00796B; } /* 하락 시 하늘(민트) */
    
    [data-testid="stMetricLabel"] { font-size: 16px; font-weight: 700; color: #666; }
    </style>
    """, unsafe_allow_html=True)

# 2. [수정] 구글 시트 실시간 연동 (CSV 게시 링크 활용)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1gcAqoVL6Y4XCh-EWrm3-Nprya3xEauLS4VckrFiBYqw/export?format=csv&gid=1639707827"

@st.cache_data(ttl=60) # 60초마다 데이터 새로고침
def load_data():
    # 실제 시트 연동 시: df = pd.read_csv(SHEET_CSV_URL)
    # 현재는 요청하신 기획안의 26.02 실제 데이터를 기반으로 로직을 구성합니다.
    summary = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
        "income": 11547372, "expense": 6125348, "savings": 5422024
    }
    
    # [수정 4] 남편(🤴 왕) 자산 -> 보라색 계열
    portfolio = pd.DataFrame([
        {"소유주": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#8E44AD"}, # 보라
        {"소유주": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#D7BDE2"}    # 연보라
    ])
    
    trend_data = [
        {"날짜": "2025-08", "순자산": 75767585}, {"날짜": "2025-09", "순자산": 84854400},
        {"날짜": "2025-10", "순자산": 91706414}, {"날짜": "2025-11", "순자산": 90894166},
        {"날짜": "2025-12", "순자산": 96985717}, {"날짜": "2026-01", "순자산": 108187566},
        {"날짜": "2026-02", "순자산": 112740391}
    ]
    df_t = pd.DataFrame(trend_data)
    df_t['순자산_만원'] = (df_t['순자산'] / 10000).astype(int)
    df_t['증감'] = df_t['순자산_만원'].diff().fillna(0).astype(int)
    return summary, portfolio, df_t

d, df_p, df_t = load_data()

st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("총 자산", f"{d['current_assets']:,.0f}원")
    c2.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    
    with c3:
        st.write("**순자산**")
        st.markdown(f"<span style='font-size:28px; font-weight:700;'>{d['net_asset']:,.0f}원</span>", unsafe_allow_html=True)
        diff = d['net_asset'] - d['last_month_net']
        pill_style = "pink-pill" if diff >= 0 else "blue-pill"
        arrow = "↑" if diff >= 0 else "↓"
        st.markdown(f"<div class='growth-pill {pill_style}'>전월 대비 {abs(diff):,.0f}원 {arrow}</div>", unsafe_allow_html=True)

    st.divider()
    
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        sel_m = st.select_slider("조회 월 범위 선택", options=df_t['날짜'].tolist(), value=(df_t['날짜'].iloc[0], df_t['날짜'].iloc[-1]))
        f_t = df_t[(df_t['날짜'] >= sel_m[0]) & (df_t['날짜'] <= sel_m[1])]
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=f_t['날짜'], y=f_t['순자산_만원'], mode='lines+markers+text',
            text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(f_t['순자산_만원'], f_t['증감'])],
            textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')
        ))
        fig_line.update_layout(yaxis=dict(range=[7000, f_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'),
                               xaxis=dict(showgrid=False), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        # [수정 2-3] 중앙 투명화 및 레이블 최적화
        fig_pie = px.sunburst(df_p, path=['소유주', '항목'], values='금액', color='항목',
                              color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_pie.update_traces(textinfo="label", insidetextorientation='horizontal') # 칸이 작을 땐 label만
        fig_pie.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)',
                              sunburstcolorway=["rgba(0,0,0,0)"]) # 중앙 투명 배경
        st.plotly_chart(fig_pie, use_container_width=True)

# 탭 2, 3 내용 채우기
with tab2:
    st.markdown("<div class='section-title'>📆 2026.02 현금흐름 분석</div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("총 수입", f"{d['income']:,.0f}원")
    m2.metric("총 지출", f"{d['expense']:,.0f}원")
    m3.metric("저축률", f"{(d['savings']/d['income']*100):.1f}%", delta=f"{d['savings']:,.0f}원 저축")
    cf_df = pd.DataFrame({"항목": ["수입", "지출", "저축"], "금액": [d['income'], d['expense'], d['savings']]})
    st.bar_chart(cf_df.set_index("항목"))

with tab3:
    st.markdown("<div class='section-title'>💡 궁금증 해결</div>", unsafe_allow_html=True)
    col_h, col_w = st.columns(2)
    with col_h:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        liq = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|ISA'))]['금액'].sum()
        st.markdown(f"<div class='card-container'><h2 style='color:#8E44AD;'>₩ {liq:,.0f}</h2><p>즉시 현금화 가능한 유동 자산 합계입니다.</p></div>", unsafe_allow_html=True)
    with col_w:
        st.markdown("### 👸 왕비(건희) : 목표 달성률")
        progress = (d['net_asset'] - d['base_net_asset']) / 100000000
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {progress*100:.1f}%**")
        st.progress(min(progress, 1.0))
