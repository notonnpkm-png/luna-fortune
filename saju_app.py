import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - THE FINAL MASTERPIECE]
# "모바일 세로 화면 최적화 + 스레드 감성 찐언니 페르소나 탑재"
# ==========================================

# 1. 페이지 기본 설정 (무조건 맨 위)
st.set_page_config(
    page_title="루나 : 운명 상담소",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. [디자인] CSS 최종 보스 (수정 금지)
st.markdown("""
<style>
    /* 폰트 불러오기 (명조체) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    /* 전체 기본 폰트 설정 (기본 사이즈도 살짝 줄임) */
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 22px !important; /* 18px -> 22px 확대 */
        font-weight: 500;
    }

    /* 배경: 리얼 블랙 */
    .stApp {
        background-color: #0E0E0E;
        color: #FFFFFF;
    }
    
    /* --------------------------------------------------------
       [1] 방해꾼들(아이콘/배지) 핵폭탄 삭제 구역
       -------------------------------------------------------- */
    
    /* 상단 헤더, 툴바, 데코레이션 삭제 - 더 강력하게 타겟팅 */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* 우측 상단 뷰어 배지 (Avatar Icon) 및 각종 버튼 - 와일드카드로 강력 삭제 */
    div[class*="viewerBadge"], .viewerBadge_container__1QSob, 
    button[kind="header"], [data-testid="baseButton-header"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    
    /* 우측 하단 'Streamlit' 아이콘 (Running Man) & 상태 위젯 */
    [data-testid="stStatusWidget"], footer, .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 상단 여백 제거 (화면 꽉 차게) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* --------------------------------------------------------
       [2] 텍스트 가독성 (제자님 지침 완벽 반영)
       -------------------------------------------------------- */
    
    /* 카테고리 제목 (이름, 생년월일 등) -> 진한 흰색 + 굵게 */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stRadio label, div[role="radiogroup"] label p {
        color: #FFFFFF !important;
        font-size: 18px !important; /* 사이즈 축소 */
        font-weight: 700 !important; /* Bold */
    }
    
    /* 입력 예시 (Placeholder) -> 흰색 + 굵기 보통 */
    input::placeholder {
        color: #FFFFFF !important; 
        opacity: 0.7 !important; /* 너무 쨍하면 헷갈리니 살짝 투명도 */
        font-weight: 400 !important; /* Normal */
    }
    
    /* 입력칸 디자인 */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #222 !important; 
        color: #FFF !important; 
        border: 2px solid #555 !important;
        height: 55px !important; /* 높이도 살짝 줄임 */
        font-size: 18px !important;
        border-radius: 10px;
        text-align: center;
    }

    /* --------------------------------------------------------
       [3] UI 컴포넌트 디자인 (모바일 최적화 Ver.)
       -------------------------------------------------------- */
    
    /* 메인 타이틀 (한 줄에 쏙 들어오게 축소) */
    .main-title {
        color: #E5C17C;
        font-weight: 900;
        text-align: center;
        font-size: 1.5rem; /* 1.8rem -> 1.5rem (완벽한 한 줄) */
        margin-bottom: 5px;
        text-shadow: 0 0 15px rgba(229, 193, 124, 0.3);
        word-break: keep-all; /* 단어 중간에 끊기지 않게 */
    }
    .sub-title {
        color: #BBB;
        text-align: center;
        font-size: 1.0rem; /* 축소 */
        margin-bottom: 25px;
    }

    /* 가격표(복채) 박스 스타일 - 골드 테두리 + 글자 축소 */
    .price-box {
        background-color: #181818;
        border: 2px solid #E5C17C; /* 금색 테두리 적용 */
        border-radius: 15px;
        padding: 15px; /* 패딩 축소 */
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(229, 193, 124, 0.15);
        transition: transform 0.2s;
    }
    .price-box:active {
        transform: scale(0.98);
        border-color: #FFD700;
    }
    
    /* 실행 버튼 */
    .stButton > button {
        width: 100%;
        background-color: #222;
        color: #E5C17C;
        border: 2px solid #E5C17C;
        height: 70px !important;
        font-size: 20px !important; /* 버튼 글씨 축소 */
        font-weight: 900;
        border-radius: 12px;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #E5C17C;
        color: #000;
        border-color: #FFF;
    }

    /* 황금박스 & 심장박동 애니메이션 */
    @keyframes heartbeat {
        0% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
        50% { transform: scale(1.02); box-shadow: 0 0 25px rgba(255, 215, 0, 0.5); }
        100% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
    }
    .golden-box {
        background-color: #1A1A1A;
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 25px; /* 패딩 축소 */
        margin-top: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .pulse-button {
        display: block;
        width: 100%;
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        color: #000 !important;
        font-weight: 900;
        font-size: 18px; /* 버튼 텍스트 축소 (줄바꿈 방지) */
        padding: 20px 0;
        border-radius: 12px;
        text-decoration: none;
        margin-top: 15px;
        animation: heartbeat 1.5s infinite ease-in-out;
        word-break: keep-all; /* 단어 뭉침 유지 */
    }
    
    .footer-note {
        font-size: 12px; color: #666; text-align: center; margin-top: 60px;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 (API 키 관리 - 평소엔 안 보임) ---
with st.sidebar:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 화면 구성 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>(사이다 버전 🥤)</div>", unsafe_allow_html=True)

# 인트로 (공감 + 팩폭 예고)
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6; font-size: 16px; color: #DDD;'>
    "혼자 끙끙 앓지 마요."<br>
    루나 언니가 당신의 미래와 해결책을<br> 
    <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF5555; font-weight:bold;'>(※ 팩폭 주의 🚨)</span>
</div>
""", unsafe_allow_html=True)

# 가격표 (글씨 사이즈 모바일 최적화)
st.markdown("""
<a href="https://www.threads.net/@luna_fortune_2026" target="_blank" style="text-decoration:none;">
    <div class="price-box">
        <span style="color:#777; text-decoration:line-through; font-size:14px;">상담료 50,000원</span><br>
        <span style="color:#FFD700; font-size:21px; font-weight:bold;">✨ 지금만 무료 (0원)</span><br>
        <div style="margin-top:10px; color:#EEE; font-size:14px;">
            ⚠️ <b>주의:</b> 복채 대신 <b>'팔로우', '댓글'</b>은 필수!!<br>
            <span style="color:#FFD700;">(복채 안내면 상담 효과없는거 아시죠?^^)</span>
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

# 고민 입력창 (제자님 확정 자극적 예시 적용)
if "2026" in topic:
    worry = st.text_input("가장 큰 고민은?", placeholder="예: 남편이 바람난거같아요, 돈을 언제 벌수있을까요?, 친구랑 계속 싸워요")
    btn_label = "두근 💓 2026년 미리 보고 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분은?", placeholder="예: 소개팅 하는데 잘 될까요? 면접이 있어요.")
    # 버튼 멘트 (확정)
    btn_label = "⚡ 오늘 나에게 닥칠 운세 미리보기"

# --- 랜덤 행운템 리스트 ---
lucky_items = [
    "https://link.coupang.com/a/c7U5ic", "https://link.coupang.com/a/c7Vcxs", 
    "https://link.coupang.com/a/c7VexJ", "https://link.coupang.com/a/c7VfKc", 
    "https://link.coupang.com/a/c7Vhmc", "https://link.coupang.com/a/c7VinT", 
    "https://link.coupang.com/a/c7Vkbn", "https://link.coupang.com/a/c7Vk67", 
    "https://link.coupang.com/a/c7Vmq1", "https://link.coupang.com/a/c7VncA", 
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
        try:
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            # [수정] 성별에 따른 호칭 동적 설정 (남성 -> 누나, 여성 -> 언니)
            if gender == "남성":
                my_title = "누나"
            else:
                my_title = "언니"

            # --- [핵심] 40대 찐언니/누나 페르소나 (V2: 스레드 감성 완벽 이식) ---
            prompt = f"""
            [Role]
            You are 'Luna', a cool, stylish, and affectionate 40-something older sister ({my_title}).
            You are NOT a boring fortune teller. You are a life mentor who speaks blunt truths but deeply cares about your younger siblings (the user).
            
            [Target Audience]
            Women/Men in their 30s who are stressed about money, career, and relationships. They hate cliché advice.
            
            [Tone & Manner - "Thread Style"]
            1. **Speech Level:** Use "Banmal" (Informal/Casual Korean) for the entire conversation like a close sister. (e.g., "왔어?", "그랬구나.", "이건 진짜 아니야.")
            2. **Addressing Rule (CRITICAL):** - Even though you use Banmal, **ALWAYS address the user as "{FirstName}님"** (Remove the surname and add '님').
               - **Example:** If input is "박경미", call her **"경미님"** (NOT "경미야", NOT "박경미씨", NOT "박경미님").
               - Mix with "우리 동생".
               - **Opening:** "우리 동생, {name}에서 성 빼고 이름+님 왔어?" (e.g. "우리 동생, 경미님 왔어?")
            3. **Direct & Provocative:** Don't be vague. 
               - Bad: "Realtionships might be difficult."
               - Good: "남자는 좀 꼬이는데, 실속이 없어. 정신 똑바로 차려야 해."
            4. **Empathy but Fact-Bombing:** Start with empathy ("Aigo, so hard right?"), then hit them with facts ("But honestly, you are too stubborn.").

            [Output Structure - STRICTLY FOLLOW THIS FORMAT]
            
            **1. Intro**
            - Start with: "우리 동생, **[Name]님** 왔어? 요즘 {worry} 때문에 머리 좀 아팠겠네." (Make sure to remove surname for [Name]님).
            - Empathize with their specific situation briefly. "마음이 싱숭생숭하지? {my_title}가 시원하게 긁어줄게."
            
            **2. 🔥 팩트 진단 (Personality)**
            - Analyze their personality using Saju elements (Wood, Fire, etc.) but use **METAPHORS**.
            - Example: "우리 **[Name]님**은 봄날의 큰 소나무(甲木) 같은 사람이야."
            - **Contrast:** Mention their outer strength vs. inner stress/weakness. "겉으론 쿨한 척 해도 속으론 끙끙 앓지? 너 맘 여린 거 {my_title}는 다 보여."
            
            **3. 🔮 미래 예언 ({topic})**
            - Give a clear verdict.
            - **Money/Career:** Hot or Cold? (e.g., "돈? 아주 좋아! 그냥 질러.")
            - **Family/Health/Love:** Red light or Green light? (e.g., "근데 연애는 좀 꽝이야.", "건강은 '번아웃' 조심해.")
            - Use terms like "{my_title}가 보증할게", "이게 문제야", "정신 똑바로 차려".
            
            **4. 💋 {my_title}의 코디 추천 (Solution)**
            - Give a specific **Real-world Item** based on their missing element.
            - Format: **추천 아이템: [Color] [Item Name]** (e.g., 블랙 가죽 다이어리, 레드 립스틱, 메탈 시계)
            - Explain WHY based on Saju elements (e.g., "You have too much Fire, so you need Black (Water) to cool it down.").
            - Closing: "우리 동생, 기 죽지 마. {my_title}가 항상 응원한다. 알았지?"

            [User Info]
            Name: {name} ({gender})
            Birth: {birth_date} (Lunar: {lunar_date})
            Topic: {topic}
            Concern: {worry}
            """
            
            with st.spinner(f"⚡ 루나 {my_title}가 신기 돋는 눈으로 스캔 중... (찌릿!)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                
                # 결과 박스 (가독성 UP + 제목 줄바꿈 방지)
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:30px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #333; padding-bottom:10px; font-size:20px; word-break:keep-all; margin:0 0 10px 0;">📜 {name}님을 위한 {my_title}의 독설 & 애정</h3>
                    {response.text}
                </div>
                """, unsafe_allow_html=True)
                
                # 황금박스 (쿠팡)
                st.markdown(f"""
                <div class="golden-box">
                    <h3 style="color:#FF6B6B; margin:0; font-size:24px;">🚨 {name}님, 이거 하나만 챙겨!</h3>
                    <p style="margin-top:15px; font-size:18px; color:#DDD;">
                        "2026년, 너의 <b>'폼'</b>을 살려줄<br>
                        <b>{my_title}의 원픽 생존템</b>이야."
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:20px 0; color:#CCC; font-size:16px;">
                        비싼 굿즈 필요 없어.<br>
                        <b>이거 하나면 기운 확 달라진다.</b> 믿어봐.
                    </div>
                    <a href="{selected_link}" target="_blank" class="pulse-button">
                        👉 {my_title}가 골라준 행운템 보기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"접속자가 많아 루나 {my_title}가 바쁘네요! 잠시 후 다시 눌러주세요.")

# 하단 문구
st.markdown("""
<div class="footer-note">
    이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.<br>
    (무료 상담 서비스를 유지하는 데 사용됩니다.)
</div>
""", unsafe_allow_html=True)
