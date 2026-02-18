import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# 1. 페이지 설정 및 프리미엄 UI 스타일링
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

    /* 슬라이더 테마 (갈색 유지) */
    div[data-testid="stSlider"], div[data-testid="stSlider"] > div { background-color: transparent !important; }
    .stSlider [data-baseweb="slider"] > div:first-child { background: #dee2e6 !important; }
    .stSlider [role="slider"] { background-color: #5D4037 !important; border: 2px solid #FFFFFF !important; }

    /* 표 중앙 정렬 */
    .stTable tbody tr td { color: #000000 !important; text-align: center !important; }
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
        months = sorted(list(set([re.findall(r'(\d{2}\.\d{1,2})\.', s)[0] for s in s_names if re.findall(r'(\d{2}\.\d{1,2})\.', s)])), key=lambda x: float(x), reverse=True)
    except:
        all_sheets, months = {}, ["26.2"]

    # 메인 지표
    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585, "avg_monthly_inc": 6391299 
    }
    
    # [복구] 탭 1용 요약 테이블 데이터
    df_p_owner = pd.DataFrame([
        {"보관하는 사람": "👸 왕비", "금액(원)": "65,850,668", "비중": "64.5%"},
        {"보관하는 사람": "🤴 왕", "금액(원)": "36,290,402", "비중": "35.5%"},
        {"보관하는 사람": "합계", "금액(원)": "102,141,070", "비중": "100.0%"}
    ])
    
    # [수정] 자산 유형별 구성 + 소유자별 컬러 (건희: 핑크계열, 동현: 보라계열)
    df_p_type = pd.DataFrame([
        {"label": "해외주식", "owner": "건희", "금액": 31225286, "색상": "#FF1493"},
        {"label": "ISA", "owner": "건희", "금액": 8651400, "색상": "#FF69B4"},
        {"label": "연금저축", "owner": "건희", "금액": 16803088, "색상": "#FFB6C1"},
        {"label": "가상화폐", "owner": "건희", "금액": 6096394, "색상": "#FFC0CB"},
        {"label": "종신보험", "owner": "건희", "금액": 3074500, "색상": "#FFE4E1"},
        {"label": "해외주식", "owner": "동현", "금액": 34809457, "색상": "#8E44AD"},
        {"label": "ISA", "owner": "동현", "금액": 1480945, "색상": "#D7BDE2"}
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
    
    return d, df_p_owner, df_p_type, df_t, months, all_sheets

d, df_p_owner, df_p_type, df_t, available_months, raw_sheets = load_all_tantan_data()

# [함수] 재무상태 표 스타일링 (D, E열 텍스트 복구 및 색상 1:1 재현)
def style_financial_sheet(df):
    # D, E열 (인덱스 2, 3) 텍스트 데이터 강제 복구
    df = df.iloc[:, 0:10].copy()
    df.iloc[:, 2] = df.iloc[:, 2].astype(str).replace(['nan', '0', '0.0', 'None'], '')
    df.iloc[:, 3] = df.iloc[:, 3].astype(str).replace(['nan', '0', '0.0', 'None'], '')
    
    df = df.replace(".", "").fillna("")
    
    # 숫자형 포맷팅 (F~I열)
    num_cols = df.columns[4:10] 
    for col in num_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    def apply_row_style(row):
        cat, sub_cat = str(row.iloc[0]), str(row.iloc[1])
        # 1. 헤더 (검정 배경)
        if cat in ['자산', '부채', '순자산'] and sub_cat == "":
            return ['background-color: #333333; color: white; font-weight: 800'] * len(row)
        # 2. 카테고리 (진회색 배경)
        elif sub_cat in ['유동 자산', '투자 자산', '비유동 자산', '단기 부채', '장기 부채']:
            return ['background-color: #E9ECEF; color: black; font-weight: 700'] * len(row)
        # 3. 데이터 행 (연회색 배경)
        elif cat == '자산' and sub_cat != "":
            return ['background-color: #F8F9FA; color: black'] * len(row)
        return ['background-color: white; color: black'] * len(row)

    return df.style.apply(apply_row_style, axis=1).format({
        df.columns[4]: "{:,.0f}", df.columns[5]: "{:,.0f}",
        df.columns[6]: "{:,.0f}", df.columns[7]: "{:,.0f}",
        df.columns[8]: "{:,.0f}", df.columns[9]: "{:,.1f}"
    })

# --- [Header] ---
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

t1, t2, t3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 1] 전체 현황 ---
with t1:
    st.markdown("<div class='section-title'>📍 현재 위치 요약</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 자산</div><div class='metric-value'>{d['current_assets']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 부채</div><div class='metric-value'>{d['current_debt']:,.0f}원</div></div>", unsafe_allow_html=True)
    with c3:
        diff = d['net_asset'] - d['last_month_net']
        st.markdown(f"<div class='custom-card'><div class='metric-label'>순자산</div><div class='metric-value'>{d['net_asset']:,.0f}원</div><div><span style='background-color:#FFE4E1; color:#FF1493; padding:4px 12px; border-radius:12px; font-size:14px; font-weight:700;'>전월 대비 {abs(diff):,.0f}원 ↑</span></div></div>", unsafe_allow_html=True)
    
    st.divider()
    col_l, col_r = st.columns([1.2, 1])
    with col_l:
        st.markdown("<div class='section-title'>순자산 성장 추이</div>", unsafe_allow_html=True)
        m_list = df_t['날짜'].dt.strftime('%Y-%m').tolist()
        sm, em = st.select_slider("📅 조회 월 범위 선택", options=m_list, value=(m_list[0], m_list[-1]), key="s_main")
        ft = df_t[(df_t['날짜'] >= pd.to_datetime(sm)) & (df_t['날짜'] <= pd.to_datetime(em))]
        
        # [수정] 지난 달 대비 증감액을 마커에 표시
        labels = [f"{v:,}만\n(+{z:,})" if z > 0 else f"{v:,}만" for v, z in zip(ft['순자산_만원'], ft['증감'])]
        
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=ft['날짜'], y=ft['순자산_만원'], mode='lines+markers+text', text=labels, textposition="top center", line=dict(color='#5D4037', width=4)))
        fig_l.update_layout(yaxis=dict(range=[7000, ft['순자산_만원'].max()*1.15]), plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, l=0, r=0, b=0))
        st.plotly_chart(fig_l, use_container_width=True)
        
    with col_r:
        st.markdown("<div class='section-title'>투자 자산 구성</div>", unsafe_allow_html=True)
        # [복구] 상단 요약 테이블
        st.table(df_p_owner.set_index("보관하는 사람"))
        
        # [수정] 파이차트: 건희(핑크계열), 동현(보라계열) 구분 및 내부 텍스트 최적화
        fig_p = px.pie(df_p_type, names='label', values='금액', color='색상', color_discrete_sequence=df_p_type['색상'].tolist())
        fig_p.update_traces(textinfo="label+percent", textposition="inside", hole=0)
        fig_p.update_layout(margin=dict(t=0, l=0, r=0, b=0), showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- [탭 2] 월별 보기 ---
with t2:
    st.markdown("<div class='section-title'>📅 월별 상세 재무 분석</div>", unsafe_allow_html=True)
    sel = st.selectbox("분석할 월 선택", options=available_months, index=0)
    
    cur = {"income": 11547372, "f_inc": 6080000, "v_inc": 5467372, "expense": 6125348, "f_exp": 2253453, "v_exp": 3871895, "total": 7063715, "f_cont": 2632715, "free_cont": 4431000}

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 수입</div><div class='metric-value'>{cur['income']:,.0f}원</div><div class='sub-text'>고정 {cur['f_inc']:,.0f} / 변동 {cur['v_inc']:,.0f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 지출</div><div class='metric-value'>{cur['expense']:,.0f}원</div><div class='sub-text'>고정 {cur['f_exp']:,.0f} / 변동 {cur['v_exp']:,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 투입 (투자+상환)</div><div class='metric-value'>{cur['total']:,.0f}원</div><div class='sub-text'>고정 {cur['f_cont']:,.0f} / 자유 {cur['free_cont']:,.0f}</div></div>", unsafe_allow_html=True)

    st.divider()
    # [복구] 정확한 Top 5 증감 현황
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.write("**💰 투자 종목 증가 Top 5 (금액 기준)**")
        st.table(pd.DataFrame({"종목": ["GOOGL", "SCHD", "TIGER 미국배당", "ETH", "XRP"], "증가액": ["1,561,671", "874,183", "539,175", "505,594", "400,701"]}).set_index("종목"))
    with col_v2:
        st.write("**📦 투자 종목 증가 Top 5 (수량 기준)**")
        st.table(pd.DataFrame({"종목": ["XRP", "TQQQ", "TIGER 미국배당", "GOOGL", "Tesla"], "증가수량": ["187", "6", "5", "5", "1"]}).set_index("종목"))

    st.divider()
    st.markdown(f"<div class='section-title'>🧱 {sel}. 재무상태 상세 (A~J열)</div>", unsafe_allow_html=True)
    s_sheet = f"{sel}. 재무상태"
    if s_sheet in raw_sheets:
        # [해결] D, E열 텍스트 데이터 복구 및 시트 컬러 적용
        styled_df = style_financial_sheet(raw_sheets[s_sheet])
        st.dataframe(styled_df, use_container_width=True, height=600)

# --- [탭 3] 궁금증해결 (시뮬레이션) ---
with t3:
    st.markdown("<div class='section-title'>💡 탄탄부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    
    st.markdown("### 🤴 왕(동현)의 궁금증 : '우리 당장 쓸 수 있는 돈이 얼마야?'")
    total_liq = 82261545 
    c_l1, c_l2 = st.columns([1, 1.5])
    with c_l1:
        st.markdown(f"<div class='custom-card' style='text-align:center;'><div class='metric-label'>부부 합산 즉시 가용 자산</div><div class='metric-value' style='color:#2E7D32;'>₩ {total_liq:,.0f}</div><div class='sub-text'>({sel}. 재무상태 기준)</div></div>", unsafe_allow_html=True)
    with c_l2:
        st.write("**💰 가용 자산 상세 구성 (연금/보험 제외)**")
        comp = pd.DataFrame({"항목": ["해외주식(부부합산)", "ISA(부부합산)", "가상화폐(건희)", "예금통장(부부합산)"], "금액": ["66,034,743", "10,132,345", "6,096,394", "8,500,000"]})
        st.table(comp.set_index("항목"))

    st.divider()
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
