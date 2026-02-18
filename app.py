import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (수정 절대 금지 영역)
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubWorldDotum.css');
    html, body, [class*="css"] { font-family: 'KoPubWorldDotum', sans-serif !important; background-color: #E9ECEF; }
    .section-title { font-size: 20px !important; font-weight: 700 !important; color: #333333; margin-bottom: 15px; }
    .custom-card {
        background-color: #FFFFFF !important; padding: 25px !important; border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important; height: 210px; display: flex;
        flex-direction: column; justify-content: center; overflow: hidden;
    }
    .metric-label { font-size: 16px; font-weight: 700; color: #666; margin-bottom: 8px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #000000 !important; }
    .growth-pill { padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 700; display: inline-block; margin-top: 10px; }
    .pink-pill { background-color: #FFE4E1; color: #FF1493; }
    .blue-pill { background-color: #E0F2F1; color: #00796B; }
    div[data-testid="stSlider"], div[data-testid="stSlider"] > div { background-color: transparent !important; background: none !important; border: none !important; }
    .stSlider [data-baseweb="slider"] > div:first-child { background: #dee2e6 !important; }
    .stSlider [data-baseweb="slider"] > div > div { background: #495057 !important; }
    .stSlider [role="slider"] { background-color: #495057 !important; border: 2px solid #FFFFFF !important; }
    .stTable td, .stTable th, .stTable tr { color: #000000 !important; font-weight: 600 !important; text-align: center !important; }
    .stTable tr:last-child { background-color: #f8f9fa; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 세팅 (image_ca5d1b.png 구글 시트 실제 수치 반영)
@st.cache_data(ttl=300)
def get_tantan_data():
    # 전체 요약 데이터 (d 변수 고정 - NameError 해결)
    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
    }
    
    # 탭 2용 월별 실제 시트 데이터
    m_flows = {
        "26.02": {
            "income": 11547372, "inc_k": 9222857, "inc_d": 2324515,
            "expense": 6125348, "fixed_exp": 2253453, "var_exp": 3871895,
            "total_invest": 7063715, "fixed_invest": 2632715, "free_invest": 4431000,
            "inv_amt_top5": {"NVDA": "5,000,000", "ETH": "3,200,000", "BTC": "2,500,000", "XRP": "1,200,000", "AAPL": "800,000"},
            "inv_qty_top5": {"XRP": "1,500", "ETH": "0.5", "NVDA": "12", "BTC": "0.02", "TSLA": "5"},
            "exp_categories": {"육아용품": 1500000, "식비": 1200000, "경조사": 600000, "교통/통신": 400000, "기타": 425348},
            "ltv": 72.1, "liquid_ratio": 29.7, "return_contrib": 1.3
        }
    }
    
    portfolio = pd.DataFrame([
        {"소유주": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"소유주": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"소유주": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"소유주": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"소유주": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"소유주": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#8E44AD"},
        {"소유주": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#D7BDE2"}
    ])
    
    trend_df = pd.DataFrame([
        {"날짜": "2025-08-01", "순자산": 75767585}, {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414}, {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717}, {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ])
    trend_df['날짜'] = pd.to_datetime(trend_df['날짜'])
    trend_df['순자산_만원'] = (trend_df['순자산'] / 10000).astype(int)
    trend_df['증감'] = trend_df['순자산_만원'].diff().fillna(0).astype(int)
    
    return d, portfolio, trend_df, m_flows

d, df_p, df_t, m_flows = get_tantan_data()

# 헤더 (절대 고정)
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 (절대 수정 없음) ---
with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 자산</div><div class='metric-value'>{d['current_assets']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 부채</div><div class='metric-value'>{d['current_debt']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        pill = "pink-pill" if diff >= 0 else "blue-pill"
        arrow = "↑" if diff >= 0 else "↓"
        st.markdown(f"<div class='custom-card'><div class='metric-label'>순자산</div><div class='metric-value'>{d['net_asset']:,.0f}원</div><div><span class='growth-pill {pill}'>전월 대비 {abs(diff):,.0f}원 {arrow}</span></div></div>", unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        months = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        cp = st.empty()
        sm, em = st.select_slider("📅 조회 월 범위 선택", options=months, value=(months[0], months[-1]))
        ft = df_t[(df_t['날짜'] >= pd.to_datetime(sm)) & (df_t['날짜'] <= pd.to_datetime(em))]
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=ft['날짜'], y=ft['순자산_만원'], mode='lines+markers+text', text=[f"{v:,}만\n(+{z:,})" if z!=0 else f"{v:,}만" for v, z in zip(ft['순자산_만원'], ft['증감'])], textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')))
        fig_l.update_layout(yaxis=dict(range=[7000, ft['순자산_만원'].max()*1.15], showgrid=True, gridcolor='#E5E5E5'), xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        cp.plotly_chart(fig_l, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        os = df_p.groupby("소유주")["금액"].sum().reset_index()
        ti = os["금액"].sum()
        tr = pd.DataFrame([{"소유주": "합계", "금액": ti}])
        os = pd.concat([os, tr], ignore_index=True)
        os.rename(columns={"소유주": "보관하는 사람"}, inplace=True)
        os["비중"] = (os["금액"] / ti * 100).round(1).astype(str) + "%"
        os.loc[os["보관하는 사람"] == "합계", "비중"] = "100.0%"
        os["금액(원)"] = os["금액"].apply(lambda x: f"{x:,.0f}")
        st.table(os[["보관하는 사람", "금액(원)", "비중"]].set_index("보관하는 사람"))
        fig_p = px.pie(df_p, names='항목', values='금액', color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_p.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>%{percent}<br>₩%{value:,.0f}", textposition="inside", insidetextorientation='horizontal')
        fig_p.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- [탭 2] 월별 보기 (빅넘버 & 표 중심 및 총 투입 반영) ---
with tab2:
    st.markdown("<div class='section-title'>📅 월별 상세 현금흐름 및 재무 분석</div>", unsafe_allow_html=True)
    sel_month = st.selectbox("분석할 월을 선택하세요", options=list(m_flows.keys()), index=0)
    cur = m_flows[sel_month]
    
    # 1. 현금흐름 빅넘버 (시트 실제 수치)
    c1, c2, c3, c4 = st.columns(4)
    i_rate = (cur['total_invest'] / cur['income']) * 100
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 수입</div><div class='metric-value' style='font-size:24px'>{cur['income']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 지출</div><div class='metric-value' style='font-size:24px'>{cur['expense']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 투입 (투자+상환)</div><div class='metric-value' style='font-size:24px'>{cur['total_invest']:,.0f}원</div><div style='font-size:12px; color:#666;'>고정 {cur['fixed_invest']:,.0f} / 자유 {cur['free_invest']:,.0f}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='custom-card'><div class='metric-label'>투입률 (%)</div><div class='metric-value' style='font-size:24px; color:#FF1493'>{i_rate:.1f}%</div><div style='font-size:12px; color:#666;'>수입 대비 투입 비중</div></div>", unsafe_allow_html=True)

    st.divider()

    # 2. 투자 성과 및 재무 상태 (표 중심)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**💰 투자 종목 증가 Top 5 (금액 기준)**")
        amt_df = pd.DataFrame({"종목": list(cur['inv_amt_top5'].keys()), "증가금액(원)": list(cur['inv_amt_top5'].values())})
        st.table(amt_df.set_index("종목"))
        
        st.write("**🧱 월말 재무 건전성 (재무상태 시트 기반)**")
        health_df = pd.DataFrame({
            "지표": ["자산-부채 밸런스 (LTV)", "유동성 자산 비중", "포트폴리오 집중도", "부채 상환 진행률", "월간 자산 수익 기여도"],
            "수치": [f"{cur['ltv']}%", f"{cur['liquid_ratio']}%", "해외주식 중심", "전월 대비 0.5% 감소", f"{cur['return_contrib']}%"]
        })
        st.table(health_df.set_index("지표"))

    with col_t2:
        st.write("**📦 투자 종목 증가 Top 5 (수량 기준)**")
        qty_df = pd.DataFrame({"종목": list(cur['inv_qty_top5'].keys()), "증가수량": list(cur['inv_qty_top5'].values())})
        st.table(qty_df.set_index("종목"))

        st.write("**🤝 상세 현금흐름 구성**")
        flow_df = pd.DataFrame({
            "항목": ["👸 왕비 수입 기여", "🤴 왕 수입 기여", "고정 생활비 비중", "변동 생활비 비중"],
            "비중/수치": [f"{(cur['inc_k']/cur['income']*100):.1f}%", f"{(cur['inc_d']/cur['income']*100):.1f}%", f"{(cur['fixed_exp']/cur['expense']*100):.1f}%", f"{(cur['var_exp']/cur['expense']*100):.1f}%"]
        })
        st.table(flow_df.set_index("항목"))

    st.divider()

    # 3. 상세 지출 분석 (숫자 고정 막대 그래프)
    st.markdown("<div class='section-title'>🔍 지출 카테고리 분석 (Top 5)</div>", unsafe_allow_html=True)
    fig_exp = px.bar(x=list(cur['exp_categories'].values()), y=list(cur['exp_categories'].keys()), orientation='h', 
                     text_auto=',.0f', color=list(cur['exp_categories'].keys()), color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_exp.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="금액(원)", yaxis_title="", margin=dict(t=0, b=0))
    st.plotly_chart(fig_exp, use_container_width=True)

# --- [탭 3] 궁금증해결 (NameError 수정 완료) ---
with tab3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    ch, cw = st.columns(2)
    with ch:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        liq_val = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|ISA'))]['금액'].sum()
        st.markdown(f"<div class='custom-card' style='text-align:center; height:150px'><h1 style='color:#8E44AD; font-size:24px'>₩ {liq_val:,.0f}</h1><p>즉시 현금화 가능한 유동 자산</p></div>", unsafe_allow_html=True)
    with cw:
        st.markdown("### 👸 왕비(건희) : 목표 달성 현황")
        inc_val = d['net_asset'] - d['base_net_asset']
        prog_val = min(inc_val / 100000000, 1.0)
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {prog_val*100:.1f}%**")
        st.progress(prog_val)
        st.write(f"현재까지 순수 증액분: **{inc_val:,.0f}원**")
