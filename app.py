import streamlit as st
from deep_translator import GoogleTranslator

# 1. 페이지 설정 및 와이드 모드 적용 (화면을 넓게 씁니다)
st.set_page_config(page_title="실시간 다국어 번역기", layout="wide")

# [매크로 연동] 주소창에서 매크로가 보내온 텍스트가 있는지 확인하고 가져옵니다
query_text = st.query_params.get("text", "")

# 2. 커스텀 CSS: 고급스러운 그레이/화이트 톤 배경 및 대칭 디자인 반영
st.markdown("""
    <style>
    /* 전체 앱 배경색을 차분한 내추럴 그레이로 변경 */
    .stApp {
        background-color: #f8fafc;
    }
    /* 제목 및 가이드 텍스트 스타일 */
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
    /* 구분선 정돈 */
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border-color: #e2e8f0;
    }
    /* 입력창과 출력창의 라벨(타이틀) 디자인 통일 */
    .stTextArea label p {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 0.5rem;
    }
    /* 텍스트 영역 테두리 및 내부 여백 정돈 */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 헤더 영역 (이모티콘 완전 제외)
st.title("나만의 실시간 다국어 번역기")
st.write("왼쪽 창에 내용을 입력하면 오른쪽 창에 실시간으로 번역 결과가 표시됩니다.")
st.markdown("<hr>", unsafe_allow_html=True)

# 4. 전체 다국어 선택 딕셔너리 (15개 언어 완벽 복구)
lang_dict = {
    "자동 감지": "auto",
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어(간체)": "zh-CN",
    "중국어(번체)": "zh-TW",
    "스페인어": "es",
    "프랑스어": "fr",
    "독일어": "de",
    "러시아어": "ru",
    "베트남어": "vi",
    "태국어": "th",
    "이탈리아어": "it",
    "포르투갈어": "pt",
    "아랍어": "ar"
}

# 5. 좌우 완벽 대칭 2분할 레이아웃 (5:5 비율)
col_left, col_right = st.columns(2)

# [왼쪽 영역] 입력창 (주소창에 매크로 텍스트가 있으면 자동으로 채워짐)
with col_left:
    source_lang_name = st.selectbox("원본 언어 선택", list(lang_dict.keys()), index=0, key="src_lang")
    text_to_translate = st.text_area(
        "원본 내용 (Input)", 
        value=query_text,
        height=380, 
        placeholder="여기에 텍스트를 입력하거나 붙여넣으세요...",
        key="input_text"
    )

source_lang = lang_dict[source_lang_name]

# [오른쪽 영역] 출력창 (왼쪽 박스와 컴포넌트 구조 및 높이 100% 일치)
with col_right:
    target_lang_name = st.selectbox(
        "번역할 언어 선택", 
        [k for k in lang_dict.keys() if k != "자동 감지"], 
        index=1, 
        key="tgt_lang"
    )
    target_lang = lang_dict[target_lang_name]
    
    # 실시간 자동 번역 로직 가동
    translated_text = ""
    if text_to_translate.strip():
        try:
            translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text_to_translate)
        except Exception as e:
            translated_text = f"번역 중 오류가 발생했습니다: {e}"
            
    # 왼쪽 창과 동일한 테두리를 가진 읽기 전용(disabled) 텍스트 박스로 결과 출력
    st.text_area(
        "번역 결과 (Output)",
        value=translated_text,
        height=380,
        placeholder="왼쪽 창에 내용을 입력하면 실시간으로 번역됩니다.",
        disabled=True,
        key="output_text"
    )