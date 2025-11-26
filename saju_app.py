import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - THE FINAL MASTERPIECE]
# "모바일 세로 화면 최적화 + 스레드 감성 찐언니 페르소나 탑재"
# "천재 작가 & 심리 닥터의 영혼 주입 버전"
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
    
    /* 전체 기본 폰트 설정 */
    html, body, [class*="css"] {
        font-family: 'Noto Serif KR', serif;
        font-size: 22px !important; 
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
    header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    div[class*="viewerBadge"], .viewerBadge_container__1QSob, 
    button[kind="header"], [data-testid="baseButton-header"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    [data-testid="stStatusWidget"], footer, .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* --------------------------------------------------------
       [2] 텍스트 가독성
       -------------------------------------------------------- */
    .stTextInput label, .stDateInput label, .stTimeInput label, .stRadio label, div[role="radiogroup"] label p {
        color: #FFFFFF !important;
        font-size: 18px !important; 
        font-weight: 700 !important; 
    }
    input::placeholder {
        color: #FFFFFF !important; 
        opacity: 0.7 !important; 
        font-weight: 400 !important;
    }
    .stTextInput input, .stDateInput input, .stTimeInput input {
        background-color: #222 !important; 
        color: #FFF !important; 
        border: 2px solid #555 !important;
        height: 55px !important;
        font-size: 18px !important;
        border-radius: 10px;
        text-align: center;
    }

    /* --------------------------------------------------------
       [3] UI 컴포넌트 디자인 (모바일 최적화 Ver.)
       -------------------------------------------------------- */
    .main-title {
        color: #E5C17C;
        font-weight: 900;
        text-align: center;
        font-size: 1.5rem;
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
        border: 2px solid #E5C17C;
        border-radius: 15px;
        padding: 15px;
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
        font-size: 20px !important;
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
        padding: 25px;
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
        font-size: 18px;
        padding: 20px 0;
        border-radius: 12px;
        text-decoration: none;
        margin-top: 15px;
        animation: heartbeat 1.5s infinite ease-in-out;
        word-break: keep-all;
    }
    
    .footer-note {
        font-size: 12px; color: #666; text-align: center; margin-top: 60px;
    }
</style>
""", unsafe_allow_html=True)

# --- [천재 작가의 두뇌] 일간(Day Stem) 계산 함수 ---
# "너는 나무야"라고 정확히 말해주기 위한 핵심 로직
def get_day_gan(birth_date):
    # 기준일: 2000년 1월 1일은 '무오(戊午)'일 (천간: 무(戊) -> index 4)
    ref_date = datetime.date(2000, 1, 1)
    ref_gan_idx = 4 # 갑(0), 을(1), 병(2), 정(3), 무(4)...
    
    gan_list = ["갑(甲, 큰 나무)", "을(乙, 꽃/덩굴)", "병(丙, 태양)", "정(丁, 촛불)", "무(戊, 큰 산)", 
                "기(己, 밭/대지)", "경(庚, 바위/도끼)", "신(辛, 보석/칼)", "임(壬, 바다)", "계(癸, 빗물)"]
    
    delta_days = (birth_date - ref_date).days
    gan_idx = (ref_gan_idx + delta_days) % 10
    return gan_list[gan_idx]

# --- 사이드바 (API 키 관리) ---
with st.sidebar:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("Gemini API Key 입력", type="password")

# --- 메인 화면 구성 ---
st.markdown("<div class='main-title'>루나 : 운명 상담소</div>", unsafe_allow_html=True)
# [요청 반영] 서브 타이틀 수정
st.markdown("<div class='sub-title'>(🥤 사이다 예언 맛집 🍿)</div>", unsafe_allow_html=True)

# 인트로
st.markdown("""
<div style='text-align: center; margin-bottom: 30px; line-height: 1.6; font-size: 16px; color: #DDD;'>
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

# 고민 입력창
if "2026" in topic:
    worry = st.text_input("가장 큰 고민은?", placeholder="예: 남편이 바람난거같아요, 돈을 언제 벌수있을까요?, 친구랑 계속 싸워요")
    btn_label = "두근 💓 2026년 미리 보고 해결책 찾기!"
else:
    worry = st.text_input("오늘 기분은?", placeholder="예: 소개팅 하는데 잘 될까요? 면접이 있어요.")
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
        # 1. 호칭 설정
        if gender == "남성":
            my_title = "누나"
        else:
            my_title = "언니"

        try:
            # 2. 날짜 계산 & 일간(Day Stem) 추출
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            # [핵심] 일간 계산: 사용자의 타고난 기운을 정확히 파악
            my_igan = get_day_gan(birth_date)

            # 3. [천재적 프롬프트 설계] 심리학적 콜드 리딩(Cold Reading) + 팩트 폭격 + 욕망 자극
            prompt = f"""
            [Role]
            You are 'Luna', a 40-something '{my_title}' who is a genius at reading people's minds.
            You combine Traditional Saju analysis with Modern Psychology (Cold Reading).
            You speak like a very close, cool, and blunt sister/noona.

            [User Profile]
            - Name: {name} ({gender})
            - Birth: {birth_date} (Lunar: {lunar_date})
            - **Core Element (Ilgan): {my_igan}** <--- CRITICAL: Build your character analysis on this.
            - Worry: {worry}
            - Topic: {topic}

            [Tone & Manner: "The Thread/Twitter Vibe"]
            - **Informal (Banmal):** "왔어?", "그랬구나.", "이건 진짜 아니야."
            - **Naming:** Call user "{name}에서 성 빼고 이름+님" (e.g., "경미님") mixed with "우리 동생".
            - **Style:** - Don't be polite. Be real. 
              - Use rhetorical questions: "내 말 틀려? 맞아, 아니야?"
              - **Hyper-Realistic:** Talk about real life scenarios (Netflix, Instagram, late-night snacks, office politics).

            [Structure & Content Instructions]

            **(Start immediately with Greeting)**
            "우리 동생, **[Name]님** 왔어? {worry} 때문에 요즘 잠도 제대로 못 잤지? {my_title}가 보니까 딱 답이 나오네."

            ### 🔥 팩트 진단: [Create a catchy Title like "겉은 장군감, 속은 두부멘탈"]
            (Analyze personality based on '{my_igan}'. Use **Cold Reading** technique.)
            - "너는 **{my_igan}**의 기운을 타고났어." (Explain what this means metaphorically).
            - **Guess specific habits:** - If Fire: "욱해서 질러놓고 밤에 이불킥 하지?"
              - If Water: "남들 고민은 다 들어주면서 정작 네 속얘기는 아무한테도 못 하지?"
              - If Metal: "아닌 건 절대 아닌 칼 같은 성격이라 손절도 잘 하지?"
            - *Write 5-6 sentences that make them shiver with accuracy.*

            ### 🔮 [Year]년 운명 예언: [Shocking Title like "돈방석 아니면 쪽박, 네 선택이야"]
            (Give a dramatic verdict on Money & Relationships.)
            - **Money:** Be extremely specific. "3월, 9월에 목돈 나갈 일 생겨. 친구가 뭐 하자고 꼬시면 절대 하지 마." or "가만히 있어도 돈이 들어오는 운이야. 이직 생각 있으면 무조건 질러."
            - **Relationships:** "오래된 인연은 끊어지고 귀인이 들어와. 근데 그 귀인이 겉모습은 별로일 수 있어."
            - *Emphasize with bold text.*

            ### 💋 {my_title}의 코디 추천: [Color] [Item Name]
            (Format: **추천 아이템: [Color] [Item Name]**)
            (Connect Saju to **Psychological Desire/Fear**).
            - "너 지금 기운이 너무 뜨거워서 돈이 다 녹고 있어. 이걸 막아줄 **[Color]** 아이템이 필수야."
            - "이거 없으면 내년에도 사람 때문에 스트레스 받아서 탈모 올 수도 있다? 나를 지켜주는 부적이라고 생각하고 꼭 챙겨."

            (Closing)
            "우리 동생, 기 죽지 마. 네 운명은 네가 만드는 거야. {my_title} 말 명심하고! 알았지?"
            """
            
            # [요청 반영] 로딩 멘트 강화
            with st.spinner(f"⚡ {name}님의 뼈 때릴 준비 중... (멘탈 잡으세요 🤯)"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash") 
                response = model.generate_content(prompt)
                
                # 결과 박스
                st.markdown(f"""
                <div style="background-color:#121212; border:1px solid #333; border-radius:15px; padding:25px; margin-top:30px; line-height:1.8;">
                    <h3 style="color:#E5C17C; border-bottom:1px solid #333; padding-bottom:10px; font-size:20px; word-break:keep-all; margin:0 0 10px 0;">📜 {name}님을 위한 {my_title}의 독설 & 애정</h3>
                    {response.text}
                </div>
                """, unsafe_allow_html=True)
                
                # 황금박스 (욕망 자극 멘트 추가)
                st.markdown(f"""
                <div class="golden-box">
                    <h3 style="color:#FF6B6B; margin:0; font-size:24px;">🚨 {name}님, 이거 없으면 손해!</h3>
                    <p style="margin-top:15px; font-size:18px; color:#DDD;">
                        "2026년, 새어나가는 돈과 사람 막아줄<br>
                        <b>{my_title}의 강력 추천 방패</b>야."
                    </p>
                    <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin:20px 0; color:#CCC; font-size:16px;">
                        단순한 물건이 아니야.<br>
                        <b>너의 부족한 기운을 채워줄 유일한 비책.</b><br>
                        (품절되기 전에 미리 봐둬)
                    </div>
                    <a href="{selected_link}" target="_blank" class="pulse-button">
                        👉 {my_title}가 골라준 비책 확인하기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.warning("잠시 후 다시 시도해주세요. 계속 문제가 생기면 관리자에게 이 오류 메시지를 보여주세요.")
