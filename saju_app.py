import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - FINAL PERFECT VERSION]
# "마크 완전 박멸 + 고대비 가독성 + 킬링 멘트 장착"
# ==========================================

# 1. 페이지 설정 (반드시 코드 맨 윗줄)
st.set_page_config(
    page_title="루나 : 운명 설계사", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. [천재 쌤의 디자인 솔루션] CSS (수정 금지)
st.markdown("""
<style>
    /* 폰트 불러오기 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    /* 전체 폰트 및 스타일 설정 (시니어 가독성 UP) */
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 22px !important; 
        font-weight: 500;
    }

    /* 배경 리얼 블랙 */
    .stApp {
        background-color: #0E0E0E;
        color: #FFFFFF;
    }
    
    /* --------------------------------------------------------
       [1] 끈질긴 마크/배지 완벽 제거 (Wildcard Hack)
       -------------------------------------------------------- */
    
    /* 헤더, 툴바, 데코레이션 삭제 */
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* 우측 상단 뷰어 배지 (이름이 뭐든 'viewerBadge'가 포함되면 삭제) */
    div[class*="viewerBadge"] {
        display: none !important;
    }
    
    /* 하단 푸터 및 Deploy 버튼 삭제 */
    footer, .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 상단 여백 제거 (화면 꽉 차게) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* --------------------------------------------------------
       [2] 입력창 가독성 심폐소생술 (고대비 모드)
       -------------------------------------------------------- */
    
    /* 질문(Label)은 무조건 흰색 & 크게 */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stRadio label {
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
    /* 입력 예시(Placeholder)는 밝은 회색으로 잘 보이게 */
    input::placeholder {
        color: #AAAAAA !important; 
        opacity: 1 !important;
    }
    
    /* 입력칸 디자인 */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #222 !important; 
        color: #FFF !important; 
        border: 2px solid #666 !important;
        height: 65px !important;
        font-size: 22px !important;
        border-radius: 10px;
        text-align: center;
    }
    
    /* 라디오 버튼 글씨 */
    div[role="radiogroup"] label p {
        font-size: 22px !important;
        font-weight: bold !important;
    }

    /* --------------------------------------------------------
       [3] UI 컴포넌트 디자인
       -------------------------------------------------------- */
    
    /* 메인 타이틀 */
    .main-title {
        color: #E5C17C;
        font-weight: 900;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 5px;
        text-shadow: 0 0 20px rgba(229, 193, 124, 0.4);
    }
    .sub-title {
        color: #BBB;
        text-align: center;
        font-size: 1.4rem;
        margin-bottom: 30px;
    }
    
    /* 실행 버튼 */
    .stButton > button {
        width: 100%;
        background-color: #333;
        color: #E5C17C;
        border: 2px solid #E5C17C;
        height: 80px !important;
        font-size: 24px !important;
        font-weight: 900;
        border-radius: 12px;
        margin-top: 20px;
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
        border: 3px solid #D4AF37;
        border-radius: 15px;
        padding: 30px;
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
        font-size: 22px;
        padding: 25px 0;
        border-radius: 12px;
        text-decoration: none;
        margin-top: 20px;
        animation: heartbeat 1.5s infinite ease-in-out;
    }
    
    .footer-note {
        font-size: 14px; color: #777; text-align: center; margin-top: 60px;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 (API 키 관리) ---
with st.sidebar:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 화면 구성 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>(사이다 버전 🥤)</div>", unsafe_allow_html=True)

# 인트로
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6; font-size: 18px; color: #DDD;'>
    "혼자 끙끙 앓지 마요."<br>
    루나 언니가 당신의 미래와 해결책을<br> 
    <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF5555; font-weight:bold;'>(※ 팩폭 주의 🚨)</span>
</div>
""", unsafe_allow_html=True)

# 가격표 (복채 유도 멘트 수정됨)
st.markdown("""
<a href="https://www.threads.net/@luna_fortune_2026" target="_blank" style="text-decoration:none;">
    <div style="background:#181818; border:1px solid #444; border-radius:15px; padding:20px; text-align:center; margin-bottom:40px;">
        <span style="color:#777; text-decoration:line-through; font-size:18px;">상담료 50,000원</span><br>
        <span style="color:#FFD700; font-size:26px; font-weight:bold;">✨ 지금만 무료 (0원)</span><br>
        <div style="margin-top:15px; color:#EEE; font-size:18px;">
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

# 고민 입력창 (예시 문구 대폭 수정됨)
if "2026" in topic:
    worry = st.text_input("가장 큰 고민은?", placeholder="예: 남편이 바람난거같아요, 돈을 언제 벌수있을까요?, 친구랑 계속 싸워요")
    btn_label = "두근두근 💓 2026년 미리 보고 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분은?", placeholder="예: 소개팅 하는데 잘 될까요? 면접이 있어요.")
    # 버튼 멘트 수정됨 (오늘 나에게 닥칠 운세 미리보기)
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
            
            prompt = f"""
            [Role]
            Act as 'Luna', a charismatic fortune teller.
            [User Info]
            Name: {name} ({gender}), Birth: {birth_date} (Lunar: {lunar_date})
            Topic: {topic}, Worry: {worry}
            [Guideline]
            Tone: Friendly but Fact-bombing. Use Korean.
            Structure: 
            1. Current State (Shocking accuracy) 
            2. Future Prediction (What will happen)
            3. Actionable Solution (Clear advice).
            Use emojis.
            """
            
            with st.spinner("⚡ 루나 언니가 운명 스캔 중... (심장이 쿵!)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                
                # 결과 박스
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:30px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #333; padding-bottom:10px;">📜 {name}님 운명 분석표</h3>
                    {response.text}
                </div>
                """, unsafe_allow_html=True)
                
                # 황금박스 (쿠팡)
                st.markdown(f"""
                <div class="golden-box">
                    <h3 style="color:#FF6B6B; margin:0; font-size:24px;">🚨 {name}님, 긴급 처방!</h3>
                    <p style="margin-top:15px; font-size:18px; color:#DDD;">
                        "지금 당신에게 <b>2%% 부족한 기운</b>을<br>
                        채워줄 <b>'생존템'</b>입니다."
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:20px 0; color:#CCC; font-size:16px;">
                        루나 언니가 엄선한 <b>'갓성비 행운템'</b>!<br>
                        <b>눈도장</b>만 찍고 가도 기운이 확 달라질 거예요.
                    </div>
                    <a href="{selected_link}" target="_blank" class="pulse-button">
                        👉 내 행운템 확인하러 가기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error("접속자가 많아 루나 언니가 바쁘네요! 잠시 후 다시 눌러주세요.")

# 하단 문구
st.markdown("""
<div class="footer-note">
    이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.<br>
    (무료 상담 서비스를 유지하는 데 사용됩니다.)
</div>
""", unsafe_allow_html=True)
