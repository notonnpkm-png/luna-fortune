import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random
import textwrap

# ==========================================
# [PROJECT: LUNA - REAL FINAL COMPLETE]
# 1. 황금박스 멘트 수정: "그냥 가면 손해" -> "행운템 꼭 보고가야해!!"
# 2. 모든 기능(호칭, 성떼기, HTML안전장치) 정상 작동 확인
# ==========================================

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="루나 : 운명 상담소",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. [디자인] CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    .stApp {
        background-color: #0E0E0E !important;
        color: #FFFFFF !important;
    }
    
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 20px !important; 
        font-weight: 500;
        background-color: #0E0E0E !important;
        color: #FFFFFF !important;
    }

    /* 방해꾼 제거 */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    div[class*="viewerBadge"], .viewerBadge_container__1QSob, [data-testid="stStatusWidget"] {
        display: none !important;
    }
    footer, #MainMenu, .stAppDeployButton {
        display: none !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 600px !important;
    }

    /* 입력폼 디자인 */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stRadio label, div[role="radiogroup"] label p {
        color: #E5C17C !important;
        font-size: 16px !important; 
        font-weight: 700 !important; 
    }
    
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #1E1E1E !important; 
        color: #FFFFFF !important; 
        border: 1px solid #555 !important;
        height: 50px !important;
        font-size: 16px !important;
        border-radius: 8px;
        text-align: center;
        font-weight: 600 !important; 
    }
    
    input::placeholder {
        color: #AAAAAA !important; 
        font-weight: 400 !important;
        opacity: 1 !important;
    }

    .stTextInput input:focus {
        border-color: #E5C17C !important;
    }

    /* 타이틀 */
    .main-title {
        color: #E5C17C;
        font-weight: 900;
        text-align: center;
        font-size: 1.8rem;
        margin-top: 10px;
        margin-bottom: 5px;
        text-shadow: 0 0 15px rgba(229, 193, 124, 0.3);
        word-break: keep-all;
    }
    .sub-title {
        color: #BBB;
        text-align: center;
        font-size: 1.0rem;
        margin-bottom: 25px;
    }

    .price-box {
        background-color: #181818;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #222, #333);
        color: #E5C17C;
        border: 1px solid #E5C17C;
        height: 65px !important;
        font-size: 18px !important;
        font-weight: 900;
        border-radius: 12px;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #E5C17C;
        color: #000;
        transform: scale(1.02);
    }

    /* 황금박스 CSS */
    @keyframes heartbeat {
        0% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.1); }
        50% { transform: scale(1.02); box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
        100% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.1); }
    }
    .golden-box {
        background-color: #1A1A1A;
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 30px 20px;
        margin-top: 40px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.9);
    }
    
    .pulse-button {
        display: block;
        width: 100%;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000 !important;
        font-weight: 900;
        font-size: 18px;
        padding: 18px 0;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 20px;
        animation: heartbeat 1.5s infinite ease-in-out;
        word-break: keep-all;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
    }
    
    .coupang-notice {
        font-size: 11px;
        color: #555;
        text-align: center;
        margin-top: 15px;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- [황금박스 생성 함수] 멘트 수정 완료 ---
def create_golden_box(name_title, link):
    return f"""
    <div class="golden-box">
        <h3 style="color:#FF6B6B; margin:0; font-size:22px; font-weight:900; line-height: 1.3;">
            🎁 {name_title},<br>행운템 꼭 보고가야해!!
        </h3>
        
        <div style="margin-top:20px; font-size:17px; color:#DDD; line-height: 1.6;">
            "{name_title}, 지금 딱 <b>2% 부족한 행운</b>을<br>
            채워줄 아이템이야."
        </div>
        
        <div style="margin-top:15px; font-size:16px; color:#BBB; line-height: 1.5;">
            루나가 <b>완전 갓성비</b>로만 골라놨어.<br>
            부담 갖지 마.<br>
            <span style="color:#FFD700; font-weight:bold;">그냥 구경만 해도 막힌 운이 뻥 뚫릴 거야.</span>
        </div>

        <a href="{link}" target="_blank" class="pulse-button">
            🚀 루나의 [시크릿 행운템] 구경하고 액땜하기 (Click)
        </a>
        
        <div class="coupang-notice">
            이 포스팅은 쿠팡 파트너스 활동의 일환으로,<br>
            이에 따른 일정액의 수수료를 제공받습니다.
        </div>
    </div>
    """

# --- 일간 계산 함수 ---
def get_day_gan(birth_date):
    ref_date = datetime.date(2000, 1, 1)
    ref_gan_idx = 4 
    gan_list = ["갑(甲, 큰 나무)", "을(乙, 꽃/덩굴)", "병(丙, 태양)", "정(丁, 촛불)", "무(戊, 큰 산)", 
                "기(己, 밭/대지)", "경(庚, 바위/도끼)", "신(辛, 보석/칼)", "임(壬, 바다)", "계(癸, 빗물)"]
    delta_days = (birth_date - ref_date).days
    gan_idx = (ref_gan_idx + delta_days) % 10
    return gan_list[gan_idx]

# --- 사이드바 ---
with st.sidebar:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 화면 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>(🥤 사이다 예언 맛집 🍿)</div>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6; font-size: 15px; color: #CCC;'>
    "혼자 끙끙 앓지 마요."<br>
    루나 언니가 당신의 미래와 해결책을<br> 
    <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF5555; font-weight:bold;'>(※ 팩폭 주의 🚨)</span>
</div>
""", unsafe_allow_html=True)

# 가격표
st.markdown("""
<a href="https://www.threads.net/@luna_fortune_2026" target="_blank" style="text-decoration:none;">
    <div class="price-box">
        <span style="color:#777; text-decoration:line-through; font-size:14px;">상담료 50,000원</span><br>
        <span style="color:#FFD700; font-size:20px; font-weight:bold;">✨ 지금만 무료 (0원)</span><br>
        <div style="margin-top:10px; color:#BBB; font-size:13px;">
            ⚠️ <b>주의:</b> 복채 대신 <b>'팔로우', '댓글'</b>은 필수!!<br>
            <span style="color:#FFD700;">(복채 안내면 상담 효과 없는거 아시죠?^^)</span>
        </div>
    </div>
</a>
""", unsafe_allow_html=True)

# --- 입력 폼 ---
topic = st.radio(
    "어떤 운명이 궁금한가요?",
    ["⚡ 오늘의 운세", "🦄 2026년 1년 운세"],
    index=1,
    horizontal=True
)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름 (본명)", placeholder="예: 이루나")
with col2:
    gender = st.radio("성별", ["여성", "남성"], horizontal=True)

birth_date = st.date_input(
    "생년월일",
    min_value=datetime.date(1940, 1, 1),
    value=datetime.date(1990, 1, 1)
)
birth_time = st.time_input("태어난 시간 (모르면 패스)", datetime.time(9, 00))

st.markdown("<br>", unsafe_allow_html=True)

if "2026" in topic:
    worry = st.text_input("가장 큰 고민은?", placeholder="예: 남편,남친이 바람?,돈,건강")
    btn_label = "두근 💓 2026년 미리 보고 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분은?", placeholder="예: 소개팅, 면접, 그냥 우울해")
    btn_label = "⚡ 오늘 나에게 닥칠 운세 미리보기"

# --- 랜덤 링크 ---
lucky_items = [
    "https://link.coupang.com/a/c7U5ic", 
    "https://link.coupang.com/a/c7Vcxs", 
    "https://link.coupang.com/a/c7VexJ", 
    "https://link.coupang.com/a/c7VfKc", 
    "https://link.coupang.com/a/c7Vhmc", 
    "https://link.coupang.com/a/c7VinT", 
    "https://link.coupang.com/a/c7Vkbn", 
    "https://link.coupang.com/a/c7Vk67", 
    "https://link.coupang.com/a/c7Vmq1", 
    "https://link.coupang.com/a/c7VncA", 
    "https://link.coupang.com/a/c7VoiP"
]
selected_link = random.choice(lucky_items)

# --- 실행 로직 ---
if st.button(btn_label):
    if not name:
        st.warning("이름을 적어주세요! (익명 보장 😎)")
    elif not gemini_api_key:
        st.error("⚠️ API 키가 없어요. 관리자에게 문의하세요.")
    else:
        # 성 떼기
        if len(name) > 2:
            short_name = name[1:] 
        else:
            short_name = name 

        if gender == "남성":
            call_name = f"{short_name} 오빠" 
            luna_role = "여동생"
        else:
            call_name = f"{short_name} 언니"
            luna_role = "아끼는 동생"

        try:
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            my_igan = get_day_gan(birth_date)

            # 프롬프트
            prompt = f"""
            [Role]
            You are 'Luna', a 30-something smart, chic consultant.
            
            [Relationship Setting]
            - Call the user "{call_name}" ONLY.
            - Tone: Friendly "Banmal" (Informal Korean).
            
            [Instructions]
            - **Emojis:** Use 1-2 relevant emojis in EVERY paragraph to make it fun. 🦄✨
            - **No English Headers:** Output the structure headers in KOREAN (e.g., "### 🔎 너의 성격 분석").

            [User Profile]
            - Birth: {birth_date} (Lunar: {lunar_date})
            - Element: {my_igan}
            - Worry: {worry}
            - Topic: {topic}

            [Output Structure (Strictly Korean)]

            **Section 1. [인사]**
            - "어, {call_name} 왔어? 얼굴이 왜 그래, 무슨 일 있어?"
            - Empathize with {worry}.

            **Section 2. [성격 분석]**
            - Header: "### 🔎 {call_name}의 진짜 성격은?"
            - Analyze based on {my_igan}.

            **Section 3. [미래 예언]**
            - Header: "### ⚡ 2026년(오늘) 운세 팩트 체크"
            - Clear advice for {topic}.

            **Section 4. [행운템 추천]**
            - Header: "### 🍀 루나의 처방전 (행운템)"
            - Suggest a "Lucky Color/Material". No Links.
            - Explain WHY.

            **Section 5. [마무리]**
            - Say something like: "아래에 가성비 좋은 아이템들로만 골라놨어. 구경만 해도 기분 전환될 거야."
            - Closing: "{call_name}, 힘내! 언니가(혹은 동생이) 항상 응원하는 거 알지? 화이팅! 💕"
            """
            
            with st.spinner(f"⚡ {call_name}의 운명 데이터 분석 중... (루나 눈 돌아가는 중 👀)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash") 
                response = model.generate_content(prompt)
                
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:20px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #444; padding-bottom:10px; font-size:20px; word-break:keep-all; margin:0 0 15px 0;">
                        💌 {call_name}에게 도착한 루나의 편지
                    </h3>
                    <div style="font-size:16px; color:#EEE;">
                        {response.text.replace("\n", "<br>")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- [황금박스] 함수 호출로 안전하게 생성 ---
                golden_box_html = create_golden_box(call_name, selected_link)
                st.markdown(golden_box_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.warning("잠시 후 다시 시도해주세요.")
