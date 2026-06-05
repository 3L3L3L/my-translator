import json

import streamlit as st
import streamlit.components.v1 as components
from google import genai  # pip install google-genai

# ──────────────────────────────────────────────────────────────
# 1. 페이지 설정
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="실시간 다국어 번역기", layout="wide")

# 2. 디자인 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    h1 { color: #0f172a; font-weight: 700; font-size: 2.2rem !important; margin-bottom: 0.5rem; }
    p { color: #475569; font-size: 0.95rem; }
    hr { margin-top: 1rem; margin-bottom: 2rem; border-color: #e2e8f0; }
    .stTextArea label p { font-size: 1.2rem !important; font-weight: 700 !important; color: #1e293b !important; }
    .stTextArea textarea { border-radius: 8px !important; border: 1px solid #cbd5e1 !important; font-size: 1.05rem !important; }
    .char-count { color: #94a3b8; font-size: 0.8rem; text-align: right; margin-top: -8px; }
    .hist-meta { color: #64748b; font-size: 0.8rem; font-weight: 600; }
    .hist-src { color: #475569; font-size: 0.92rem; }
    .hist-tgt { color: #0f172a; font-size: 0.95rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("나만의 AI 실시간 번역기")
st.write("텍스트 입력 후 빈 화면을 클릭하거나 Ctrl+Enter를 누르면 실시간으로 즉시 자동 번역됩니다.")
st.markdown("<hr>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 3. 세션 상태
# ──────────────────────────────────────────────────────────────
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
if "history" not in st.session_state:          # ⭐ 번역 기록
    st.session_state.history = []              # [{"src","tgt","input","output"}, ...]

MAX_HISTORY = 20

# ──────────────────────────────────────────────────────────────
# 4. 콜백 함수들
# ──────────────────────────────────────────────────────────────
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
    st.session_state.last_cache_key = ""

def load_from_history(idx):
    """기록의 원문을 입력창으로 다시 불러오기"""
    item = st.session_state.history[idx]
    st.session_state.src_lang = item["src"]
    if item["tgt"] != "자동 감지":
        st.session_state.tgt_lang = item["tgt"]
    st.session_state.input_text = item["input"]
    st.session_state.last_cache_key = ""   # 다시 번역되도록

def clear_history():
    st.session_state.history = []

# ──────────────────────────────────────────────────────────────
# 5. API 키
# ──────────────────────────────────────────────────────────────
default_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        default_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

gemini_key = st.sidebar.text_input("Gemini API Key", type="password", value=default_key)

# 6. 언어 목록
lang_dict = {
    "자동 감지": "Detect Automatically",
    "한국어": "Korean",
    "영어": "English",
    "일본어": "Japanese",
    "중국어": "Chinese",
    "스페인어": "Spanish",
    "프랑스어": "French",
    "독일어": "German",
}

# ──────────────────────────────────────────────────────────────
# 7. 언어 선택 + 스왑 버튼
# ──────────────────────────────────────────────────────────────
col_lang_left, col_swap_btn, col_lang_right = st.columns([9, 2, 9])

with col_lang_left:
    st.selectbox("원본 언어 선택", list(lang_dict.keys()), key="src_lang")

with col_swap_btn:
    st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
    st.button("⇄ 스왑", on_click=swap_languages, use_container_width=True)

with col_lang_right:
    st.selectbox("번역할 언어 선택", [k for k in lang_dict.keys() if k != "자동 감지"], key="tgt_lang")

# ──────────────────────────────────────────────────────────────
# 8. 입력 영역
# ──────────────────────────────────────────────────────────────
col_text_left, col_text_right = st.columns(2)

with col_text_left:
    st.text_area(
        "원본 내용 (Input)",
        height=350,
        placeholder="번역할 내용을 입력한 뒤, 빈 화면을 클릭하거나 Ctrl+Enter를 누르세요...",
        key="input_text",
    )
    # ⭐ 글자수 표시
    st.markdown(f"<div class='char-count'>{len(st.session_state.input_text)}자</div>",
                unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 9. 캐시 기반 자동 번역
# ──────────────────────────────────────────────────────────────
text_to_translate = st.session_state.input_text.strip()

if text_to_translate:
    current_cache_key = f"{st.session_state.src_lang}_{st.session_state.tgt_lang}_{text_to_translate}"

    if st.session_state.last_cache_key != current_cache_key:
        if not gemini_key:
            st.session_state.translated_text = "⚠️ 왼쪽 사이드바창에 Gemini API Key를 입력해 주세요."
        else:
            with st.spinner("AI 엔진 번역 중..."):
                try:
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
                        contents=prompt,
                    )
                    if response.text:
                        st.session_state.translated_text = response.text
                        st.session_state.last_cache_key = current_cache_key

                        # ⭐ 번역 기록 저장 (직전과 동일하면 생략)
                        entry = {
                            "src": st.session_state.src_lang,
                            "tgt": st.session_state.tgt_lang,
                            "input": text_to_translate,
                            "output": response.text,
                        }
                        hist = st.session_state.history
                        if not hist or hist[0]["input"] != entry["input"] or hist[0]["tgt"] != entry["tgt"]:
                            hist.insert(0, entry)
                            del hist[MAX_HISTORY:]
                    else:
                        st.session_state.translated_text = "❌ 번역 실패: AI가 빈 결과를 반환했습니다."
                except Exception as e:
                    st.session_state.translated_text = f"❌ 시스템 오류 발생: {str(e)}"
else:
    st.session_state.translated_text = ""
    st.session_state.last_cache_key = ""

# ──────────────────────────────────────────────────────────────
# 10. 출력 영역 + 복사 버튼
# ──────────────────────────────────────────────────────────────
with col_text_right:
    st.text_area(
        "번역 결과 (Output)",
        value=st.session_state.translated_text,
        height=350,
        disabled=True,
        placeholder="내용을 입력하면 여기에 실시간으로 자동 번역됩니다.",
    )
    st.markdown(f"<div class='char-count'>{len(st.session_state.translated_text)}자</div>",
                unsafe_allow_html=True)

    # ⭐ 복사 버튼 (브라우저 클립보드 사용)
    if st.session_state.translated_text and not st.session_state.translated_text.startswith(("⚠️", "❌")):
        safe_text = json.dumps(st.session_state.translated_text)
        components.html(
            f"""
            <button id="copyBtn" style="
                width:100%; padding:10px; border-radius:8px; cursor:pointer;
                border:1px solid #cbd5e1; background:#0f172a; color:#fff;
                font-size:0.95rem; font-weight:600;">
                📋 결과 복사
            </button>
            <script>
                const b = document.getElementById('copyBtn');
                b.onclick = () => {{
                    navigator.clipboard.writeText({safe_text}).then(() => {{
                        b.innerText = '✅ 복사됨!';
                        setTimeout(() => b.innerText = '📋 결과 복사', 1500);
                    }});
                }};
            </script>
            """,
            height=55,
        )

# ──────────────────────────────────────────────────────────────
# 11. 번역 기록
# ──────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander(f"📜 번역 기록 ({len(st.session_state.history)})", expanded=False):
    if not st.session_state.history:
        st.caption("아직 번역 기록이 없습니다.")
    else:
        st.button("🗑️ 기록 전체 삭제", on_click=clear_history)
        for i, item in enumerate(st.session_state.history):
            c1, c2 = st.columns([10, 2])
            with c1:
                st.markdown(
                    f"<div class='hist-meta'>{item['src']} → {item['tgt']}</div>"
                    f"<div class='hist-src'>{item['input']}</div>"
                    f"<div class='hist-tgt'>↳ {item['output']}</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.button("↩️ 불러오기", key=f"load_{i}",
                          on_click=load_from_history, args=(i,),
                          use_container_width=True)
            st.markdown("<hr style='margin:0.6rem 0; border-color:#f1f5f9'>",
                        unsafe_allow_html=True)