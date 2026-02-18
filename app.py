import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (전체 현황 보존을 위해 수정 금지)
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
    .sub-text { font-size: 12px; color: #666; font-weight: 500; margin-top: 5px; }

    .growth-pill { padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 700; display: inline-block; margin-top: 10px; }
    .pink-pill { background-color: #FFE4E1; color: #FF1493; }

    /* 슬라이더 스타일 */
    div[data-testid="stSlider"], div[data-testid="stSlider"] > div { background-color: transparent !important; background: none !important; border: none !important; }
    .stSlider [data-baseweb="slider"] > div:first-child { background: #dee2e6 !important; }
    .stSlider [data-baseweb="slider"] > div > div { background: #495057 !important; }
    .stSlider [role="slider"] { background-color: #495057 !important; border: 2px solid #FFFFFF !important; }

    /* [수정] 표 스타일: 헤더만 연회색, 나머지는 흰색 */
    .stTable thead tr th { background-color: #F8F9FA !important; color: #000000 !important; font-weight: 700 !important; text-align: center !important; border-bottom: 2px solid #dee2e6 !important; }
    .stTable tbody tr td { color: #000000 !important; font-weight: 500 !important; text-align: center !important; background-color: #FFFFFF !important; border-bottom: 1px solid #f1f1f1 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 연동 로직 (KeyError, ImportError 방지)
SHEET_ID = "1gcAqoVL6Y4XCh-EWrm3-Nprya3xEauLS4VckrFiBYqw"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=60)
def load_and_sync_data():
    try:
        all_sheets = pd.read_excel(EXCEL_URL, sheet_name=None, engine='openpyxl')
        sheet_names = list(all_sheets.keys())
        # 26년도 월 시트 추출 (26.01, 26.02...)
        months = sorted(list(set([re.search(r'26\.\d{2}', s).group() for s in sheet_names if re.search(r'26\.\d{2}', s)])), reverse=True)
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}. requirements.txt에 openpyxl이 있는지 확인해주세요.")
        return None, None, None, ["26.02"], {}

    # [탭 1 고정 데이터] d 변수로 통일하여 NameError 방지
    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
    }
    
    portfolio_data = [
        {"보관하는 사람": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493"},
        {"보관하는 사람": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4"},
        {"보관하는 사람": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1"},
        {"보관하는 사람": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB"},
        {"보관하는 사람": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1"},
        {"보관하는 사람": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#8E44AD"},
        {"보관하는 사람": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#D7BDE2"}
    ]
    df_p = pd.DataFrame(portfolio_data)
    
    trend_df = pd.DataFrame([
        {"날짜": "2025-08-01", "순자산": 75767585}, {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414}, {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717}, {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ])
    trend_df['날짜'] = pd.to_datetime(trend_df['날짜'])
    trend_df['순자산_만원'] = (trend_df['순자산'] / 10000).astype(int)
    trend_df['증감'] = trend_df['순자산_만원'].diff().fillna(0).astype(int)
    
    return d, df_p, trend_df, months, all_sheets

d, df_p, df_t, available_months, raw_data = load_and_sync_data()

# 헤더
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

t1, t2, t3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 (절대 보존 및 KeyError 해결) ---
with t1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 자산</div><div class='metric-value'>{d['current_assets']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 부채</div><div class='metric-value'>{d['current_debt']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        st.markdown(f"<div class='custom-card'><div class='metric-label'>순자산</div><div class='metric-value'>{d['net_asset']:,.0f}원</div><div><span class='growth-pill pink-pill'>전월 대비 {abs(diff):,.0f}원 ↑</span></div></div>", unsafe_allow_html=True)
    st.divider()
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        m_list = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        sm, em = st.select_slider("📅 조회 월 범위 선택", options=m_list, value=(m_list[0], m_list[-1]), key="slider_t1")
        ft = df_t[(df_t['날짜'] >= pd.to_datetime(sm)) & (df_t['날짜'] <= pd.to_datetime(em))]
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=ft['날짜'], y=ft['순자산_만원'], mode='lines+markers+text', text=[f"{v:,}만\n(+{z:,})" if z!=0 else f"{v:,}만" for v, z in zip(ft['순자산_만원'], ft['증감'])], textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')))
        fig_l.update_layout(yaxis=dict(range=[7000, ft['순자산_만원'].max()*1.15], showgrid=True), xaxis=dict(tickformat="%y.%m", showgrid=False), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        st.plotly_chart(fig_l, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        # [해결] KeyError: os 가공 시 컬럼명 매칭
        os = df_p.groupby("보관하는 사람")["금액"].sum().reset_index()
        ti = os["금액"].sum()
        os = pd.concat([os, pd.DataFrame([{"보관하는 사람": "합계", "금액": ti}])], ignore_index=True)
        os["비중"] = (os["금액"] / ti * 100).round(1).astype(str) + "%"
        os.loc[os["보관하는 사람"] == "합계", "비중"] = "100.0%"
        os["금액(원)"] = os["금액"].apply(lambda x: f"{x:,.0f}")
        st.table(os[["보관하는 사람", "금액(원)", "비중"]].set_index("보관하는 사람"))
        fig_p = px.pie(df_p, names='항목', values='금액', color='항목', color_discrete_map={row['항목']: row['색상'] for _, row in df_p.iterrows()})
        fig_p.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>%{percent}<br>₩%{value:,.0f}", textposition="inside", insidetextorientation='horizontal')
        fig_p.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- [탭 2] 월별 보기 (요청 사항 반영 및 자동화) ---
with t2:
    st.markdown("<div class='section-title'>📅 월별 상세 분석 (26년 이후)</div>", unsafe_allow_html=True)
    sel_month = st.selectbox("분석할 월을 선택하세요", options=available_months, index=0)
    
    # 26.02 실제 시트 수치 (image_ca689d, image_ca5d1b 참고)
    cur = {
        "income": 11547372, "fixed_inc": 6080000, "var_inc": 5467372,
        "expense": 6125348, "fixed_exp": 2253453, "var_exp": 3871895,
        "total_cont": 7063715, "fixed_cont": 2632715, "free_cont": 4431000
    }

    # 1. 빅넘버 (부가설명 추가)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 수입</div><div class='metric-value' style='font-size:24px'>{cur['income']:,.0f}원</div><div class='sub-text'>고정 {cur['fixed_inc']:,.0f} / 변동 {cur['var_inc']:,.0f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 지출</div><div class='metric-value' style='font-size:24px'>{cur['expense']:,.0f}원</div><div class='sub-text'>고정 {cur['fixed_exp']:,.0f} / 변동 {cur['var_exp']:,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 투입 (투자+상환)</div><div class='metric-value' style='font-size:24px'>{cur['total_cont']:,.0f}원</div><div class='sub-text'>고정 {cur['fixed_cont']:,.0f} / 자유 {cur['free_cont']:,.0f}</div></div>", unsafe_allow_html=True)

    st.divider()

    # 2. 투자 성과 Top 5 (디자인: 헤더만 회색)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**💰 투자 종목 증가 Top 5 (금액 기준)**") #
        amt_df = pd.DataFrame({"종목": ["GOOGL", "SCHD", "TIGER 미국배당", "ETH", "XRP"], "증가금액(원)": ["1,561,671", "874,183", "539,175", "505,594", "400,701"]})
        st.table(amt_df.set_index("종목"))
    with col_t2:
        st.write("**📦 투자 종목 증가 Top 5 (수량 기준)**") #
        qty_df = pd.DataFrame({"종목": ["XRP", "SCHD", "GOOGL", "TIGER 미국배당", "Tesla"], "증가수량": ["187", "81", "5", "5", "1"]})
        st.table(qty_df.set_index("종목"))

    st.divider()

    # 3. 재무상태 시트 A~J열 그대로 옮기기
    st.markdown(f"<div class='section-title'>🧱 {sel_month}. 재무상태 상세 내역 (A~J열)</div>", unsafe_allow_html=True)
    status_sheet = f"{sel_month}. 재무상태"
    if status_sheet in raw_data:
        # A~J열 추출 (iloc[:, 0:10])
        st.table(raw_data[status_sheet].iloc[:, 0:10].fillna("-"))
    else:
        st.info(f"'{status_sheet}' 시트를 준비 중입니다.")

# --- [탭 3] 궁금증해결 (NameError 해결) ---
with t3:
    st.markdown("<div class='section-title'>💡 부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    ch, cw = st.columns(2)
    with ch:
        st.markdown("### 🤴 왕(동현) : 당장 쓸 수 있는 돈")
        # [해결] df_p 컬럼명 보관하는 사람 매칭
        liq = df_p[(df_p['보관하는 사람'] == "🤴 왕") & (df_p['항목'].str.contains('해외주식|ISA'))]['금액'].sum()
        st.markdown(f"<div class='custom-card' style='text-align:center; height:150px'><h1 style='color:#8E44AD; font-size:24px'>₩ {liq:,.0f}</h1><p>즉시 현금화 가능 자산</p></div>", unsafe_allow_html=True)
    with cw:
        st.markdown("### 👸 왕비(건희) : 목표 달성 현황")
        # [해결] NameError: summary -> d 로 수정
        net_inc = d['net_asset'] - d['base_net_asset']
        st.write(f"**🎯 1차 목표 (+1억) 달성률: {(net_inc/100000000)*100:.1f}%**")
        st.progress(min(net_inc / 100000000, 1.0))
