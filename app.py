import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 디자인 (핀테크 스타일)
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #f0f2f6; }
    .main { background-color: #f8f9fa; }
    div[data-testid="stExpander"] { border-radius: 16px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 (시트 연동 로직 - 예시 데이터 포함)
# 실제 운영 시 SHEET_URL에 본인의 CSV 익스포트 링크를 넣으시면 됩니다.
@st.cache_data(ttl=300)
def get_data():
    # 기획안에 명시된 핵심 수치들 (시트에서 계산되어 넘어온다고 가정)
    summary = {
        "current_assets": 403641070,
        "current_debt": 290900679,
        "net_asset": 112740391,
        "last_month_net": 105000000,
        "base_net_asset": 75760000, # 25년 8월 기준점
        "monthly_income": 11547372,
        "monthly_expense": 6125348,
        "monthly_savings": 5422024,
        "baby_prep_percent": 68
    }
    
    # 포트폴리오 데이터
    portfolio = pd.DataFrame({
        "항목": ["해외주식", "연금저축", "ISA", "가상화폐", "보험"],
        "금액": [66030000, 16800000, 10130000, 6100000, 3070000]
    })
    
    # 시계열 데이터 (연간관리 탭용)
    trend = pd.DataFrame({
        "월": ["25.08", "25.09", "25.10", "25.11", "25.12", "26.01", "26.02"],
        "순자산": [75760000, 82000000, 89000000, 95000000, 98000000, 105000000, 112740391]
    })
    
    return summary, portfolio, trend

d, df_p, df_t = get_data()

# 상단 타이틀
st.title("👏 탄탄부부 3-View 재정 대시보드")
st.caption("우리는 돈을 이해하고, 의사결정하는 시스템을 만든다.")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "❤️ 우리가 궁금한 것"])

# --- [탭 1] 전체 현황 ---
with tab1:
    st.subheader("📍 현재 위치 요약")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 자산", f"{d['current_assets']:,.0f}원")
    c2.metric("총 부채", f"- {d['current_debt']:,.0f}원", delta_color="inverse")
    c3.metric("순자산", f"{d['net_asset']:,.0f}원", delta=f"{d['net_asset']-d['last_month_net']:,.0f}")
    
    st.divider()
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.write("**투자 자산 구성**")
        fig_pie = px.pie(df_p, values='금액', names='항목', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_b:
        st.write("**순자산 성장 추이**")
        fig_line = px.line(df_t, x="월", y="순자산", markers=True)
        fig_line.update_traces(line_color='#FF4B4B', line_width=3)
        st.plotly_chart(fig_line, use_container_width=True)

# --- [탭 2] 월별 보기 ---
with tab2:
    st.selectbox("분석할 월 선택", ["2026.02", "2026.01", "2025.12"], index=0)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    savings_rate = (d['monthly_savings'] / d['monthly_income']) * 100
    
    # 저축률 색상 규칙 적용
    sr_color = "🟢" if savings_rate >= 30 else "🟡" if savings_rate >= 20 else "🔴"
    
    col_m1.metric("이번 달 수입", f"{d['monthly_income']:,.0f}원")
    col_m2.metric("이번 달 지출", f"{d['monthly_expense']:,.0f}원")
    col_m3.metric("저축률", f"{sr_color} {savings_rate:.1f}%")

    st.write("**수입/지출 구조**")
    cf_data = pd.DataFrame({
        "구분": ["수입", "지출", "저축"],
        "금액": [d['monthly_income'], d['monthly_expense'], d['monthly_savings']]
    })
    st.bar_chart(cf_data.set_index("구분"))

# --- [탭 3] 우리가 궁금한 것 ---
with tab3:
    # 👨 남편 챕터
    st.markdown("### 👨 남편 : 지금 당장 쓸 수 있는 돈")
    liquid_assets = df_p[df_p['항목'].isin(['해외주식', '가상화폐', 'ISA'])]['금액'].sum()
    
    c_liq = st.container()
    with c_liq:
        st.write(f"#### 💰 ₩ {liquid_assets:,.0f}")
        if liquid_assets >= 100000000:
            st.balloons()
            st.success("🎉 대단해요! 현금화 가능 자산이 1억을 돌파했습니다!")
        st.progress(min(liquid_assets / 100000000, 1.0))
        st.caption(f"전체 자산 중 {liquid_assets/d['current_assets']*100:.1f}%가 즉시 유동화 가능합니다.")

    st.divider()

    # 👩 아내 챕터
    st.markdown("### 👩 아내 : 목표 달성률 추적")
    net_growth = d['net_asset'] - d['base_net_asset']
    
    goal1 = 100000000 # 1억
    goal2 = 300000000 # 3억
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("**🎯 1차 목표 (+1억)**")
        g1_p = min(net_growth / goal1, 1.0)
        st.metric("달성률", f"{g1_p*100:.1f}%")
        st.progress(g1_p)
        st.caption(f"남은 금액: {max(goal1 - net_growth, 0):,.0f}원")

    with col_g2:
        st.write("**🎯 2차 목표 (+3억)**")
        g2_p = min(net_growth / goal2, 1.0)
        st.metric("달성률", f"{g2_p*100:.1f}%")
        st.progress(g2_p)
        st.caption(f"남은 금액: {max(goal2 - net_growth, 0):,.0f}원")

    # 성취 시스템 (배지)
    st.write("**🏆 탄탄부부 성취 기록**")
    badges = []
    if g1_p >= 0.25: badges.append("🌱 25% 달성")
    if g1_p >= 0.50: badges.append("🌿 50% 달성")
    if g1_p >= 0.75: badges.append("🌳 75% 달성")
    if g1_p >= 1.00: badges.append("🎆 1차 목표 완수!")
    st.write(" | ".join(badges))
    
    st.info(f"👶 **사랑이** 탄생까지 약 { (datetime(2026,3,24) - datetime.now()).days }일 남았습니다! (현재 준비 {d['baby_prep_percent']}%)")
