import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (수정 절대 금지)
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

# 2. 데이터 세팅 (요청하신 지표를 위한 상세 데이터 시뮬레이션)
@st.cache_data(ttl=300)
def get_tantan_data():
    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
    }
    
    # [월별 데이터] 현금흐름 + 재무상태 + 투자성과
    monthly_flows = {
        "26.02": {
            "income_k": 6200000, "income_d": 5347372, "fixed_exp": 2253453, "var_exp": 3871895,
            "inv_amount_top": {"NVDA": 5000000, "ETH": 3200000, "BTC": 2500000, "XRP": 1200000, "AAPL": 800000},
            "inv_qty_top": {"XRP": 1500, "ETH": 0.5, "NVDA": 12, "BTC": 0.02, "TSLA": 5},
            "exp_categories": {"식비": 1200000, "육아용품": 1500000, "경조사": 600000, "교통/통신": 400000, "기타": 171895},
            "liquid_assets": 120000000, "non_liquid": 283641070, "asset_return": 1500000,
            "accounts": {"삼성증권": 85000000, "업비트": 45000000, "주택청약": 30000000, "CMA": 15000000, "현금": 5000000}
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
    
    return d, portfolio, trend_df, monthly_flows

d, df_p, df_t, m_flows = get_tantan_data()

# 헤더 (고정)
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
        m_list = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        cp = st.empty()
        sm, em = st.select_slider("📅 조회 범위", options=m_list, value=(m_list[0], m_list[-1]))
        ft = df_t[(df_t['날짜'] >= pd.to_datetime(sm)) & (df_t['날짜'] <= pd.to_datetime(em))]
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=ft['날짜'], y=ft['순자산_만원'], mode='lines+markers+text', text=[f"{v:,}만\n(+{z:,})" if z!=0 else f"{v:,}만" for v, z in zip(ft['순자산_만원'], ft['증감'])], textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')))
        fig_l.update_layout(yaxis=dict(range=[7000, ft['순자산_만원'].max()*1.15]), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        cp.plotly_chart(fig_l, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        os = df_p.groupby("소유주")["금액"].sum().reset_index()
        ti = os["금액"].sum()
        os = pd.concat([os, pd.DataFrame([{"소유주": "합계", "금액": ti}])], ignore_index=True)
        os.rename(columns={"소유주": "보관하는 사람"}, inplace=True)
        os["비중"] = (os["금액"]/ti*100).round(1).astype(str)+"%"
        os.loc[os["보관하는 사람"]=="합계","비중"]="100.0%"
        st.table(os.set_index("보관하는 사람"))
        fig_p = px.pie(df_p, names='항목', values='금액', color='항목', color_discrete_map={r['항목']: r['색상'] for _, r in df_p.iterrows()})
        fig_p.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>%{percent}<br>₩%{value:,.0f}", textposition="inside", insidetextorientation='horizontal')
        fig_p.update_layout(margin=dict(t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- [탭 2] 월별 보기 (요청 지표 100% 반영) ---
with tab2:
    sel_m = st.selectbox("분석 월 선택", options=list(m_flows.keys()), index=0)
    m = m_flows[sel_m]
    
    # 1. 핵심 요약 (4개)
    st.markdown("<div class='section-title'>💰 이번 달 현금흐름 요약</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    total_inc = m['income_k'] + m['income_d']
    total_exp = m['fixed_exp'] + m['var_exp']
    savings = total_inc - total_exp
    s_rate = (savings/total_inc)*100
    with c1: st.markdown(f"<div class='custom-card' style='height:140px'><div class='metric-label'>총 수입</div><div class='metric-value' style='font-size:20px'>{total_inc:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card' style='height:140px'><div class='metric-label'>총 지출</div><div class='metric-value' style='font-size:20px'>{total_exp:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card' style='height:140px'><div class='metric-label'>순 저축액</div><div class='metric-value' style='font-size:20px'>{savings:,.0f}원</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='custom-card' style='height:140px'><div class='metric-label'>저축률</div><div class='metric-value' style='font-size:20px; color:#FF1493'>{s_rate:.1f}%</div></div>", unsafe_allow_html=True)

    # 2. 투자 성과 (Top 5)
    st.divider()
    st.markdown("<div class='section-title'>📈 이번 달 투자 종목 성과 (Top 5)</div>", unsafe_allow_html=True)
    col_inv_l, col_inv_r = st.columns(2)
    with col_inv_l:
        st.write("**금액 기준 증가 Top 5**")
        fig_inv1 = px.bar(x=list(m['inv_amount_top'].keys()), y=list(m['inv_amount_top'].values()), color_discrete_sequence=['#2ECC71'])
        st.plotly_chart(fig_inv1, use_container_width=True)
    with col_inv_r:
        st.write("**수량 기준 증가 Top 5**")
        fig_inv2 = px.bar(x=list(m['inv_qty_top'].keys()), y=list(m['inv_qty_top'].values()), color_discrete_sequence=['#3498DB'])
        st.plotly_chart(fig_inv2, use_container_width=True)

    # 3. 상세 지출 분석
    st.divider()
    st.markdown("<div class='section-title'>🔍 상세 지출 및 수입 분석</div>", unsafe_allow_html=True)
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    with col_exp1:
        st.write("**고정비 vs 변동비 비중**")
        fig_e1 = px.pie(values=[m['fixed_exp'], m['var_exp']], names=['고정비', '변동비'], color_discrete_sequence=['#95A5A6', '#FF69B4'], hole=0.5)
        st.plotly_chart(fig_e1, use_container_width=True)
    with col_exp2:
        st.write("**수입 분담 비율 (👸 vs 🤴)**")
        fig_e2 = px.pie(values=[m['income_k'], m['income_d']], names=['건희(왕비)', '동현(왕)'], color_discrete_sequence=['#FF1493', '#8E44AD'])
        st.plotly_chart(fig_e2, use_container_width=True)
    with col_exp3:
        st.write("**지출 카테고리 Top 5**")
        fig_e3 = px.bar(x=list(m['exp_categories'].values()), y=list(m['exp_categories'].keys()), orientation='h', color_discrete_sequence=['#E74C3C'])
        st.plotly_chart(fig_e3, use_container_width=True)

    # 4. 재무상태 시트 기반 지표 (New)
    st.divider()
    st.markdown("<div class='section-title'>🧱 월말 재무 건전성 분석 (재무상태 시트 기반)</div>", unsafe_allow_html=True)
    
    

    col_st1, col_st2, col_st3 = st.columns(3)
    with col_st1:
        st.write("**자산-부채 밸런스 (LTV)**")
        ltv = (d['current_debt']/d['current_assets'])*100
        fig_st1 = go.Figure(go.Indicator(mode="gauge+number", value=ltv, title={'text': "부채 비중(%)"}, gauge={'bar':{'color':"#333"}}))
        fig_st1.update_layout(height=250)
        st.plotly_chart(fig_st1, use_container_width=True)
    with col_st2:
        st.write("**유동성 vs 비유동성 비중**")
        fig_st2 = px.pie(values=[m['liquid_assets'], m['non_liquid']], names=['유동자산', '비유동자산'], color_discrete_sequence=['#3498DB', '#BDC3C7'], hole=0.5)
        st.plotly_chart(fig_st2, use_container_width=True)
    with col_st3:
        st.write("**자산 수익 기여도 (저축 vs 투자수익)**")
        fig_st3 = px.pie(values=[savings, m['asset_return']], names=['이번달 저축', '투자 수익'], color_discrete_sequence=['#27AE60', '#F1C40F'])
        st.plotly_chart(fig_st3, use_container_width=True)

    st.write("**계좌별 잔액 Top 5**")
    fig_st4 = px.bar(x=list(m['accounts'].keys()), y=list(m['accounts'].values()), color=list(m['accounts'].keys()))
    st.plotly_chart(fig_st4, use_container_width=True)

# --- [탭 3] 궁금증해결 (오류 수정 완료) ---
with tab3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    ch, cw = st.columns(2)
    with ch:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        liq_total = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|ISA'))]['금액'].sum()
        st.markdown(f"<div class='custom-card' style='text-align:center; height:150px'><h1 style='color:#8E44AD; font-size:24px'>₩ {liq_total:,.0f}</h1><p>즉시 현금화 가능 자산</p></div>", unsafe_allow_html=True)
    with cw:
        st.markdown("### 👸 왕비(건희) : 목표 달성 현황")
        inc = d['net_asset'] - d['base_net_asset']
        prog = min(inc / 100000000, 1.0)
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {prog*100:.1f}%**")
        st.progress(prog)
