import streamlit as st
import yfinance as yf
from google import genai
import pandas as pd

# --- 1. 웹 페이지 기본 설정 ---
st.set_page_config(page_title="AI 종합 자산 관리", page_icon="🏦", layout="wide")

# 비밀 금고(Secrets)에서 API 키 불러오기
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    # 2025년 무료 티어에서 가장 안정적인 모델 별칭 설정
    TARGET_MODEL = 'gemini-flash-latest'
except Exception:
    st.error("❌ API Key를 찾을 수 없습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

# --- 2. 상단 레이아웃 ---
st.title("🏦 AI 통합 자산 관리 솔루션 v1.2")
st.markdown("실시간 금융 데이터와 **2025년형 최신 AI**가 당신의 자산을 관리합니다.")
st.divider()

# 서비스 탭 구성
tab1, tab2 = st.tabs(["📈 글로벌 AI 투자 비서", "👴 4050 노후 관리 매니저"])

# --- 3. [탭 1] 글로벌 AI 투자 비서 ---
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔍 종목 분석")
        ticker = st.text_input("종목 코드를 입력하세요 (예: TSLA, NVDA, BTC-USD)", value="TSLA").upper()
        analyze_btn = st.button("AI 전략 리포트 생성")

    if analyze_btn:
        with st.spinner('데이터 분석 중...'):
            try:
                # 데이터 수집 및 지표 계산
                stock = yf.Ticker(ticker)
                df = stock.history(period="30d")
                
                if df.empty:
                    st.error("종목 데이터를 가져올 수 없습니다. 코드를 확인해주세요.")
                else:
                    today_price = df['Close'].iloc[-1]
                    ma5_price = df['Close'].rolling(window=5).mean().iloc[-1]
                    trend = "상승" if today_price > ma5_price else "하락"

                    # 뉴스 수집 (2025년 최신 구조 대응)
                    news_text = ""
                    if stock.news:
                        for n in stock.news[:3]:
                            title = n.get('content', {}).get('title', '제목 없음')
                            news_text += f"- {title}\n"

                    # AI 분석 요청
                    prompt = f"""
                    당신은 냉철한 투자 전문가입니다. {ticker}에 대해 분석해주세요.
                    현 주가: {today_price:.2f} / 5일 이평선: {ma5_price:.2f} ({trend}세)
                    최신 뉴스: {news_text}
                    양식: 1.시장현황(1줄) 2.호재/악재 3.최종추천(매수/매도/관망) 4.이유
                    """
                    
                    response = client.models.generate_content(model=TARGET_MODEL, contents=prompt)

                    with col2:
                        st.subheader(f"📊 {ticker} 분석 결과")
                        st.line_chart(df['Close'])
                        st.info(response.text)
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")

# --- 4. [탭 2] 노후 관리 매니저 ---
with tab2:
    st.title("👴 은퇴 설계 시뮬레이션")
    st.markdown("현재의 자산과 저축 습관을 바탕으로 미래를 진단합니다.")
    
    with st.form("retirement_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("현재 나이", 20, 70, 45)
            retire_age = st.number_input("은퇴 희망 나이", 50, 90, 65)
        with c2:
            asset = st.number_input("현재 자산 (만원)", 0, 1000000, 10000)
            monthly_save = st.number_input("월 저축액 (만원)", 0, 1000, 100)
        with c3:
            spend = st.number_input("은퇴 후 월 희망 생활비 (만원)", 0, 2000, 300)
            rate = st.slider("기대 수익률 (%)", 0.0, 15.0, 4.0)
        
        submit = st.form_submit_button("노후 진단 시작")

    if submit:
        # 은퇴 자산 시뮬레이션 (복리 계산)
        years = retire_age - age
        future_asset = asset * ((1 + rate/100) ** years)
        for i in range(years):
            future_asset += (monthly_save * 12) * ((1 + rate/100) ** (years - i))
        
        st.divider()
        st.metric("은퇴 시점 예상 자산", f"{int(future_asset):,} 만원")
        
        # AI 상담원 진단 요청
        retirement_prompt = f"""
        당신은 실버케크 자산관리사입니다. 
        {age}세 사용자가 {retire_age}세에 {int(future_asset)}만원으로 은퇴하려 합니다.
        은퇴 후 월 {spend}만원 생활이 가능할지 분석하고, 남은 {years}년 동안의 전략을 세워주세요.
        """
        
        with st.spinner('AI 매니저가 조언을 준비 중입니다...'):
            try:
                res = client.models.generate_content(model=TARGET_MODEL, contents=retirement_prompt)
                st.success("🤖 AI 맞춤형 노후 전략")
                st.write(res.text)
            except Exception as e:
                st.error(f"AI 진단 중 오류 발생: {e}")