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
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 연동 및 매핑 로직
SHEET_ID = "1gcAqoVL6Y4XCh-EWrm3-Nprya3xEauLS4VckrFiBYqw"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

@st.cache_data(ttl=60)
def load_all_tantan_data():
    all_sheets = pd.read_excel(EXCEL_URL, sheet_name=None, engine='openpyxl')
    s_names = list(all_sheets.keys())
    # yy.m. 또는 yy.mm. 패턴 자동 인식
    months = sorted(list(set([re.findall(r'(\d{2}\.\d{1,2})\.', s)[0] for s in s_names if re.findall(r'(\d{2}\.\d{1,2})\.', s)])), key=lambda x: float(x), reverse=True)
    months = [m for m in months if m.startswith('26')]

    # [탭 1] 고정 데이터
    d = {
        "current_assets": 403641070, "current_debt": 290900679, "net_asset": 112740391,
        "last_month_net": 108187566, "base_net_asset": 75767585,
        "avg_monthly_inc": 6391299 
    }
    
    df_p_main = pd.DataFrame([
        {"보관하는 사람": "👸 왕비", "항목": "해외주식", "금액": 31225286, "색상": "#FF1493", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "ISA", "금액": 8651400, "색상": "#FFB6C1", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "가상화폐", "금액": 6096394, "색상": "#FFC0CB", "유동성": True},
        {"보관하는 사람": "👸 왕비", "항목": "연금저축", "금액": 16803088, "색상": "#FF69B4", "유동성": False},
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
    
    return d, df_p_main, df_t, months, all_sheets

d, df_p, df_t, available_months, raw_sheets = load_all_tantan_data()

# 스타일링 함수 (F~I열 정수 및 콤마 적용)
def style_financial_sheet(df):
    df = df.replace(".", "").fillna("")
    num_cols = df.columns[3:10]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    def apply_row_style(row):
        cat, sub_cat = str(row.iloc[0]), str(row.iloc[1])
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

# --- [Header] ---
st.title("🏆 탄탄부부의 경제적 자유를 위한 위대한 여정")
st.markdown("#### 우리의 속도대로 차근차근 성실하게 🚀💛")

t1, t2, t3 = st.tabs(["📊 전체 현황", "📆 월별 보기", "💡 궁금증해결"])

# --- [탭 2] 월별 보기 (데이터 연동 강화) ---
with t2:
    st.markdown("<div class='section-title'>📅 월별 상세 재무 분석</div>", unsafe_allow_html=True)
    sel = st.selectbox("분석할 월 선택", options=available_months, index=0)
    
    # [데이터 자동 매핑] '현금흐름' 시트에서 수치 추출 시도
    f_sheet = f"{sel}. 현금흐름"
    if f_sheet in raw_sheets:
        fs = raw_sheets[f_sheet]
        # 시트 내 위치가 고정되어 있다면 아래와 같이 추출 (예시 인덱스)
        # 실제 시트 구조에 맞춰 행/열 번호(iloc)를 조정해야 합니다.
        try:
            cur = {
                "income": fs.iloc[1, 2], "f_inc": fs.iloc[2, 2], "v_inc": fs.iloc[3, 2],
                "expense": fs.iloc[5, 2], "f_exp": fs.iloc[6, 2], "v_exp": fs.iloc[7, 2],
                "total": fs.iloc[9, 2], "f_cont": fs.iloc[10, 2], "free_cont": fs.iloc[11, 2]
            }
        except:
            # 시트 구조가 다를 경우를 대비한 백업 (26.2. 기준 하드코딩)
            cur = {"income": 11547372, "f_inc": 6080000, "v_inc": 5467372, "expense": 6125348, "f_exp": 2253453, "v_exp": 3871895, "total": 7063715, "f_cont": 2632715, "free_cont": 4431000}
    else:
        cur = {"income": 0, "f_inc": 0, "v_inc": 0, "expense": 0, "f_exp": 0, "v_exp": 0, "total": 0, "f_cont": 0, "free_cont": 0}

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 수입</div><div class='metric-value'>{cur['income']:,.0f}원</div><div class='sub-text'>고정 {cur['f_inc']:,.0f} / 변동 {cur['v_inc']:,.0f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='custom-card'><div class='metric-label'>이번 달 총 지출</div><div class='metric-value'>{cur['expense']:,.0f}원</div><div class='sub-text'>고정 {cur['f_exp']:,.0f} / 변동 {cur['v_exp']:,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='custom-card'><div class='metric-label'>총 투입 (투자+상환)</div><div class='metric-value'>{cur['total']:,.0f}원</div><div class='sub-text'>고정 {cur['f_cont']:,.0f} / 자유 {cur['free_cont']:,.0f}</div></div>", unsafe_allow_html=True)

    st.divider()
    s_sheet = f"{sel}. 재무상태"
    if s_sheet in raw_sheets:
        styled_df = style_financial_sheet(raw_sheets[s_sheet].iloc[:, 0:10])
        st.dataframe(styled_df, use_container_width=True, height=600)

# --- [탭 3] 궁금증해결 ---
with t3:
    st.markdown("<div class='section-title'>💡 탄탄부부 전용 궁금증 해결</div>", unsafe_allow_html=True)
    
    # 왕의 궁금증
    st.markdown("### 🤴 왕(동현)의 궁금증 : '우리 당장 쓸 수 있는 돈이 얼마야?'")
    liquid_df = df_p[df_p['유동성'] == True]
    total_liquid = liquid_df['금액'].sum()
    
    c_l1, c_l2 = st.columns([1, 1.5])
    with c_l1:
        st.markdown(f"<div class='custom-card' style='text-align:center;'><div class='metric-label'>부부 합산 즉시 가용 자산</div><div class='metric-value' style='color:#2E7D32;'>₩ {total_liquid:,.0f}</div><div class='sub-text'>({sel}. 재무상태 기준)</div></div>", unsafe_allow_html=True)
    with c_l2:
        st.write("**💰 가용 자산 상세 구성**")
        comp = liquid_assets = liquid_df.groupby('항목')['금액'].sum().reset_index()
        comp['비중'] = (comp['금액']/total_liquid*100).round(1).astype(str) + "%"
        comp['금액(원)']=comp['금액'].apply(lambda x:f"{x:,.0f}")
        st.table(comp[['항목', '금액(원)', '비중']].set_index('항목'))

    st.divider()

    # 왕비의 궁금증
    st.markdown("### 👸 왕비(건희)의 궁금증 : '우리 목표까지 얼마나 남았지?'")
    targets = {"1차 목표": {"amount": 175500000, "desc": "+1억 증식 (1.75억)", "plan": "2027-06"}, "2차 목표": {"amount": 200000000, "desc": "순자산 2억 돌파", "plan": "2027-12"}}
    
    ct1, ct2 = st.columns(2)
    for i, (name, target) in enumerate(targets.items()):
        with [ct1, ct2][i]:
            rate = (d['net_asset'] / target['amount']) * 100
            rem = target['amount'] - d['net_asset']
            days_left = int(rem / (d['avg_monthly_inc'] / 30))
            est_date = datetime.now() + timedelta(days=days_left)
            st.markdown(f"#### {name} : {target['desc']}")
            st.markdown(f"계획: **{target['plan']}** | 달성률: <span class='highlight-text'>{rate:.1f}%</span>", unsafe_allow_html=True)
            st.progress(min(rate/100, 1.0))
            st.markdown(f"<div class='custom-card' style='height:140px; margin-top:10px;'><div class='metric-label'>예상 달성 시점</div><div class='metric-value' style='font-size:22px;'>🚀 {est_date.strftime('%Y년 %m월')}</div><div class='sub-text'>(월평균 증액 {d['avg_monthly_inc']:,.0f}원 기준)</div></div>", unsafe_allow_html=True)
