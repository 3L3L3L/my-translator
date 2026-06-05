import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 와이드 모드 적용
st.set_page_config(page_title="실시간 다국어 번역기", layout="wide")

# [매크로 연동] 주소창에서 매크로가 보내온 텍스트가 있는지 확인
query_text = st.query_params.get("text", "")

# 2. 커스텀 CSS (고급스러운 디자인)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    h1 {
        color: #0f172a;
        font-weight: 700;
        font-size: 2.2rem !important;
        letter-spacing: -0.05em;
        margin-bottom: 0.5rem;
    }
    p {
        color: #475569;
        font-size: 0.95rem;
    }
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border-color: #e2e8f0;
    }
    .stTextArea label p {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 0.5rem;
    }
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("나만의 실시간 다국어 번역기")
st.write("왼쪽 창에 내용을 입력하면 오른쪽 창에 실시간으로 번역 결과가 표시됩니다.")
st.markdown("<hr>", unsafe_allow_html=True)

# [🔥 버그 수정] 로컬 환경에 secrets 파일이 없을 때 튕기는 현상을 완벽히 방지합니다.
default_key = ""
try:
    default_key = st.secrets.get("GEMINI_API_KEY", "")
)
except Exception:
    # 로컬에 secrets.toml 파일이 없어도 에러를 내지 않고 공백으로 자연스럽게 넘어갑니다.
    pass

# 사이드바 API 키 세팅
gemini_key = st.sidebar.text_input("Gemini API Key", type="password", value=default_key)

# 4. 전체 다국어 선택 딕셔너리
lang_dict = {
    "자동 감지": "Detect Language Automatically",
    "한국어": "Korean",
    "영어": "English",
    "일본어": "Japanese",
    "중국어(간체)": "Simplified Chinese",
    "중국어(번체)": "Traditional Chinese",
    "스페인어": "Spanish",
    "프랑스어": "French",
    "독일어": "German",
    "러시아어": "Russian",
    "베트남어": "Vietnamese",
    "태국어": "Thai",
    "이탈리아어": "Italian",
    "포르투갈어": "Portuguese",
    "아랍어": "Arabic"
}

# 5. 좌우 완벽 대칭 2분할 레이아웃
col_left, col_right = st.columns(2)

with col_left:
    source_lang_name = st.selectbox("원본 언어 선택", list(lang_dict.keys()), index=0, key="src_lang")
    text_to_translate = st.text_area(
        "원본 내용 (Input)", 
        height=380, 
        placeholder="여기에 텍스트를 입력하거나 붙여넣으세요...",
        key="input_text"
    )

with col_right:
    target_lang_name = st.selectbox(
        "번역할 언어 선택", 
        [k for k in lang_dict.keys() if k != "자동 감지"], 
        index=1, 
        key="tgt_lang"
    )
    
    translated_text = ""
    
    # 실시간 텍스트 감지 및 번역 로직 수행
    if text_to_translate.strip():
        if not gemini_key:
            translated_text = "⚠️ 왼쪽 사이드바창을 열어 발급받으신 Gemini API Key를 입력해 주세요."
        else:
            try:
                # Gemini 엔진 초기화
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 프롬프트 조립 규칙
                if source_lang_name == "자동 감지":
                    prompt = (
                        f"Translate the following text into {lang_dict[target_lang_name]}. "
                        f"Keep the original format, URLs, and line breaks intact. "
                        f"Do NOT add any intro, explanations, or notes. Reply ONLY with the translated text.\n\n"
                        f"Text:\n{text_to_translate}"
                    )
                else:
                    prompt = (
                        f"Translate the following text into {lang_dict[target_lang_name]}. "
                        f"The original language is {lang_dict[source_lang_name]}. "
                        f"Keep the original format, URLs, and line breaks intact. "
                        f"Do NOT add any intro, explanations, or notes. Reply ONLY with the translated text.\n\n"
                        f"Text:\n{text_to_translate}"
                    )
                
                # AI 번역 요청
                response = model.generate_content(prompt)
                
                if response.text:
                    translated_text = response.text
                else:
                    translated_text = "번역 엔진이 빈 결과를 반환했습니다."
                    
            except Exception as e:
                translated_text = f"번역 중 시스템 오류가 발생했습니다: {str(e)}"
    
    # 결과창 출력
    st.text_area(
        "번역 결과 (Output)",
        value=translated_text,
        height=380,
        placeholder="왼쪽 창에 내용을 입력한 뒤, 빈 화면을 클릭하거나 Ctrl+Enter를 누르면 실시간으로 번역됩니다.",
        disabled=True,
        key="output_text"
    )