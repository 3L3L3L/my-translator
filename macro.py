import keyboard
import time
import urllib.parse
import webbrowser
import pyperclip
import os

# [필독] 본인의 진짜 Streamlit 인터넷 배포 주소를 넣으세요!
WEB_URL = "https://my-translator-fby6uybwz4l3k3xucufn7e.streamlit.app/" 

last_time = 0

def on_ctrl_c():
    global last_time
    current_time = time.time()
    
    # 0.5초 안에 Ctrl+C가 연속으로 두 번 눌렸는지 감지
    if current_time - last_time < 0.5:
        time.sleep(0.1) # 클립보드에 문자가 완전히 복사될 때까지 찰나의 대기
        text = pyperclip.paste()
        
        if text.strip():
            # 문장 부호나 띄어쓰기를 주소창용 문자로 변환 (인코딩)
            encoded_text = urllib.parse.quote(text)
            # 브라우저로 내 번역기 사이트 강제 오픈
            webbrowser.open(f"{WEB_URL}?text={encoded_text}")
            
    last_time = current_time

# 프로그램을 완전히 종료하고 싶을 때 누르는 핫키 (Ctrl + Shift + X)
keyboard.add_hotkey('ctrl+shift+x', lambda: os._exit(0))

# 키보드 감시 시작
keyboard.add_hotkey('ctrl+c', on_ctrl_c)
keyboard.wait()