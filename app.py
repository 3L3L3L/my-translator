import streamlit as st
from deep_translator import GoogleTranslator

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="나만의 다국어 번역기", page_icon="🌐", layout="centered")

# 2. 디자인 및 헤더
st.title("🌐 나만의 심플 다국어 번역기")
st.write("광고 없이 깔끔하게 사용하는 나만의 번역 공간입니다.")
st.markdown("---")

# 3. 언어 선택 딕셔너리 (언어 대폭 추가!)
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

# 4. 화면 분할 (원본 언어 / 목적 언어 선택)
col1, col2 = st.columns(2)
with col1:
    source_lang_name = st.selectbox("원본 언어", list(lang_dict.keys()), index=0)
with col2:
    target_lang_name = st.selectbox("번역할 언어", [k for k in lang_dict.keys() if k != "자동 감지"], index=1)

source_lang = lang_dict[source_lang_name]
target_lang = lang_dict[target_lang_name]

# 5. 텍스트 입력창
text_to_translate = st.text_area("번역할 내용을 입력하세요", height=200, placeholder="여기에 텍스트를 입력하거나 붙여넣으세요...")

# 6. 번역 실행 버튼 및 로직
if st.button("번역하기", type="primary", use_container_width=True):
    if not text_to_translate.strip():
        st.warning("텍스트를 먼저 입력해주세요!")
    else:
        with st.spinner("번역하는 중..."):
            try:
                # 번역 실행
                translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text_to_translate)
                
                # 결과 출력
                st.markdown("### 📝 번역 결과")
                st.info(translated_text)
                
            except Exception as e:
                st.error(f"번역 중 오류가 발생했습니다: {e}")