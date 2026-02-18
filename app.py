import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (수정 금지 영역)
st.set_page_config(page_title="탄탄부부 재정 대시보드", layout="wide")

st.markdown("""
    <style>
    @import url('https://webfontworld.github.io/kopub/KoPubWorldDotum.css');
    
    html, body, [class*="css"] {
        font-family: 'KoPubWorldDotum', sans-serif !important;
        background-color: #E9ECEF; 
    }
    
    .section-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #333333;
        margin-bottom: 15px;
    }

    .custom-card {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        height: 210px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
    }

    .metric-label { font-size: 16px; font-weight: 700; color: #666; margin-bottom: 8px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #000000 !important; }

    .growth-pill {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
        margin-top: 10px;
    }
    .pink-pill { background-color: #FFE4E1; color: #FF1493; }
    .blue-pill { background-color: #E0F2F1; color: #00796B; }

    div[data-testid="stSlider"], div[data-testid="stSlider"] > div {
        background-color: transparent !important;
        background: none !important;
        border: none !important;
    }
    .stSlider [data-baseweb="slider"] > div:first-child {
        background: #dee2e6 !important; 
    }
    .stSlider [data-baseweb="slider"] > div > div {
        background: #495057 !important; 
    }
    .stSlider [role="slider"] {
        background-color: #495057 !important;
        border: 2px solid #FFFFFF !important;
    }

    .stTable td, .stTable th, .stTable tr {
        color: #000000 !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    .stTable tr:last-child {
        background-color: #f8f9fa;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 세팅 (전체 현황 및 월별 데이터 통합)
@st.cache_data(ttl=300)
def get_tantan_data():
    # 전체 요약 데이터 (Tab 1용)
    summary = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
    }
    
    # 월별 현금흐름 데이터 (Tab 2용) 
    monthly_flows = {
        "26.02": {"income": 11547372, "fixed_exp": 2253453, "var_exp": 3871895, "total_exp": 6125348, "savings": 5422024},
        "26.01": {"income": 14506124, "fixed_exp": 2253453, "var_exp": 550000, "total_exp": 2803453, "savings": 11702671},
        "25.12": {"income": 9502747, "fixed_exp": 2269553, "var_exp": 452000, "total_exp": 2721553, "savings": 6781194},
        "25.11": {"income": 9525170, "fixed_exp": 2269553, "var_exp": 550000, "total_exp": 2819553, "savings": 6705617},
        "25.10": {"income": 9847331, "fixed_exp": 2269553, "var_exp": 2057460, "total_exp": 4327013, "savings": 5520318},
        "25.09": {"income": 9634784, "fixed_exp": 2269553, "var_exp": 1188000, "total_exp": 3457553, "savings": 6177231},
        "25.08": {"income": 7111200, "fixed_exp": 1015346, "var_exp": 1200000, "total_exp": 2215346, "savings": 4895854},
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
    
    trend_data = pd.DataFrame([
        {"날짜": "2025-08-01", "순자산": 75767585}, {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414}, {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717}, {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ])
    trend_data['날짜'] = pd.to_datetime(trend_data['날짜'])
    trend_data['순자산_만원'] = (trend_data['순자산'] / 10000).astype(int)
    trend_data['증감'] = trend_data['순자산_만원'].diff().fillna(0).astype(int)
    
    return summary, portfolio, trend_data, monthly_flows

d, df_p, df_t, flows = get_tantan_data()

# 헤더 (수정 금지 영역)
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 (절대 수정 없음) ---
with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='custom-card'><div class='metric-label'>총 자산</div><div class='metric-value'>{d['current_assets']:,.0f}원</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='custom-card'><div class='metric-label'>총 부채</div><div class='metric-value'>{d['current_debt']:,.0f}원</div></div>""", unsafe_allow_html=True)
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        pill_style = "pink-pill" if diff >= 0 else "blue-pill"
        arrow = "↑" if diff >= 0 else "↓"
        st.markdown(f"""
            <div class='custom-card'>
                <div class='metric-label'>순자산</div>
                <div class='metric-value'>{d['net_asset']:,.0f}원</div>
                <div><span class='growth-pill {pill_style}'>전월 대비 {abs(diff):,.0f}원 {arrow}</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        months_list = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        chart_placeholder = st.empty()
        start_m, end_m = st.select_slider("📅 조회 월 범위 선택", options=months_list, value=(months_list[0], months_list[-1]))
        f_t = df_t[(df_t['날짜'] >= pd.to_datetime(start_m)) & (df_t['날짜'] <= pd.to_datetime(end_m))]
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=f_t['날짜'], y=f_t['순자산_만원'], mode='lines+markers+text', text=[f"{v:,}만\n(+{z:,})" if z != 0 else f"{v:,}만" for v, z in zip(f_t['순자산_만원'], f_t['증감'])], textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')))
        fig_line.update_layout(yaxis=dict(range=[7000, f_t['순자산_만원'].max() * 1.15], showgrid=True, gridcolor='#E5E5E5'), xaxis=dict(tickformat="%y.%m", dtick="M1", showgrid=False), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        chart_placeholder.plotly_chart(fig_line, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        owner_summary = df_p.groupby("소유주")["금액"].sum().reset_index()
        total_inv = owner_summary["금액"].sum()
        total_row = pd.DataFrame([{"소유주": "합계", "금액": total_inv}])
        owner_summary = pd.concat([owner_summary, total_row], ignore_index=True)
        owner_summary.rename(columns={"소유주": "보관하는 사람"}, inplace=True)
        owner_summary["비중"] = (owner_summary["금액"] / total_inv * 100).round(1).astype(str) + "%"
        owner_summary.loc[owner_summary["보관하는 사람"] == "합계", "비중"] = "100.0%"
        owner_summary["금액(원)"] = owner_summary["금액"].apply(lambda x: f"{x:,.0f}")
        st.table(owner_summary[["보관하는 사람", "금액(원)", "비중"]].set_index("보관하는 사람"))
        fig_pie = px.pie(df_p, names='항목', values='금액', color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_pie.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>%{percent}<br>₩%{value:,.0f}", textposition="inside", insidetextorientation='horizontal')
        fig_pie.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- [탭 2] 월별 보기 (신규 구현 영역) ---
with tab2:
    st.markdown("<div class='section-title'>📅 월별 상세 현금흐름 분석</div>", unsafe_allow_html=True)
    
    # 월 선택 셀렉박스
    selected_month = st.selectbox("분석할 월을 선택하세요", options=list(flows.keys()), index=0)
    month_data = flows[selected_month]
    
    # 주요 지표 (3컬럼) 
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class='custom-card'><div class='metric-label'>총 수입</div><div class='metric-value'>{month_data['income']:,.0f}원</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='custom-card'><div class='metric-label'>총 지출 (생활비)</div><div class='metric-value'>{month_data['total_exp']:,.0f}원</div></div>""", unsafe_allow_html=True)
    with m3:
        s_rate = (month_data['savings'] / month_data['income']) * 100
        st.markdown(f"""<div class='custom-card'><div class='metric-label'>순 저축액 (저축률)</div><div class='metric-value'>{month_data['savings']:,.0f}원</div><div style='color:#FF1493; font-weight:700;'>({s_rate:.1f}%)</div></div>""", unsafe_allow_html=True)
    
    st.divider()
    
    # 상세 내역 분석 (좌: 지출 구조, 우: 수입/지출/저축 비중)
    col_flow_l, col_flow_r = st.columns([1, 1])
    
    with col_flow_l:
        st.markdown("<div class='section-title'>💳 지출 구성 분석</div>", unsafe_allow_html=True)
        exp_df = pd.DataFrame({
            "항목": ["고정 생활비", "변동 생활비"],
            "금액": [month_data['fixed_exp'], month_data['var_exp']]
        })
        fig_exp = px.bar(exp_df, x="항목", y="금액", text_auto=',.0f', color="항목",
                         color_discrete_map={"고정 생활비": "#6C757D", "변동 생활비": "#FF69B4"})
        fig_exp.update_layout(plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_exp, use_container_width=True)
        
    with col_flow_r:
        st.markdown("<div class='section-title'>💰 현금흐름 밸런스</div>", unsafe_allow_html=True)
        flow_df = pd.DataFrame({
            "구분": ["지출", "저축/투자"],
            "금액": [month_data['total_exp'], month_data['savings']]
        })
        fig_balance = px.pie(flow_df, names="구분", values="금액", hole=0.5,
                             color="구분", color_discrete_map={"지출": "#E74C3C", "저축/투자": "#2ECC71"})
        fig_balance.update_traces(textinfo="label+percent")
        fig_balance.update_layout(margin=dict(t=0, b=0), showlegend=False)
        st.plotly_chart(fig_balance, use_container_width=True)

# --- [탭 3] 궁금증해결 (기존 로직 유지) ---
with tab3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    col_h, col_w = st.columns(2)
    with col_h:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        liq = df_p[(df_p['소유주'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|가상화폐|ISA'))]['금액'].sum()
        st.markdown(f"<div class='custom-card' style='text-align:center;'><h1 style='color:#8E44AD;'>₩ {liq:,.0f}</h1><p>즉시 현금화 가능한 유동 자산</p></div>", unsafe_allow_html=True)
    with col_w:
        st.markdown("### 👸 왕비(건희) : 목표 달성 현황")
        net_inc = summary['net_asset'] - summary['base_net_asset']
        progress = min(net_inc / 100000000, 1.0)
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {progress*100:.1f}%**")
        st.progress(progress)
        st.write(f"현재까지 순수 증액분: **{net_inc:,.0f}원**")
