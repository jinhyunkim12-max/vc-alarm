import requests
from bs4 import BeautifulSoup
import datetime
import pytz # 시차 해결용 도구

# ==========================================
# [사용자 설정] 본인의 봇 토큰과 채팅 ID로 꼭! 다시 바꿔주세요
TELEGRAM_TOKEN = "7690518189:AAFr5eue6klClHix1rque5DGU0eZFMT2Stc"
CHAT_ID = "1230013620"
# ==========================================

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def get_today_kst():
    # 미국 서버 시간 대신 '한국 시간(KST)' 기준으로 오늘 날짜를 가져옵니다.
    kst = pytz.timezone('Asia/Seoul')
    return datetime.datetime.now(kst).strftime("%Y-%m-%d")

def check_new_post():
    today = get_today_kst()
    print(f"[{today}] 한국 시간 기준으로 공고 확인 시작...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 1. 한국벤처투자 (KVIC)
    try:
        url = "https://www.kvic.or.kr/notice/notice01"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 첫 번째 글만 보지 않고, 위에서 10개(tr)를 다 뒤집니다.
        rows = soup.select('.board_list tbody tr')
        for row in rows[:10]: 
            try:
                date_text = row.select('td')[3].get_text(strip=True).replace('.', '-')
                if date_text == today:
                    title = row.select_one('td.subject a').get_text(strip=True)
                    link = "https://www.kvic.or.kr" + row.select_one('td.subject a')['href']
                    send_telegram(f"🔔 [한국벤처투자] 발견!\n{title}\n{link}")
                    print(f"전송 완료: {title}")
            except:
                continue # 날짜 형식이 다르거나 공지글이면 패스
    except Exception as e:
        print(f"KVIC 오류: {e}")

    # 2. 한국성장금융
    try:
        url = "https://www.kgrowth.or.kr/notice.asp"
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        rows = soup.select('.tbl_board tbody tr')
        for row in rows[:10]:
            try:
                date_text = row.select('td')[2].get_text(strip=True).replace('.', '-')
                if date_text == today:
                    title = row.select_one('td.subject a').get_text(strip=True)
                    link = "https://www.kgrowth.or.kr/notice.asp"
                    send_telegram(f"🔔 [한국성장금융] 발견!\n{title}\n{link}")
            except:
                continue
    except Exception as e:
        print(f"K-Growth 오류: {e}")

    # 3. 한국벤처캐피탈협회 (KVCA)
    try:
        url_kvca = "https://www.kvca.or.kr/Program/invest/list.html?a_gb=board&a_cd=8&a_item=0&sm=2_2_2"
        res = requests.get(url_kvca, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 테이블의 모든 줄을 가져옵니다
        rows = soup.select('table tbody tr')
        
        for row in rows[:10]: # 위에서 10개만 확인
            try:
                # KVCA는 날짜가 보통 뒤에서 두 번째 칸에 있습니다.
                cols = row.select('td')
                if len(cols) < 3: continue # 내용 없는 줄 패스

                date_text = cols[-2].get_text(strip=True).replace('.', '-')
                
                # 오늘 날짜와 똑같으면 전송
                if date_text == today:
                    title_tag = row.select_one('a')
                    title = title_tag.get_text(strip=True)
                    link_suffix = title_tag['href']
                    link = f"https://www.kvca.or.kr/Program/invest/{link_suffix}"
                    
                    send_telegram(f"🔔 [KVCA] 발견!\n{title}\n{link}")
            except:
                continue
    except Exception as e:
        print(f"KVCA 오류: {e}")

if __name__ == "__main__":
    check_new_post()
