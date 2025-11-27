import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - THE FINAL MASTERPIECE]
# "모바일 세로 화면 최적화 + 스레드 감성 찐언니 페르소나 탑재"
# "깃허브 배지 삭제(Clean Ver.) + 쿠팡 랜덤 보물찾기 로직 적용"
# ==========================================

# 1. 페이지 기본 설정 (무조건 맨 위)
st.set_page_config(
    page_title="루나 : 운명 상담소",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. [디자인] CSS 최종 보스 (깃허브 배지 삭제 포함)
st.markdown("""
<style>
    /* 폰트 불러오기 (명조체 - 신뢰감 & 고급짐) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    /* 전체 기본 폰트 및 배경 설정 */
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 20px !important; 
        font-weight: 500;
        background-color: #0E0E0E; /* 리얼 블랙 */
        color: #FFFFFF;
    }

    /* --------------------------------------------------------
       [핵심] 방해꾼들(아이콘/배지/헤더/푸터) 완벽 제거 구역
       -------------------------------------------------------- */
    /* 상단 헤더, 햄버거 메뉴, 데코레이션 바 삭제 */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* ★ 하단 깃허브/스트림릿 배지(Viewer Badge) 삭제 ★ */
    /* 클래스 이름이 바뀌어도 걸리도록 와일드카드 사용 */
    div[class*="viewerBadge"] {
        display: none !important;
        visibility: hidden !important;
    }
    .viewerBadge_container__1QSob {
        display: none !important;
    }
    
    /* 기본 푸터 삭제 */
    footer {
        display: none !important;
        visibility: hidden !important;
    }
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }
    .stAppDeployButton {
        display: none !important;
    }

    /* 상단 여백 제거 (모바일 화면 넓게 쓰기) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 600px !important; /* 모바일 최적화 폭 제한 */
    }

    /* --------------------------------------------------------
       [UI] 텍스트 가독성 & 입력폼 디자인
       -------------------------------------------------------- */
    /* 라벨 색상 (골드) */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stRadio label, div[role="radiogroup"] label p {
        color: #E5C17C !important;
        font-size: 16px !important; 
        font-weight: 700 !important; 
    }
    /* 입력창 스타일 */
    input::placeholder {
        color: #888 !important; 
        font-weight: 400 !important;
    }
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #1E1E1E !important; 
        color: #FFF !important; 
        border: 1px solid #444 !important;
        height: 50px !important;
        font-size: 16px !important;
        border-radius: 8px;
        text-align: center;
    }
    .stTextInput input:focus, .stDateInput input:focus {
        border-color: #E5C17C !important;
    }

    /* --------------------------------------------------------
       [UI] 타이틀 및 버튼 디자인
       -------------------------------------------------------- */
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

    /* 가격표(복채) 박스 스타일 */
    .price-box {
        background-color: #181818;
        border: 1px solid #333;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* 실행 버튼 (그라데이션) */
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

    /* 황금박스 & 심장박동 애니메이션 */
    @keyframes heartbeat {
        0% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.1); }
        50% { transform: scale(1.02); box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
        100% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.1); }
    }
    .golden-box {
        background-color: #1A1A1A;
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 25px 20px;
        margin-top: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
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
        margin-top: 15px;
        animation: heartbeat 1.5s infinite ease-in-out;
        word-break: keep-all;
    }
    
    /* 쿠팡 안전 문구 (회색, 작게 - 필수!) */
    .coupang-notice {
        font-size: 11px;
        color: #555;
        text-align: center;
        margin-top: 15px;
        letter-spacing: -0.5px;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- [천재 작가의 두뇌] 일간(Day Stem) 계산 함수 ---
def get_day_gan(birth_date):
    # 기준일: 2000년 1월 1일은 '무오(戊午)'일 (천간: 무(戊) -> index 4)
    ref_date = datetime.date(2000, 1, 1)
    ref_gan_idx = 4 
    gan_list = ["갑(甲, 큰 나무)", "을(乙, 꽃/덩굴)", "병(丙, 태양)", "정(丁, 촛불)", "무(戊, 큰 산)", 
                "기(己, 밭/대지)", "경(庚, 바위/도끼)", "신(辛, 보석/칼)", "임(壬, 바다)", "계(癸, 빗물)"]
    delta_days = (birth_date - ref_date).days
    gan_idx = (ref_gan_idx + delta_days) % 10
    return gan_list[gan_idx]

# --- 사이드바 (API 키 관리 - 평소엔 숨겨짐) ---
with st.sidebar:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 화면 구성 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>(🥤 사이다 예언 맛집 🍿)</div>", unsafe_allow_html=True)

# 인트로
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6; font-size: 15px; color: #CCC;'>
    "혼자 끙끙 앓지 마요."<br>
    루나 언니가 당신의 미래와 해결책을<br> 
    <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF5555; font-weight:bold;'>(※ 팩폭 주의 🚨)</span>
</div>
""", unsafe_allow_html=True)

# 가격표 (링크트리 등 SNS 연결 유도) - 버튼 클릭 시 새창
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
    name = st.text_input("이름 (본명)", placeholder="예: 박경미")
with col2:
    gender = st.radio("성별", ["여성", "남성"], horizontal=True)

birth_date = st.date_input(
    "생년월일",
    min_value=datetime.date(1940, 1, 1),
    value=datetime.date(1990, 1, 1)
)
birth_time = st.time_input("태어난 시간 (모르면 패스)", datetime.time(9, 00))

st.markdown("<br>", unsafe_allow_html=True)

# 고민 입력창
if "2026" in topic:
    worry = st.text_input("가장 큰 고민은?", placeholder="예: 돈, 사업, 남편, 건강 등 (짧게)")
    btn_label = "두근 💓 2026년 미리 보고 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분은?", placeholder="예: 소개팅, 면접, 그냥 우울해")
    btn_label = "⚡ 오늘 나에게 닥칠 운세 미리보기"

# --- [대표님의 황금열쇠] 랜덤 쿠팡 링크 리스트 ---
# (대표님이 가지고 계신 파트너스 링크들 - 여기에 본인 링크 추가/수정 가능)
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
        # 1. 호칭 설정 (언니/누나)
        if gender == "남성":
            my_title = "누나"
        else:
            my_title = "언니"

        try:
            # 2. 날짜 계산 & 일간(Day Stem) 추출
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            my_igan = get_day_gan(birth_date)

            # 3. [천재적 프롬프트 설계] 루나 페르소나 (30대 골드미스 ver.)
            prompt = f"""
            [Role]
            You are 'Luna', a 30-something successful, chic, and rich 'Gold Miss' (Unnie/Noona).
            You run a famous consulting shop in Cheongdam-dong.
            You combine Traditional Saju (Five Elements) with Modern Psychology.
            
            [Tone & Manner]
            - **Cool & Direct:** Speak like a close, confident sister. Use "Banmal" (Informal Korean).
            - **Not Condescending:** Do NOT treat the user like a child. Treat them like a younger sibling or friend you care about.
            - **Mix:** 70% Fact Bomb (Rational) + 30% Warmth (Emotional Support).
            - **Keywords:** "야," "있잖아," "내 말 잘 들어," "솔직히 말해서," "언니 믿지?"

            [User Profile]
            - Name: {name} ({gender})
            - Birth: {birth_date} (Lunar: {lunar_date})
            - **Core Element (Ilgan): {my_igan}** <--- Use this for personality analysis.
            - Worry: {worry}
            - Topic: {topic}

            [Output Structure]

            **1. [Greeting & Hook]**
            - "어, {name} 왔어? 얼굴이 왜 그래, 무슨 일 있어?" (Start naturally)
            - Acknowledge the {worry} with empathy but sharpness.

            **2. [Personality Analysis (Based on {my_igan})]**
            - Title: Use an Emoji + Short Impactful Title.
            - Analyze their nature using their element ({my_igan}).
            - E.g., If Fire: "Passion is good, but you burn out too fast."
            - **Cold Reading:** Guess a specific habit (e.g., "You act strong but cry alone at night").

            **3. [The Prediction (Focus on {topic})]**
            - Give a clear direction for 2026 (or Today).
            - Use **Strong Verbs**: "Make money," "Cut him off," "Go for it."
            - Mention specific months or directions if possible (make it sound professional).

            **4. [Luna's Secret Solution (Item Recommendation)]**
            - **CRITICAL:** Do NOT provide a specific URL.
            - **Concept:** Recommend a **"Lucky Color"**, **"Material"** (Gold, Wood, Metal), or **"Category"** (Perfume, Bedding, Accessory).
            - Explain WHY this item helps their Saju.
            - E.g., "Your energy is too cold. You need a 'Red' item or something 'Hot' to balance it."

            **5. [Closing]**
            - "I've picked out some items for you below. Go check them out before your luck runs out."
            - "Cheer up. I'm on your side."
            """
            
            # 로딩 중 메시지 (루나 스타일)
            with st.spinner(f"⚡ {name}의 운명 데이터 분석 중... (루나 언니가 신들린 눈으로 보는 중 👀)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash") 
                response = model.generate_content(prompt)
                
                # 결과 박스 (페르소나 리포트)
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:20px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #444; padding-bottom:10px; font-size:20px; word-break:keep-all; margin:0 0 15px 0;">
                        💌 {name}에게 도착한 루나의 독점 리포트
                    </h3>
                    <div style="font-size:16px; color:#EEE;">
                        {response.text.replace("\n", "<br>")}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 황금박스 (구매 유도 클라이맥스)
                st.markdown(f"""
                <div class="golden-box">
                    <h3 style="color:#FF6B6B; margin:0; font-size:22px; font-weight:900;">
                        🚨 {name}, 잠깐! 그냥 가면 손해!
                    </h3>
                    <p style="margin-top:15px; font-size:16px; color:#CCC;">
                        "방금 말한 그 <b>[행운템]</b>, 아무거나 사면 안 돼.<br>
                        {my_title}가 너를 위해 <b>기운 좋은 것들만</b> 모아놨어."
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:20px 0; color:#AAA; font-size:14px;">
                        👇 <b>아래 버튼 누르고 '보물찾기' 시작해!</b><br>
                        (너한테 딱 꽂히는 게 <b>진짜 네 물건</b>이야)
                    </div>
                    <a href="{selected_link}" target="_blank" class="pulse-button">
                        🚀 {my_title}의 [시크릿 행운템] 보러가기 (Click)
                    </a>
                    <div class="coupang-notice">
                        이 포스팅은 쿠팡 파트너스 활동의 일환으로,<br>
                        이에 따른 일정액의 수수료를 제공받습니다.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.warning("잠시 후 다시 시도해주세요. (서버가 폭주 중인가 봐요!)")
