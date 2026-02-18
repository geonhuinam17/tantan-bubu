import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# 1. 페이지 설정 및 프리미엄 UI 스타일링 (전체 현황 보존)
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
    .metric-value { font-size: 24px; font-weight: 700; color: #000000 !important; }
    .sub-text { font-size: 12px; color: #666; font-weight: 500; margin-top: 5px; }
    .highlight-text { color: #FF1493; font-weight: 800; }

    .growth-pill { padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 700; display: inline-block; margin-top: 10px; background-color: #FFE4E1; color: #FF1493; }

    /* 슬라이더 스타일 */
    div[data-testid="stSlider"], div[data-testid="stSlider"] > div { background-color: transparent !important; background: none !important; border: none !important; }
    .stSlider [data-baseweb="slider"] > div:first-child { background: #dee2e6 !important; }
    .stSlider [data-baseweb="slider"] > div > div { background: #495057 !important; }
    .stSlider [role="slider"] { background-color: #495057 !important; border: 2px solid #FFFFFF !important; }

    /* 표 스타일: 헤더만 연회색 */
    .stTable thead tr th { background-color: #F8F9FA !important; color: #000000 !important; font-weight: 700 !important; text-align: center !important; }
    .stTable tbody tr td { color: #000000 !important; font-weight: 500 !important; text-align: center !important; background-color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 연동 로직
SHEET_ID = "1gcAqoVL6Y4XCh-EWrm3-Nprya3xEauLS4VckrFiBYqw"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=60)
def load_all_tantan_data():
    try:
        all_sheets = pd.read_excel(EXCEL_URL, sheet_name=None, engine='openpyxl')
        s_names = list(all_sheets.keys())
        # [수정] 26.2. 같은 한 자리 월 인식 Regex
        available_m = sorted(list(set([re.findall(r'(26\.\d{1,2})\.', s)[0] for s in s_names if re.findall(r'(26\.\d{1,2})\.', s)])), key=lambda x: float(x), reverse=True)
    except:
        all_sheets, available_m = {}, ["26.2"]

    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
        "avg_monthly_inc": 6391299 
    }
    
    df_p_main = pd.DataFrame([
        {"보관하는 사람": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4", "유동성": False},
        {"보관하는 사람": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "보험", "금액": 3074500, "색상": "#FFE4E1", "유동성": False},
        {"보관하는 사람": "🤴 왕", "항목": "해외주식 ", "금액": 34809457, "색상": "#8E44AD", "유동성": True},
        {"보관하는 사람": "🤴 왕", "항목": "ISA ", "금액": 1480945, "색상": "#D7BDE2", "유동성": True}
    ])
    
    df_t = pd.DataFrame([
        {"날짜": "2025-08-01", "순자산": 75767585}, {"날짜": "2025-09-01", "순자산": 84854400},
        {"날짜": "2025-10-01", "순자산": 91706414}, {"날짜": "2025-11-01", "순자산": 90894166},
        {"날짜": "2025-12-01", "순자산": 96985717}, {"날짜": "2026-01-01", "순자산": 108187566},
        {"날짜": "2026-02-01", "순자산": 112740391}
    ])
    df_t['날짜'] = pd.to_datetime(df_t['날짜'])
    df_t['순자산_만원'] = (df_t['순자산'] / 10000).astype(int)
    df_t['증감'] = df_t['순자산_만원'].diff().fillna(0).astype(int)
    
    return d, df_p_main, df_t, available_m, all_sheets

d, df_p, df_t, available_months, raw_sheets = load_all_tantan_data()

# [스타일링 함수] F~I열 정수 및 천 단위 콤마 적용
def style_financial_sheet(df):
    df = df.replace(".", "").fillna("")
    num_cols = df.columns[3:10] # D~J열
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    def apply_row_style(row):
        cat = str(row.iloc[0]) # A열: 구분
        sub_cat = str(row.iloc[1]) # B열: 세부 항목
        if cat in ['자산', '부채', '순자산'] and sub_cat == "":
            return ['background-color: #333333; color: white; font-weight: 800'] * len(row)
        elif sub_cat in ['유동 자산', '투자 자산', '비유동 자산', '단기 부채', '장기 부채']:
            return ['background-color: #E9ECEF; color: black; font-weight: 700'] * len(row)
        elif cat == '자산' and sub_cat != "":
            return ['background-color: #F8F9FA; color: black'] * len(row)
        return ['background-color: white; color: black'] * len(row)

    return df.style.apply(apply_row_style, axis=1).format({
        df.columns[3]: "{:,.0f}", df.columns[4]: "{:,.0f}", df.columns[5]: "{:,.0f}",
        df.columns[6]: "{:,.0f}", df.columns[7]: "{:,.0f}", df.columns[8]: "{:,.0f}",
        df.columns[9]: "{:,.1f}"
    })

# --- [Header] 대시보드 정체성 ---
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

tab1, tab2, tab3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 (완벽 보존) ---
with tab1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 자산</div><div class='metric-value'>{d['current_assets']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 부채</div><div class='metric-value'>{d['current_debt']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        st.markdown(f"<div class='custom-card'><div class='metric-label'>순자산</div><div class='metric-value'>{d['net_asset']:,.0f}원</div><div><span class='growth-pill'>전월 대비 {abs(diff):,.0f}원 ↑</span></div></div>", unsafe_allow_html=True)
    st.divider()
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        m_list = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        sm, em = st.select_slider("📅 조회 월 범위 선택", options=m_list, value=(m_list[0], m_list[-1]), key="s_main")
        ft = df_t[(df_t['날짜'] >= pd.to_datetime(sm)) & (df_t['날짜'] <= pd.to_datetime(em))]
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=ft['날짜'], y=ft['순자산_만원'], mode='lines+markers+text', text=[f"{v:,}만\n(+{z:,})" if z!=0 else f"{v:,}만" for v, z in zip(ft['순자산_만원'], ft['증감'])], textposition="top center", line=dict(color='#5D4037', width=4), marker=dict(size=12, color='#5D4037')))
        fig_l.update_layout(yaxis=dict(range=[7000, ft['순자산_만원'].max()*1.15]), xaxis=dict(tickformat="%y.%m"), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        st.plotly_chart(fig_l, use_container_width=True)
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        os = df_p.groupby("보관하는 사람")["금액"].sum().reset_index()
        ti = os["금액"].sum()
        os = pd.concat([os, pd.DataFrame([{"보관하는 사람": "합계", "금액": ti}])], ignore_index=True)
        os["비중"] = (os["금액"] / ti * 100).round(1).astype(str) + "%"
        os["금액(원)"] = os["금액"].apply(lambda x: f"{x:,.0f}")
        st.table(os[["보관하는 사람", "금액(원)", "비중"]].set_index("보관하는 사람"))
        fig_p = px.pie(df_p, names='항목', values='금액', color='항목', color_discrete_map={r['항목']: r['색상'] for _, r in df_p.iterrows()})
        fig_p.update_traces(textinfo="label+percent+value", texttemplate="%{label}<br>%{percent}<br>₩%{value:,.0f}", textposition="inside", insidetextorientation='horizontal')
        fig_p.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- [탭 2] 월별 보기 (스타일 및 정수 변환) ---
with tab2:
    st.markdown("<div class='section-title'>📅 월별 상세 재무 분석</div>", unsafe_allow_html=True)
    sel = st.selectbox("분석할 월 선택", options=available_months, index=0)
    
    # 실제 데이터 매핑 (image_ca5d1b, ca689d 기준)
    cur = {"income": 11547372, "f_inc": 6080000, "v_inc": 5467372, "expense": 6125348, "f_exp": 2253453, "v_exp": 3871895, "total": 7063715, "f_cont": 2632715, "free_cont": 4431000}

    # [수정] 1. 빅넘버 (ValueError 해결된 포맷팅)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 수입</div><div class='metric-value'>{cur['income']:,.0f}원</div><div class='sub-text'>고정 {cur['f_inc']:,.0f} / 변동 {cur['v_inc']:,.0f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 지출</div><div class='metric-value'>{cur['expense']:,.0f}원</div><div class='sub-text'>고정 {cur['f_exp']:,.0f} / 변동 {cur['v_exp']:,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 투입 (투자+상환)</div><div class='metric-value'>{cur['total']:,.0f}원</div><div class='sub-text'>고정 {cur['f_cont']:,.0f} / 자유 {cur['free_cont']:,.0f}</div></div>", unsafe_allow_html=True)

    st.divider()
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**💰 투자 종목 증가 Top 5 (금액 기준)**")
        amt_df = pd.DataFrame({"종목": ["GOOGL", "SCHD", "TIGER 미국배당", "ETH", "XRP"], "증가금액(원)": ["1,561,671", "874,183", "539,175", "505,594", "400,701"]})
        st.table(amt_df.set_index("종목"))
    with col_t2:
        st.write("**📦 투자 종목 증가 Top 5 (수량 기준)**")
        qty_df = pd.DataFrame({"종목": ["XRP", "SCHD", "GOOGL", "TIGER 미국배당", "Tesla"], "증가수량": ["187", "81", "5", "5", "1"]})
        st.table(qty_df.set_index("종목"))

    st.divider()
    # [핵심] 재무상태 상세 내역 스타일 재현
    st.markdown(f"<div class='section-title'>🧱 {sel}. 재무상태 상세 (A~J열)</div>", unsafe_allow_html=True)
    s_sheet = f"{sel}. 재무상태"
    if s_sheet in raw_sheets:
        styled_df = style_financial_sheet(raw_sheets[s_sheet].iloc[:, 0:10])
        st.dataframe(styled_df, use_container_width=True, height=600)
    else:
        # 26.2. vs 26.02. 케이스 모두 대응
        alt_s = f"{float(sel):.1f}. 재무상태"
        if alt_s in raw_sheets:
            st.dataframe(style_financial_sheet(raw_sheets[alt_s].iloc[:, 0:10]), use_container_width=True, height=600)
        else:
            st.info(f"'{s_sheet}' 시트 데이터를 불러올 준비가 되었습니다.")

# --- [탭 3] 궁금증해결 (시뮬레이션 포함) ---
with tab3:
    st.markdown("<div class='section-title'>💡 탄탄부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    
    # 1. 왕(동현)의 궁금증
    st.markdown("### 🤴 왕(동현)의 궁금증 : '우리 당장 쓸 수 있는 돈이 얼마야?'")
    liq_df = df_p[df_p['유동성'] == True]
    total_liq = liq_df['금액'].sum()
    
    c_l1, c_l2 = st.columns([1, 1.5])
    with c_l1:
        st.markdown(f"<div class='custom-card' style='text-align:center;'><div class='metric-label'>부부 합산 즉시 가용 자산</div><div class='metric-value' style='color:#2E7D32;'>₩ {total_liq:,.0f}</div><div class='sub-text'>({sel}. 재무상태 기준)</div></div>", unsafe_allow_html=True)
    with c_l2:
        st.write("**💰 가용 자산 상세 구성**")
        comp = liq_df.groupby('항목')['금액'].sum().reset_index()
        comp['비중'] = (comp['금액']/total_liq*100).round(1).astype(str) + "%"
        comp['금액(원)'] = comp['금액'].apply(lambda x: f"{x:,.0f}")
        st.table(comp[['항목', '금액(원)', '비중']].set_index('항목'))

    st.divider()

    # 2. 왕비(건희)의 궁금증
    st.markdown("### 👸 왕비(건희)의 궁금증 : '우리 목표까지 얼마나 남았지?'")
    targets = {"1차 목표": {"amount": 175500000, "desc": "+1억 증식 (1.75억)", "plan": "2027-06"}, "2차 목표": {"amount": 200000000, "desc": "순자산 2억 돌파", "plan": "2027-12"}}
    ct1, ct2 = st.columns(2)
    for i, (name, target) in enumerate(targets.items()):
        with [ct1, ct2][i]:
            rate = (d['net_asset'] / target['amount']) * 100
            rem = target['amount'] - d['net_asset']
            est_date = datetime(2026, 2, 1) + timedelta(days=int(30 * (rem / d['avg_monthly_inc'])))
            st.markdown(f"#### {name} : {target['desc']}")
            st.markdown(f"계획: **{target['plan']}** | 달성률: <span class='highlight-text'>{rate:.1f}%</span>", unsafe_allow_html=True)
            st.progress(min(rate/100, 1.0))
            st.markdown(f"<div class='custom-card' style='height:140px; margin-top:10px;'><div class='metric-label'>예상 달성 시점</div><div class='metric-value' style='font-size:22px;'>🚀 {est_date.strftime('%Y년 %m월')}</div><div class='sub-text'>(월평균 증액 {d['avg_monthly_inc']:,.0f}원 기준)</div></div>", unsafe_allow_html=True)
