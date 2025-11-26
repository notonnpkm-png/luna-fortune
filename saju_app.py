import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - FINAL REMASTER]
# "모든 꼬리표 삭제 + 시니어 가독성 최적화"
# ==========================================

# 1. 페이지 기본 설정 (가장 윗줄에 있어야 함)
st.set_page_config(
    page_title="루나 : 운명 설계사", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="collapsed" # 사이드바 숨김 출발
)

# 2. [핵심] 강력한 디자인 CSS (수정 금지)
st.markdown("""
<style>
    /* 폰트 불러오기 (고급스러운 명조체) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    /* [시니어 모드] 전체 글씨 크기 대폭 확대 */
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 20px !important; /* 기본 폰트 20px로 고정 (아주 큼) */
        font-weight: 500;
    }

    /* 배경색 리얼 블랙 */
    .stApp {
        background-color: #0E0E0E;
        color: #FFFFFF;
    }
    
    /* --------------------------------------------------------
       [1] 방해꾼들 완전 삭제 (Deploy 버튼, 햄버거, 푸터 등)
       -------------------------------------------------------- */
    header {visibility: hidden !important; height: 0px !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* 우측 상단 'Deploy', 'Manage app' 버튼 등 모든 툴바 삭제 */
    [data-testid="stToolbar"], 
    [data-testid="stHeader"], 
    .stAppDeployButton, 
    div[data-testid="stDecoration"],
    button[title="View app in Streamlit Cloud"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 혹시 모를 뷰어 배지(Viewer Badge) 타겟팅 삭제 */
    .viewerBadge_container__1QSob, 
    div[class^='viewerBadge_'] {
        display: none !important;
    }

    /* 상단 여백 제거 (화면 꽉 차게) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* --------------------------------------------------------
       [2] UI 요소 디자인 (타이틀, 버튼, 입력창)
       -------------------------------------------------------- */
    .main-title {
        color: #E5C17C;
        font-weight: 900;
        text-align: center;
        font-size: 2.8rem; /* 타이틀 더 크게 */
        margin-bottom: 5px;
        text-shadow: 0 0 15px rgba(229, 193, 124, 0.3);
    }
    .sub-title {
        color: #888;
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 30px;
    }
    
    /* 입력창 디자인 (시니어용 : 터치 영역 확대) */
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #222 !important;
        color: #fff !important;
        border: 1px solid #555 !important;
        height: 60px !important; /* 입력칸 높이 키움 */
        font-size: 20px !important; /* 입력 글씨 키움 */
        text-align: center;
        border-radius: 10px;
    }
    
    /* 버튼 디자인 */
    .stButton > button {
        width: 100%;
        background-color: #222;
        color: #E5C17C;
        border: 2px solid #E5C17C;
        height: 75px !important;
        font-size: 22px !important;
        font-weight: bold;
        border-radius: 12px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #E5C17C;
        color: #000;
        transform: scale(1.02);
    }

    /* 라디오 버튼 (선택지) 글씨 키우기 */
    .stRadio label {
        font-size: 20px !important;
        padding: 10px;
    }

    /* --------------------------------------------------------
       [3] 황금박스 심장박동 애니메이션 (간섭 방지)
       -------------------------------------------------------- */
    @keyframes heartbeat {
        0% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
        50% { transform: scale(1.03); box-shadow: 0 0 30px rgba(255, 215, 0, 0.6); }
        100% { transform: scale(1); box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }
    }
    
    .golden-box {
        background-color: #1A1A1A;
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 30px;
        margin-top: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
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
        animation: heartbeat 1.5s infinite ease-in-out; /* 심장박동 적용 */
        box-shadow: 0 5px 15px rgba(255, 140, 0, 0.4);
    }
    .pulse-button:hover {
        opacity: 0.9;
    }

    /* 쿠팡 파트너스 문구 (흐리게) */
    .footer-note {
        font-size: 14px;
        color: #555;
        text-align: center;
        margin-top: 50px;
        font-weight: 300;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 (관리자용, 평소엔 숨겨짐) ---
with st.sidebar:
    st.header("🔐 관리자 설정")
    # secrets에 키가 있으면 자동 사용, 없으면 입력창
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 타이틀 영역 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>(사이다 버전 🥤)</div>", unsafe_allow_html=True)

# --- 인트로 멘트 ---
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6;'>
    "혼자 끙끙 앓지 마요."<br>
    루나 언니가 당신의 미래와 해결책을<br> 
    <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF5555; font-size: 18px;'>(※ 팩폭 주의 🚨 유리멘탈 금지)</span>
</div>
""", unsafe_allow_html=True)

# --- 가격표 (복채 대신 팔로우) ---
st.markdown("""
<a href="https://www.threads.net/@luna_fortune_2026" target="_blank" style="text-decoration:none;">
    <div style="background:#161616; border:1px solid #444; border-radius:15px; padding:20px; text-align:center; margin-bottom:40px;">
        <span style="color:#888; text-decoration:line-through; font-size:18px;">상담료 50,000원</span><br>
        <span style="color:#FFD700; font-size:26px; font-weight:bold;">✨ 지금만 무료 (0원)</span><br>
        <div style="margin-top:15px; color:#DDD; font-size:16px;">
            ⚠️ <b>주의:</b> 복채 대신 <b>'팔로우', '댓글'</b>은 필수!!<br>
            (복채를 내야 효과가 최고인 거 아시죠? 😉)
        </div>
    </div>
</a>
""", unsafe_allow_html=True)

# --- 사용자 입력 폼 ---
# 운세 종류 선택
topic = st.radio(
    "어떤 운명이 궁금한가요?",
    ["⚡ 오늘의 운세", "🦄 2026년 1년 운세"],
    index=1,
    horizontal=True
)

st.markdown("---")

# 정보 입력
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름을 입력해주세요", placeholder="예: 이루나")
with col2:
    gender = st.radio("성별", ["여성", "남성"], horizontal=True)

birth_date = st.date_input(
    "생년월일",
    min_value=datetime.date(1940, 1, 1),
    value=datetime.date(1990, 1, 1)
)
birth_time = st.time_input("태어난 시간 (모르면 패스)", datetime.time(9, 00))

# 고민 입력
st.markdown("<br>", unsafe_allow_html=True)
if "2026" in topic:
    worry = st.text_input("지금 가장 답답한 문제는?", placeholder="예: 남편이 바람난거같아요!, 언제 돈 많이 벌수있을까요?")
    btn_label = "두근두근 💓 2026년 미리 보고, 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분이나 상황은?", placeholder="예: 중요한 미팅이 있어요. 소개팅이 있어요.")
    btn_label = "⚡ 오늘 내 운세, 직설적으로 확인하기!"

# --- 쿠팡 행운템 링크 리스트 (랜덤) ---
lucky_items = [
    "https://link.coupang.com/a/c7U5ic", "https://link.coupang.com/a/c7Vcxs", 
    "https://link.coupang.com/a/c7VexJ", "https://link.coupang.com/a/c7VfKc", 
    "https://link.coupang.com/a/c7Vhmc", "https://link.coupang.com/a/c7VinT", 
    "https://link.coupang.com/a/c7Vkbn", "https://link.coupang.com/a/c7Vk67", 
    "https://link.coupang.com/a/c7Vmq1", "https://link.coupang.com/a/c7VncA", 
    "https://link.coupang.com/a/c7VoiP"
]
selected_link = random.choice(lucky_items)

# --- 결과 분석 로직 ---
if st.button(btn_label):
    if not name:
        st.warning("이름을 입력해주셔야 제가 신통방통하게 맞추죠! 😎")
    elif not gemini_api_key:
        st.error("⚠️ 관리자 키가 설정되지 않았습니다.")
    else:
        try:
            # 음력 변환
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            # 프롬프트 설정 (제자님 요청 스타일 반영)
            prompt = f"""
            [Role]
            You are 'Luna', a charismatic and sharp fortune teller. 
            Analyze the user's fortune based on Saju (Four Pillars of Destiny).
            
            [User Data]
            Name: {name} ({gender})
            Birth: {birth_date} (Lunar: {lunar_date})
            Topic: {topic}
            Concern: {worry}
            
            [Output Guidelines]
            1. Language: Korean.
            2. Tone: Friendly but straightforward ("팩폭" style). Like a close older sister giving realistic advice.
            3. Structure:
               - 🌪️ 뼈 때리는 현상 분석 (Current State)
               - 🔮 냉정한 미래 예측 (Prediction)
               - 💊 사이다 해결책 (Actionable Advice)
            4. Formatting: Use emojis effectively. Use **bold** for emphasis. No long paragraphs.
            """
            
            with st.spinner("⚡ 루나 언니가 신들린 듯 분석 중입니다... (잠시만요!)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                
                # 1. 운세 결과 출력 박스
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:30px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #333; padding-bottom:10px;">📜 {name}님을 위한 분석표</h3>
                    {response.text}
                </div>
                """, unsafe_allow_html=True)
                
                # 2. 황금박스 (심장박동 애니메이션 적용)
                st.markdown(f"""
                <div class="golden-box">
                    <h3 style="color:#FF6B6B; margin:0; font-size:24px;">🚨 {name}님, 긴급 처방입니다!</h3>
                    <p style="margin-top:15px; font-size:18px; color:#DDD;">
                        "이 물건은 당신에게 지금 딱 <b>2% 부족한 기운</b>을<br>
                        채워줄 <b>'생존템'</b>입니다."
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:20px 0; color:#CCC; font-size:16px;">
                        요즘 사는 게 참 만만치 않죠?<br>
                        그래서 루나 언니가 <b>'갓성비 아이템'</b>으로 골라놨어요!<br>
                        내 행운템이 뭔지 <b>눈도장</b>만 찍고 가도 기운이 확 달라질 거예요.
                    </div>
                    <a href="{selected_link}" target="_blank" class="pulse-button">
                        👉 내 운명에 '강력한 행운템' 보러가기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"접속자가 폭주하여 잠시 연결이 지연되고 있어요. 다시 한번 눌러주세요! ({e})")

# --- 하단 문구 ---
st.markdown("""
<div class="footer-note">
    이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.<br>
    (무료 상담 서비스를 유지하는 데 사용됩니다.)
</div>
""", unsafe_allow_html=True)
