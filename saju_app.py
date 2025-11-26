import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar

# ==========================================
# [PROJECT: 루나 언니 - MOBILE OPTIMIZED]
# "이름 빈칸 수정 + 복채 배너를 메인 화면으로 이동 (모바일 필승 전략)"
# ==========================================

st.set_page_config(page_title="루나: 미래상담사", page_icon="🌙", layout="wide")

# --- 스타일링 ---
st.markdown("""
<style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button {
        background-color: #FF007F; /* 핫핑크 */
        color: white; font-weight: bold; border: 2px solid white; height: 60px; font-size: 20px;
        box-shadow: 4px 4px 0px #ffffff;
    }
    h1 { color: #FF007F; font-family: 'Sans-serif'; font-weight: 900; font-style: italic; }
    .stTextInput>div>div>input { color: black; font-weight: bold; }
    /* 라디오 버튼 텍스트 색상 */
    .stRadio > label { color: white !important; font-size: 16px; }
    div[data-baseweb="radio"] > div { color: white; }
    
    /* 복채 배너 스타일 */
    .follow-box {
        background-color: #330019; padding: 15px; border-radius: 10px; 
        border: 1px solid #FF007F; text-align: center; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바: 키 설정 (배너는 메인으로 뺌) ---
with st.sidebar:
    st.header("🔧 설정")
    # 자동 로그인
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("키 입력", type="password")
    
    st.divider()
    model_option = st.radio("속도 선택", ["🔥 풀파워 (Pro)", "⚡ 급속 (Flash)"])
    if "Pro" in model_option:
        selected_model = "gemini-2.5-pro"
    else:
        selected_model = "gemini-2.5-flash"

# --- 메인 로직 ---
st.title("💋 2026년 예언: 🌙루나 미래 상담사")
st.markdown("### \"우리 동생, 2025년 고생했어. 이제 2026년 준비해야지?\"")

# [🔥 중요] 복채 배너를 화면 맨 위로 이동 (모바일 가시성 100%)
sns_link = "https://www.threads.net/@luna_fortune_2026"
st.markdown(f"""
<a href="{sns_link}" target="_blank" style="text-decoration: none;">
    <div class="follow-box">
        <p style='color: white; font-weight: bold; margin: 0; font-size: 18px;'>💸 복채는 돈 대신 '팔로우'로 받는다.</p>
        <p style='color: #FF007F; font-size: 14px; margin-top: 5px;'>
        (터치해서 약발 받으러 가기 👆)
        </p>
    </div>
</a>
""", unsafe_allow_html=True)

# 주제 선택
topic = st.radio(
    "뭐가 궁금해? 골라봐.",
    ["📅 오늘 하루나 잘 넘기자 (오늘의 운세)", "🦄 2026년(병오년) 나 어때? (1년 운세)"],
    index=1, 
    horizontal=True
)

col1, col2 = st.columns(2)
with col1:
    # [수정 완료] value="" 로 설정하여 빈칸으로 만듦 / placeholder는 회색 안내 문구
    name = st.text_input("이름 (본명)", value="", placeholder="여기에 이름 입력해")
    gender = st.radio("성별", ["여자", "남자"])
with col2:
    birth_date = st.date_input("생년월일", min_value=datetime.date(1950, 1, 1), value=datetime.date(1990, 1, 1))
    birth_time = st.time_input("태어난 시간", datetime.time(9, 00))

# 질문 & 링크 설정
if "2026" in topic:
    worry = st.text_input("내년에 뭐가 제일 걱정돼?", placeholder="돈, 연애, 건강... 솔직히 말해.")
    lucky_link = "https://www.coupang.com/np/search?component=&q=2026년다이어리" 
    btn_text = "🦄 2026년 내 운명 팩트체크 하기 (Click)"
else:
    worry = st.text_input("오늘 기분 어때?", placeholder="꿀꿀해, 불안해...")
    lucky_link = "https://www.coupang.com/np/search?component=&q=행운의키링" 
    btn_text = "📅 오늘 하루, 언니한테 점검받기 (Click)"


# --- 버튼 클릭 실행 ---
if st.button(btn_text, use_container_width=True):
    if not name:
        st.warning("야, 이름은 알려줘야 점을 보지. 이름 입력해.")
    elif not gemini_api_key:
        st.error("키 설정 오류. 관리자에게 문의하세요.")
    else:
        try:
            # 음력 변환 & 날짜 설정
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            current_date_str = "2025년 11월 26일"
            
            # 호칭 설정
            if gender == "여자": my_title = "언니"
            else: my_title = "누나"

            # 프롬프트
            prompt = f"""
            [System Setting]
            - Current Date: {current_date_str} (Late 2025)
            - Upcoming Year: 2026 (Year of the Red Horse)
            - Target User: {name} ({gender})
            - Birth: {birth_date} (Lunar: {lunar_date})
            - User's Worry: {worry if worry else 'General'}
            
            [Persona: 'Luna {my_title}']
            - Tough, cool, realistic older sister. 100% Banmal.
            - Start with: "우리 {name},"
            
            [Content]
            1. Personality Check (Fact bomb)
            2. Future Prediction ({'2026' if '2026' in topic else 'Today'})
            3. Solution (Lucky Item/Color)
            """
            
            with st.spinner(f"{my_title}가 우리 {name} 사주 꼼꼼히 보는 중..."):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(selected_model) 
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.success(f"📨 우리 {name} 분석 끝났다.")
                st.markdown(response.text)
                
                st.markdown("---")
                st.markdown(f"### 💋 {name}(을)를 위한 {my_title}의 추천템")
                st.write(f"이거 하나만 챙겨. {my_title} 믿고 딱 한 번만 해봐.")     
                st.link_button(f"👉 {my_title}가 골라준 '행운의 소품' 보기", lucky_link)

        except Exception as e:
            st.error(f"에러 났다: {e}")


