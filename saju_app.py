import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar

# ==========================================
# [PROJECT: 루나 언니 - FINAL MASTERPIECE]
# "스레드 연동 + 자동 호칭 + 2026년 대비 + 완벽한 수익화"
# ==========================================

st.set_page_config(page_title="루나: 미래 상담사", page_icon="🌙", layout="wide")

# --- 스타일링 (힙한 블랙 & 핫핑크) ---
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
</style>
""", unsafe_allow_html=True)

# --- 사이드바: 설정 ---
with st.sidebar:
    st.header("💋 루나 언니 대기실")
    
    # [복채 배너] 스레드 팔로우 유도
    st.markdown("""
    <div style='background-color: #330019; padding: 15px; border-radius: 10px; border: 1px solid #FF007F;'>
        <p style='color: white; font-weight: bold; margin: 0; font-size: 16px;'>💸 복채는 돈 대신 받는다.</p>
        <p style='color: #FF007F; font-size: 14px; margin-top: 10px; line-height: 1.5;'>
        <b>'팔로우'</b>하고 <b>'댓글'</b> 남겨야<br>
        점괘 약발 더 잘 받는 거 알지? 😉<br>
        (필수니까 얼른 하고 와!)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # [링크] 자네의 루나 계정으로 연결 (주소 수정 완료)
    sns_link = "https://www.threads.net/@luna_fortune_2026" 
    st.link_button("💖 약발 받으러 가기 (Click)", sns_link)

    # [자동 로그인] Secrets에서 키 가져오기
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("상담권(API Key) 내놔", type="password")
    
    st.divider()
    
    # [모델 선택] 안정적인 1.5 버전 사용
    model_option = st.radio("언니 컨디션", ["🔥 풀파워 (Pro)", "⚡ 급속 (Flash)"])
    if "Pro" in model_option:
        selected_model = "gemini-2.5-pro"
    else:
        selected_model = "gemini-2.5-flash"

# --- 메인 로직 ---
st.title("💋 2026년 예언:🌙루나 미래 상담사")
st.markdown("### \"우리 동생, 2025년 고생했어. 이제 2026년 준비해야지?\"")

# 주제 선택
topic = st.radio(
    "뭐가 궁금해? 골라봐.",
    ["📅 오늘 하루나 잘 넘기자 (오늘의 운세)", "🦄 2026년(병오년) 나 어때? (신년 총운)"],
    index=1, 
    horizontal=True
)

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름 (본명)", placeholder="박경미")
    gender = st.radio("성별", ["여자", "남자"])
with col2:
    birth_date = st.date_input("생년월일", min_value=datetime.date(1950, 1, 1), value=datetime.date(1990, 1, 1))
    birth_time = st.time_input("태어난 시간", datetime.time(9, 00))

# [중요] 주제에 따른 질문 & 수익화 링크 자동 변경
if "2026" in topic:
    worry = st.text_input("내년에 뭐가 제일 걱정돼?", placeholder="돈, 연애, 건강... 솔직히 말해.")
    # 2026년 대비용 다이어리/플래너 링크 (나중에 자네 파트너스 링크로 교체)
    lucky_link = "https://www.coupang.com/np/search?component=&q=2026년다이어리" 
    btn_text = "🦄 2026년 내 운명 팩트체크 하기 (Click)"
else:
    worry = st.text_input("오늘 기분 어때?", placeholder="꿀꿀해, 불안해...")
    # 가벼운 코디/소품 링크 (나중에 자네 파트너스 링크로 교체)
    lucky_link = "https://www.coupang.com/np/search?component=&q=행운의키링" 
    btn_text = "📅 오늘 하루, 언니한테 점검받기 (Click)"


# --- 버튼 클릭 시 실행 ---
if st.button(btn_text, use_container_width=True):
    if not gemini_api_key:
        st.error("잠깐! 왼쪽 사이드바에 키(Key)가 없잖아. (서버 설정 확인 필요)")
    else:
        try:
            # 1. 음력 변환
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            # 2. 날짜 고정
            current_date_str = "2025년 11월 26일"
            
            # 3. [지능형 호칭 시스템] 여자->언니, 남자->누나
            if gender == "여자":
                my_title = "언니"
            else:
                my_title = "누나"

            # 4. 루나 페르소나 (다정+팩폭)
            prompt = f"""
            [System Setting]
            - Current Date: {current_date_str} (Late 2025)
            - Upcoming Year: 2026 (Year of the Red Horse, 병오년)
            - Target User: {name} ({gender})
            - Birth: {birth_date} (Lunar: {lunar_date})
            - User's Worry: {worry if worry else 'Just check my vibe'}
            
            [Persona: 'Luna {my_title}' (Cool & Caring Mentor)]
            - You are a cool, stylish, and realistic older sister/noona.
            - **Call yourself:** '{my_title}' (e.g., {my_title}가 봤을 땐).
            - **Call the user:** "우리 {name}" (My {name}) or "{name}아/{name}야".
            - **NEVER use:** "야!" (Too rude), "당신" (Too distant).
            - **Tone:** 100% Banmal (Casual Korean). Direct but full of affection.
            
            [Analysis Content]
            1. **🔥 팩트 진단 (Personality)**
               - Start with: "우리 {name}, {my_title}가 보니까 너는..."
               - Analyze the Saju deeply but explain it simply.
               - Point out flaws affectionately (e.g., "너 맘이 너무 약해서 탈이야.").
            
            2. **🔮 미래 예언 ({'2026년' if '2026' in topic else '오늘'})**
               - Give a clear verdict on their worry.
               - DO NOT talk about 2024. Focus on the transition to 2026.
               
            3. **💋 {my_title}의 코디 추천 (Solution)**
               - Suggest **light fashion items or accessories** (Ring, Cap, Socks, Planner).
               - Recommend a specific Color and Item.
               - End with: "우리 {name}, 기 죽지 마. {my_title}가 항상 응원한다."
            """
            
            with st.spinner(f"{my_title}가 우리 {name} 사주 꼼꼼히 보는 중..."):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(selected_model) 
                response = model.generate_content(prompt)
                
                # 결과 출력
                st.markdown("---")
                st.success(f"📨 우리 {name} 분석 끝났다. 얼른 확인해 봐.")
                st.markdown(response.text)
                
                # 수익화 섹션
                st.markdown("---")
                st.markdown(f"### 💋 {name}(을)를 위한 {my_title}의 코디 추천")
                
                if "2026" in topic:
                    st.write(f"2026년은 '폼'이 생명이야. {my_title}가 골라준 이거 하나면 기운 확 달라진다. 비싼 거 필요 없어.")
                else:
                    st.write(f"오늘 나가기 전에 이거 챙겼어? 없으면 하나 장만해. {my_title} 믿고 딱 한 번만 해봐.")
                    
                st.link_button(f"👉 {my_title}가 골라준 '행운의 소품' 보기", lucky_link)

        except Exception as e:
            st.error(f"아오.. 서버가 말을 안 듣네. 다시 눌러봐. (Error: {e})")

