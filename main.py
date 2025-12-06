import requests
from bs4 import BeautifulSoup
import datetime
import os

# ==========================================
# [사용자 설정] 본인 정보로 바꿔주세요
TELEGRAM_TOKEN = "7690518189:AAFr5eue6klClHix1rque5DGU0eZFMT2Stc"
CHAT_ID = "1230013620"
# ==========================================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

def check_new_post():
    # 오늘 날짜 구하기 (YYYY-MM-DD 형식)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"오늘 날짜: {today} 확인 시작...")

    # 1. 한국벤처투자 (KVIC)
    try:
        url = "https://www.kvic.or.kr/notice/"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 게시판 리스트의 첫 번째 줄 가져오기
        first_row = soup.select_one('.board_list tbody tr')
        if first_row:
            # 날짜 확인 (보통 4번째나 5번째 칸에 날짜가 있음, 사이트마다 다름)
            date_text = first_row.select('td')[3].get_text(strip=True) # 날짜 위치 추정
            title = first_row.select_one('td.subject a').get_text(strip=True)
            link = "https://www.kvic.or.kr" + first_row.select_one('td.subject a')['href']

            # 만약 게시글 날짜가 오늘과 같다면 알림 전송
            if date_text == today:
                send_telegram(f"🔔 [한국벤처투자] 오늘 뜬 공고!\n{title}\n{link}")
            else:
                print(f"KVIC: 오늘({today}) 올라온 공고 없음. (최신글: {date_text})")
    except Exception as e:
        print(f"KVIC 오류: {e}")

    # 2. 한국성장금융
    try:
        url = "https://www.kgrowth.or.kr/notice.asp"
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        first_row = soup.select_one('.tbl_board tbody tr')
        if first_row:
            date_text = first_row.select('td')[2].get_text(strip=True) # 날짜 위치
            title = first_row.select_one('td.subject a').get_text(strip=True)
            link = "https://www.kgrowth.or.kr/notice.asp"

            if date_text == today:
                send_telegram(f"🔔 [한국성장금융] 오늘 뜬 공고!\n{title}\n{link}")
            else:
                print(f"K-Growth: 오늘({today}) 올라온 공고 없음. (최신글: {date_text})")
    except Exception as e:
        print(f"K-Growth 오류: {e}")

if __name__ == "__main__":
    check_new_post()
