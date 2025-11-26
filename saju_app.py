import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - FINAL MOBILE MASTERPIECE]
# "모바일 가독성 최적화 + 팩폭/설렘 멘트 + 수익화 완결"
# ==========================================

st.set_page_config(
    page_title="루나 : 운명 설계사", 
    page_icon="⚡", 
    layout="wide"
)

# --- [디자인] 모바일 최적화 & 시선 강탈 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700;900&display=swap');
    
    /* 1. 배경 및 기본 폰트 설정 (4060 가독성 위해 폰트 키움) */
    .stApp {
        background-color: #0E0E0E; /* 깊은 블랙 */
        color: #FFFFFF; /* 완전한 화이트 (가독성 최우선) */
        font-family: 'Noto Serif KR', serif;
        font-size: 19px; /* 기본 폰트 확대 */
    }
    
    /* 2. 헤더 스타일 (모바일에서도 줄바꿈 예쁘게) */
    h1 {
        color: #E5C17C;
        font-family: 'Noto Serif KR', serif;
        font-weight: 900;
        text-align: center;
        margin-bottom: 15px;
        font-size: 2.3rem; /* 모바일에서 너무 크지 않게 조정 */
        line-height: 1.3;
        text-shadow: 0 2px 10px rgba(229, 193, 124, 0.2);
    }
    
    .sub-header {
        text-align: center;
        color: #CCCCCC; /* 밝은 회색으로 가독성 확보 */
        font-size: 17px;
        margin-bottom: 30px;
        line-height: 1.6;
        font-weight: 400;
        word-break: keep-all; /* 단어 중간에 끊기지 않게 */
    }

    /* 3. 가격표 (황금 박스) */
    .price-tag {
        background: #161616;
        border: 1px solid #D4AF37;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 0 auto 30px auto;
        max-width: 600px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .sale-price { 
        color: #FFD700; 
        font-weight: 900; 
        font-size: 24px; 
    }

    /* 4. 입력창 및 버튼 (엄지손가락 터치하기 편하게 큼직하게) */
    .stTextInput>div>div>input { 
        text-align: center; 
        background-color: #222; 
        color: #FFF; 
        border: 1px solid #555; 
        height: 55px; /* 높이 확보 */
        font-size: 18px;
        border-radius: 8px;
    }
    /* 라디오 버튼 폰트 키우기 */
    .stRadio label {
        font-size: 18px !important;
    }

    /* 실행 버튼 스타일 (기본 버튼) */
    .stButton>button {
        background: #222; 
        color: #E5C17C; 
        border: 1px solid #E5C17C;
        height: 70px; /* 터치 영역 확대 */
        font-size: 20px; 
        width: 100%; 
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover { 
        background: #E5C17C; 
        color: #000; 
        border: none; 
    }

    /* 5. 결과 박스 (가독성: 흰 글씨 + 줄간격 넓게) */
    .letter-box {
        background-color: #121212; 
        padding: 30px; 
        border-radius: 10px;
        border: 1px solid #333; 
        border-top: 5px solid #D4AF37; 
        margin-top: 30px; 
        line-height: 1.9; /* 줄 간격 시원하게 */
        font-size: 19px; /* 글씨 큼직하게 */
        color: #FAFAFA;
    }
    
    /* 6. [핵심] 쇼핑 유도 황금 박스 & 버튼 애니메이션 */
    .prescription-box {
        background-color: #1A1A1A; 
        border: 2px solid #D4AF37; 
        padding: 25px; 
        margin-top: 35px; 
        text-align: center; 
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.1);
    }

    /* 심장박동 애니메이션 */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); transform: scale(1); }
        50% { transform: scale(1.02); }
        70% { box-shadow: 0 0 0 15px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); transform: scale(1); }
    }

    /* 링크 버튼 (강렬한 오렌지/골드 그라데이션) */
    a.lucky-btn {
        display: block;
        width: 100%;
        background: linear-gradient(90deg, #FF8C00, #FFD700); /* 오렌지~골드 */
        color: #000000 !important;
        text-align: center;
        padding: 22px;
        font-size: 20px;
        font-weight: 900; /* 제일 두껍게 */
        border-radius: 10px;
        text-decoration: none;
        margin-top: 20px;
        animation: pulse 2s infinite; 
        box-shadow: 0 5px 15px rgba(255, 140, 0, 0.4);
        transition: 0.3s;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.header("🔐 관리자 승인")
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("API Key 입력", type="password")

# --- 메인 화면 (Header) ---
st.markdown("<h1>루나 : 운명 설계사<br><span style='font-size: 0.8em;'>(문제해결 팩폭 상담소)</span></h1>", unsafe_allow_html=True)

# [수정된 서브 멘트: 팩폭 주의 강조]
st.markdown("""
<div class='sub-header'>
    "혼자 끙끙 앓지 마세요."<br>
    루나 언니가 당신의 미래와 해결책을 <b>냉정하고 확실하게</b> 알려줄게요.<br>
    <span style='color: #FF6B6B; font-weight: bold;'>(※ 유리멘탈 주의 🚨)</span>
</div>
""", unsafe_allow_html=True)

# [가격 앵커링: 필수 멘트 적용]
st.markdown("""
<div class='price-tag'>
    <span style='text-decoration: line-through; color: #888; margin-right: 10px; font-size: 16px;'>1:1 심층 상담료 50,000원</span>
    <span class='sale-price'>지금만 무료 (0원)</span><br>
    <div style='font-size: 15px; color: #DDD; margin-top:12px; font-weight: 500; line-height: 1.5;'>
        ⚠️ <b>주의:</b> 복채 대신 <b>'팔로우'</b>와 <b>'댓글'</b>은 필수입니다!<br>
        <span style='color:#FFD700; font-size:14px;'>(복채 내야 효과가 최고인 거 아시죠?^^✨)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 입력 폼 (Input) ---
col_main, col_dummy = st.columns([1, 0.01]) 
with col_main:
    # 메뉴
    topic = st.radio(
        "어떤 운명이 궁금한가요?",
        ["오늘의 운세 (Daily)", "🦄 2026년 1년 운세 (Yearly)"],
        index=1,
        horizontal=True
    )
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("이름 (본명)", placeholder="예: 홍길동")
        gender = st.radio("성별", ["여성", "남성"], horizontal=True)
    with c2:
        birth_date = st.date_input("생년월일", min_value=datetime.date(1950, 1, 1), value=datetime.date(1990, 1, 1))
        birth_time = st.time_input("태어난 시간 (모르면 패스)", datetime.time(9, 00))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 질문 유도
    if "2026" in topic:
        worry = st.text_input("지금 가장 꽉 막힌 문제는?", placeholder="예: 돈이 자꾸 새요, 남편이랑 자꾸 싸워요, 건강이 불안해요...")
        # [수정된 버튼 텍스트: 설렘 + 액션]
        btn_text = "두근두근 💓 2026년 미리 보고, 인생 바꿀 '해결책' 찾으러 가자!"
    else:
        worry = st.text_input("오늘 컨디션이나 기분은?", placeholder="예: 이유 없이 불안함, 중요한 계약 앞둠...")
        btn_text = "⚡ 오늘 내 기운, 냉정하게 확인하러 가기!"

# 쿠팡 링크 (행운템)
lucky_bag = [
    "https://link.coupang.com/a/c7U5ic", "https://link.coupang.com/a/c7Vcxs", 
    "https://link.coupang.com/a/c7VexJ", "https://link.coupang.com/a/c7VfKc", 
    "https://link.coupang.com/a/c7Vhmc", "https://link.coupang.com/a/c7VinT", 
    "https://link.coupang.com/a/c7Vkbn", "https://link.coupang.com/a/c7Vk67", 
    "https://link.coupang.com/a/c7Vmq1", "https://link.coupang.com/a/c7VncA", 
    "https://link.coupang.com/a/c7VoiP"
]
lucky_link = random.choice(lucky_bag)

# --- 실행 로직 ---
if st.button(btn_text, use_container_width=True):
    if not name:
        st.warning("이름을 입력해야 진단서를 끊어드리죠. 얼른 적으세요.")
    elif not gemini_api_key:
        st.error("시스템 키 오류. 관리자에게 문의하세요.")
    else:
        try:
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            # [프롬프트: 팩트 폭력 + 해결책 중심]
            prompt = f"""
            [System Role]
            Act as 'Luna', a sharp, insightful fortune consultant (The 'Unnie' who gives Fact-bombs).
            Target Audience: 20s-60s.
            Tone: 
            - Polite but Hitting the Bone (예의는 지키되 팩트는 정확하게).
            - Use metaphors like "Fire needs Water" to explain Saju easily.
            - Focus on "Problem Solving".
            
            [User Info]
            Name: {name} ({gender}), Birth: {birth_date} (Lunar: {lunar_date})
            Topic: {topic}, Worry: {worry}
            
            [Structure of Response]
            1. **🛑 팩트 진단 (Diagnosis)**: 
               - Start with a shock/hook. e.g., "{name}님, 솔직히 말할게요. 지금 속이 숯검정이시네요."
               - Analyze their Saju elements directly linked to their worry.
            
            2. **📉 미래 예측 (Prognosis)**:
               - If they don't change, what happens in 2026? Be realistic.
            
            3. **💊 루나의 솔루션 (Solution)**:
               - Provide a clear, actionable solution.
               - **Bridge to the Item:** Connect the solution to a specific element/item they need.
               - e.g., "You need Water energy urgently. You must carry this specific item to survive."
            """
            
            with st.spinner(f"⚡ {name}님의 사주를 냉철하게 스캔 중입니다..."):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                
                st.markdown(f"<div class='letter-box'><h3>📋 {name}님을 위한 운명 진단서</h3>{response.text}</div>", unsafe_allow_html=True)
                
                # --- [수익화] 쇼핑 유도 황금 박스 (네가 원한 멘트 완벽 적용) ---
                st.markdown(f"""
                <div class='prescription-box'>
                    <h3 style='color: #FF6B6B; margin:0; font-size:22px; font-weight:900;'>🚨 {name}님, 긴급 처방입니다!</h3>
                    <div style='margin-top: 20px; font-size: 18px; color: #FFF; line-height: 1.6;'>
                        "이 물건은 <b>당신에게 지금 딱 2% 부족한 기운을<br>채워줄 '생존템'</b>입니다."
                    </div>
                    
                    <div style='margin-top: 25px; font-size: 16px; color: #DDD; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; line-height: 1.6;'>
                        <b>요즘 사는 게 참 만만치 않죠?<br>
                        그래서 루나 언니가 '갓성비 아이템'으로 골라놨어요!<br><br>
                        내 행운템이 뭔지 눈도장만 찍고 가도<br>
                        기운이 확 달라질 거예요.</b>
                    </div>
                    
                    <a href="{lucky_link}" target="_blank" class="lucky-btn">
                        👉 내 운명에 '강력한 행운템' 보러가기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Footer
                st.markdown("<div style='text-align:center; color:#666; font-size:13px; margin-top:20px;'>COPYRIGHT ⓒ LUNA SOLUTION. 본 추천은 쿠팡 파트너스 활동이며, 수익은 무료 상담 운영에 큰 힘이 됩니다.</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"진단 요청이 폭주하여 시스템이 과열되었습니다. 잠시 후 다시 눌러주세요. ({e})")



