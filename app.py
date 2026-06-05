import streamlit as st
from deep_translator import GoogleTranslator

# 1. 웹페이지 기본 설정 (와이드 모드로 변경하여 2분할 화면을 시원하게 만듭니다)
st.set_page_config(page_title="나만의 실시간 번역기", page_icon="🌐", layout="wide")

# 2. 디자인 및 헤더
st.title("🌐 나만의 실시간 다국어 번역기")
st.write("번역하기 버튼을 누를 필요 없이, 왼쪽에 타이핑하면 오른쪽에 즉시 번역됩니다.")
st.markdown("---")

# 3. 다국어 선택 딕셔너리
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

# 4. 좌우 2분할 레이아웃 구성 (5:5 비율)
col_left, col_right = st.columns(2)

# [왼쪽 영역] 원본 언어 선택 및 텍스트 입력
with col_left:
    st.markdown("### 📥 원본 내용 (Input)")
    source_lang_name = st.selectbox("원본 언어 선택", list(lang_dict.keys()), index=0, key="src_lang")
    
    text_to_translate = st.text_area(
        "번역할 내용을 입력하세요", 
        height=350, 
        placeholder="여기에 텍스트를 타이핑하거나 붙여넣으세요...",
        key="input_text"
    )

# [오른쪽 영역] 목적 언어 선택 및 자동 번역 결과 출력
with col_right:
    st.markdown("### 📤 번역 결과 (Output)")
    target_lang_name = st.selectbox(
        "번역할 언어 선택", 
        [k for k in lang_dict.keys() if k != "자동 감지"], 
        index=1, 
        key="tgt_lang"
    )
    
    source_lang = lang_dict[source_lang_name]
    target_lang = lang_dict[target_lang_name]
    
    # 결과를 담을 공간을 미리 확보 (UI가 깨지는 것을 방지)
    output_container = st.container()
    
    with output_container:
        # 실시간 자동 번역 로직 (텍스트가 입력되어 있으면 즉시 실행)
        if text_to_translate.strip():
            try:
                translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text_to_translate)
                # 깔끔한 박스 형태로 결과 출력
                st.info(translated_text)
            except Exception as e:
                st.error(f"번역 중 오류가 발생했습니다: {e}")
        else:
            # 입력 창이 비어있을 때 보여줄 가이드 문구
            st.caption("왼쪽 창에 내용을 입력하면 이곳에 실시간으로 번역 결과가 표시됩니다.")