import streamlit as st
import google.generativeai as genai
import datetime
from korean_lunar_calendar import KoreanLunarCalendar
import random

# ==========================================
# [PROJECT: LUNA - FINAL ACTION MAKER]
# "직관적인 메뉴 + 강력한 팔로우 유도 (필수)"
# ==========================================

st.set_page_config(
    page_title="LUNA: 운명 상담소(연애/인생/사업/타로)", 
    page_icon="🔮", 
    layout="wide"
)

# --- [디자인] 시선 강탈 & 따뜻한 감성 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;500;700&display=swap');
    
    /* 전체 배경: 고급스러운 다크 모드 */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Noto Serif KR', serif;
    }
    
    /* [버튼 애니메이션] 두근두근 효과 (시선 집중) */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); transform: scale(1); }
        50% { transform: scale(1.02); }
        70% { box-shadow: 0 0 0 15px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); transform: scale(1); }
    }

    /* 링크 버튼 스타일 (화려하게) */
    a.lucky-btn {
        display: block;
        width: 100%;
        background: linear-gradient(45deg, #FFD700, #FF8C00, #FFD700);
        background-size: 200% 200%;
        color: #000000 !important;
        text-align: center;
        padding: 20px;
        font-size: 20px;
        font-weight: 900;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 15px;
        animation: pulse 2s infinite; 
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        transition: 0.3s;
    }
    a.lucky-btn:hover {
        background: linear-gradient(45deg, #FF8C00, #FFD700);
        color: #000 !important;
    }

    /* 헤더 */
    h1 {
        color: #E5C17C;
        font-family: 'Noto Serif KR', serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        text-align: center;
        color: #A0A0A0;
        font-size: 15px;
        margin-bottom: 25px;
        font-weight: 300;
    }

    /* 가격표 */
    .price-tag {
        background: #1E1E1E;
        border: 1px solid #E5C17C;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin: 0 auto 30px auto;
        max-width: 500px;
    }
    .sale-price { color: #FFD700; font-weight: bold; font-size: 20px; }

    /* 입력창 및 버튼 */
    .stTextInput>div>div>input { text-align: center; background-color: #222; color: #FFF; }
    .stButton>button {
        background: #333; color: #E5C17C; border: 1px solid #E5C17C;
        height: 60px; font-size: 18px; width: 100%; font-weight: bold;
    }
    .stButton>button:hover { background: #E5C17C; color: #000; }

    /* 결과 박스 */
    .letter-box {
        background-color: #1A1A1A; padding: 30px; border-radius: 10px;
        border-top: 5px solid #E5C17C; margin-top: 30px; line-height: 1.8;
    }
    
    /* 처방전 박스 */
    .prescription-box {
        background-color: #262020; border: 2px solid #D4AF37;
        padding: 25px; margin-top: 30px; text-align: center; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.header("🔐 관리자 인증")
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        gemini_api_key = st.text_input("API Key 입력", type="password")

# --- 메인 화면 ---
st.markdown("<h1>LUNA : 운명 상담소</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>혼자 끙끙 앓지 마요.<br>언니가 당신의 흐름을 읽어줄게요.</div>", unsafe_allow_html=True)

# [수정] 가격 앵커링 (필수 강조 멘트 적용)
st.markdown("""
<div class='price-tag'>
    <span style='text-decoration: line-through; color: #666; margin-right: 10px;'>1회 상담료 50,000원</span>
    <span class='sale-price'>지금은 무료 이벤트 중</span><br>
    <div style='font-size: 14px; color: #BBB; margin-top:8px; font-weight: 500;'>
        💸 복채 대신 '팔로우'와 '댓글'은 필수예요!<br>
        <span style='color:#FFD700; font-size:12px;'>(그래야 복채 내는 효과가 나서 운이 최고로 좋아져요✨)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 입력 폼
col_main, col_dummy = st.columns([1, 0.01]) 
with col_main:
    # [수정] 직관적인 메뉴 이름 적용
    topic = st.radio(
        "어떤 운명이 궁금한가요?",
        ["오늘의 운세", "🦄 2026년 1년 운세"],
        index=1,
        horizontal=True
    )
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("이름 (본명)", placeholder="예: 김루나")
        gender = st.radio("성별", ["여성", "남성"], horizontal=True)
    with c2:
        birth_date = st.date_input("태어난 날", min_value=datetime.date(1950, 1, 1), value=datetime.date(1990, 1, 1))
        birth_time = st.time_input("태어난 시간 (모르면 패스)", datetime.time(9, 00))

    st.markdown("<br>", unsafe_allow_html=True)
    
    if "2026" in topic:
        worry = st.text_input("요즘 가장 답답한 게 뭐예요?", placeholder="예: 사업이 막혀요, 이직할까요?, 재회하고 싶어요...")
        btn_text = "📜 2026년 내 운명 흐름, 자세히 풀어보기"
    else:
        worry = st.text_input("오늘 하루, 특히 신경 쓰이는 일 있어?", placeholder="예: 면접, 소개팅, 계약, 아니면 그냥 기분...")
        btn_text = "📜 오늘 하루 기운, 미리 읽어보기"

# 쿠팡 링크
lucky_bag = [
    "https://link.coupang.com/a/c7U5ic", "https://link.coupang.com/a/c7Vcxs", 
    "https://link.coupang.com/a/c7VexJ", "https://link.coupang.com/a/c7VfKc", 
    "https://link.coupang.com/a/c7Vhmc", "https://link.coupang.com/a/c7VinT", 
    "https://link.coupang.com/a/c7Vkbn", "https://link.coupang.com/a/c7Vk67", 
    "https://link.coupang.com/a/c7Vmq1", "https://link.coupang.com/a/c7VncA", 
    "https://link.coupang.com/a/c7VoiP"
]
lucky_link = random.choice(lucky_bag)

# 실행 로직
if st.button(btn_text, use_container_width=True):
    if not name:
        st.warning("이름을 알려줘야 언니가 점을 봐주지~ 😅")
    elif not gemini_api_key:
        st.error("상담소 문이 잠겼어요. (API Key 확인 필요)")
    else:
        try:
            calendar = KoreanLunarCalendar()
            calendar.setSolarDate(birth_date.year, birth_date.month, birth_date.day)
            lunar_date = calendar.LunarIsoFormat()
            
            prompt = f"""
            [System Role]
            Act as 'Luna', a warm and insightful fortune teller (Sister/Mentor vibe).
            Target: General public (20s~60s). 
            Tone: Polite Korean ('해요' style) but very intimate and comforting.
            
            [User Info]
            Name: {name} ({gender}), Birth: {birth_date} (Lunar: {lunar_date})
            Topic: {topic}, Worry: {worry}
            
            [Request]
            Provide a warm, empathetic analysis.
            Structure:
            1. **공감의 한마디**: "많이 힘들었죠?" or "기대되는 하루네요!"
            2. **사주 분석**: Use professional terms but explain them easily.
            3. **조언**: Specific advice for their worry.
            """
            
            with st.spinner(f"🌙 {name}님의 사주를 꼼꼼히 살펴보고 있어요..."):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                
                st.markdown(f"<div class='letter-box'><h3>💌 {name}님을 위한 분석 결과</h3>{response.text}</div>", unsafe_allow_html=True)
                
                # --- [수익화] 화려한 버튼 & 친근한 안심 멘트 ---
                st.markdown(f"""
                <div class='prescription-box'>
                    <h3 style='color: #FFD700; margin:0; font-size:22px; font-weight:bold;'>🧲 {name}님을 위한 '운명 자석'</h3>
                    <p style='color: #E0E0E0; font-size: 16px; margin-top: 15px; line-height: 1.6;'>
                        당신의 사주에 지금 딱 <b>2% 부족한 기운</b>이 보여요.<br>
                        이 물건은 흩어져 있는 <b>행운을 자석처럼 당신에게 강제로 끌어당겨 줄 행운템</b>이에요.<br>
                        <br>
                        <span style='color: #BBB; font-size: 13px;'>
                        (걱정 마세요. 커피 한 잔 값으로 운명을 바꿀 수 있는<br>
                        가성비 좋고 센스 있는 아이템으로만 골랐습니다. 안심하고 확인하세요.)
                        </span>
                    </p>
                    <a href="{lucky_link}" target="_blank" class="lucky-btn">
                        👉 내 운명에 '강력한 행운템' 보러가기 (Click)
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Footer
                st.markdown("<div style='text-align:center; color:#555; font-size:12px; margin-top:15px;'>COPYRIGHT ⓒ LUNA. 본 추천은 쿠팡 파트너스 활동이며, 수익은 무료 상담 운영에 큰 힘이 됩니다.</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"지금 상담 요청이 폭주해서 잠시 연결이 늦어졌어요. 다시 버튼을 눌러주세요! ({e})")


