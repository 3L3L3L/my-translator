import streamlit as st
from google import genai  # ✅ 새 통합 SDK (pip install google-genai)

# 1. 무조건 와이드 모드로 화면 넓게 설정
st.set_page_config(page_title="실시간 다국어 번역기", layout="wide")

# 2. 고급스러운 그레이 미니멀 디자인 CSS 적용
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    h1 { color: #0f172a; font-weight: 700; font-size: 2.2rem !important; margin-bottom: 0.5rem; }
    p { color: #475569; font-size: 0.95rem; }
    hr { margin-top: 1rem; margin-bottom: 2rem; border-color: #e2e8f0; }
    .stTextArea label p { font-size: 1.2rem !important; font-weight: 700 !important; color: #1e293b !important; }
    .stTextArea textarea { border-radius: 8px !important; border: 1px solid #cbd5e1 !important; font-size: 1.05rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("나만의 AI 실시간 번역기")
st.write("텍스트 입력 후 빈 화면을 클릭하거나 Ctrl+Enter를 누르면 실시간으로 즉시 자동 번역됩니다.")
st.markdown("<hr>", unsafe_allow_html=True)

# 3. [핵심] 데이터 충돌 방지 및 스왑을 위한 세션 상태 안정화 (최초 1회만 선언)
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "자동 감지"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "영어"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "last_cache_key" not in st.session_state:
    st.session_state.last_cache_key = ""

# 4. 양방향 언어/텍스트 실시간 스왑 함수
def swap_languages():
    old_src = st.session_state.src_lang
    old_tgt = st.session_state.tgt_lang
    old_input = st.session_state.input_text
    old_output = st.session_state.translated_text

    if old_src == "자동 감지":
        st.session_state.src_lang = old_tgt
        st.session_state.tgt_lang = "한국어" if old_tgt != "한국어" else "영어"
    else:
        st.session_state.src_lang = old_tgt
        st.session_state.tgt_lang = old_src

    st.session_state.input_text = old_output
    st.session_state.translated_text = old_input
    # 스왑 후에는 캐시키를 비워 다음 번역이 새로 트리거되도록 함
    st.session_state.last_cache_key = ""

# 5. 인터넷 서버(Secrets) 혹은 로컬 환경 API 키 안전하게 가져오기
default_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        default_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

gemini_key = st.sidebar.text_input("Gemini API Key", type="password", value=default_key)

# 6. 지원하는 다국어 목록 세팅
lang_dict = {
    "자동 감지": "Detect Automatically",
    "한국어": "Korean",
    "영어": "English",
    "일본어": "Japanese",
    "중국어": "Chinese",
    "스페인어": "Spanish",
    "프랑스어": "French",
    "독일어": "German"
}

# 7. 상단 언어 선택 박스 및 스왑(⇄) 버튼 레이아웃 구성
col_lang_left, col_swap_btn, col_lang_right = st.columns([9, 2, 9])

with col_lang_left:
    st.selectbox("원본 언어 선택", list(lang_dict.keys()), key="src_lang")

with col_swap_btn:
    st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
    st.button("⇄ 스왑", on_click=swap_languages, use_container_width=True)

with col_lang_right:
    st.selectbox("번역할 언어 선택", [k for k in lang_dict.keys() if k != "자동 감지"], key="tgt_lang")

# 8. 입출력 텍스트 레이아웃 화면 배치
col_text_left, col_text_right = st.columns(2)

with col_text_left:
    st.text_area(
        "원본 내용 (Input)",
        height=350,
        placeholder="번역할 내용을 입력한 뒤, 빈 화면을 클릭하거나 Ctrl+Enter를 누르세요...",
        key="input_text"
    )

# 9. [실시간 자동 번역] 캐시 기반 로직
# (텍스트 입력창이 렌더링된 직후 실행되도록 서순을 정렬하여 데이터 유실 방지)
text_to_translate = st.session_state.input_text.strip()

if text_to_translate:
    # 언어와 본문을 조합해 고유한 캐시 키 생성 -> 내용이 바뀔 때만 1번만 API 호출
    current_cache_key = f"{st.session_state.src_lang}_{st.session_state.tgt_lang}_{text_to_translate}"

    if st.session_state.last_cache_key != current_cache_key:
        if not gemini_key:
            st.session_state.translated_text = "⚠️ 왼쪽 사이드바창에 Gemini API Key를 입력해 주세요."
        else:
            with st.spinner("AI 엔진 번역 중..."):
                try:
                    # ✅ 새 SDK: 클라이언트 생성 후 models.generate_content 호출
                    client = genai.Client(api_key=gemini_key)

                    prompt = (
                        f"You are a professional, lightning-fast translator. "
                        f"Translate the following text into {lang_dict[st.session_state.tgt_lang]}. "
                        f"The original language is {lang_dict[st.session_state.src_lang]}. "
                        f"Keep the original format, links, and line breaks exactly the same. "
                        f"Do NOT say any greetings, intros, or explanations. "
                        f"Give me ONLY the translated result text.\n\n"
                        f"Text to translate:\n{text_to_translate}"
                    )

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    if response.text:
                        st.session_state.translated_text = response.text
                        st.session_state.last_cache_key = current_cache_key
                    else:
                        st.session_state.translated_text = "❌ 번역 실패: AI가 빈 결과를 반환했습니다."
                except Exception as e:
                    st.session_state.translated_text = f"❌ 시스템 오류 발생: {str(e)}"
else:
    st.session_state.translated_text = ""
    st.session_state.last_cache_key = ""

with col_text_right:
    # ✅ key 제거: 읽기 전용 표시 박스이므로 value만으로 결과를 갱신
    st.text_area(
        "번역 결과 (Output)",
        value=st.session_state.translated_text,
        height=350,
        disabled=True,
        placeholder="내용을 입력하면 여기에 실시간으로 자동 번역됩니다."
    )