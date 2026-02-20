import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
from datetime import datetime
import os

# 1단계: 텔레그램 설정 (깃허브 Secrets에서 불러옴)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# 오늘 날짜 구하기 (형식: 2024-02-21 or 2024.02.21)
today_dash = datetime.now().strftime("%Y-%m-%d")
today_dot = datetime.now().strftime("%Y.%m.%d")

async def send_msg(text):
    bot = telegram.Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)

def check_new_post():
    new_posts = []
    
    # === 1. 한국벤처투자 (KVIC) ===
    try:
        url = "https://www.kvic.or.kr/notice/kvic-notice/investment-business-notice"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 첫 번째 게시물 가져오기
        latest = soup.select('table.board_list tbody tr')[0]
        date = latest.select('td')[3].text.strip() # 날짜 위치
        title = latest.select('td.subject a')[0].text.strip()
        link = "https://www.kvic.or.kr" + latest.select('td.subject a')[0]['href']

        if date == today_dash or date == today_dot:
            new_posts.append(f"[한국벤처투자]\n{title}\n{link}")
    except Exception as e:
        print(f"KVIC Error: {e}")

    # === 2. 한국성장금융 (K-Growth / 모바일) ===
    try:
        url = "https://m.kgrowth.or.kr/notice.asp?page=1"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 모바일 사이트 리스트 구조
        latest = soup.select('div.notice_list ul li')[0] 
        date = latest.select('span.date')[0].text.strip()
        title = latest.select('strong')[0].text.strip()
        # 링크는 자바스크립트 구조라 기본 공지 페이지로 대체
        link = "https://m.kgrowth.or.kr/notice.asp"

        if date == today_dash or date == today_dot:
            new_posts.append(f"[한국성장금융]\n{title}\n{link}")
    except Exception as e:
        print(f"K-Growth Error: {e}")

    # === 3. 농업정책보험금융원 (APFS / 키워드 필터링) ===
    try:
        url = "https://www.apfs.kr/front/board/boardContentsListPage.do?boardId=10026&menuId=41"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 게시물 리스트 순회 (키워드 찾기 위해 상위 3개 정도만 검색)
        rows = soup.select('div.board_list_wrap tbody tr')
        for row in rows[:3]:
            date = row.select('td')[4].text.strip()
            title = row.select('td.title_left a')[0].text.strip()
            link_id = row.select('td.title_left a')[0]['onclick'].split("'")[1]
            link = f"https://www.apfs.kr/front/board/boardContentsView.do?contentsId={link_id}&boardId=10026&menuId=41"
            
            # 날짜가 오늘이고, '출자'라는 단어가 포함된 경우만
            if (date == today_dash or date == today_dot) and ("출자" in title):
                new_posts.append(f"[농금원-출자]\n{title}\n{link}")
    except Exception as e:
        print(f"APFS Error: {e}")

    # === 4. 한국벤처캐피탈협회 (KVCA) ===
    try:
        url = "https://www.kvca.or.kr/Program/invest/list.html?a_gb=board&a_cd=8&a_item=0&sm=2_2_2"
        res = requests.get(url)
        res.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(res.text, 'html.parser')
        
        latest = soup.select('table.list_table tbody tr')[0]
        date = latest.select('td')[-1].text.strip() # 보통 맨 뒤가 조회수 아니면 날짜
        # KVCA는 날짜 형식이 다를 수 있어 확인 필요하지만 보통 YYYY.MM.DD
        title = latest.select('td.subject a')[0].text.strip()
        link = "https://www.kvca.or.kr/Program/invest/" + latest.select('td.subject a')[0]['href']

        if date == today_dash or date == today_dot:
            new_posts.append(f"[KVCA]\n{title}\n{link}")
    except Exception as e:
        print(f"KVCA Error: {e}")

    return new_posts

# 실행 및 전송
if __name__ == "__main__":
    posts = check_new_post()
    if posts:
        message = f"📢 {today_dash} VC 출자사업 알림 ({len(posts)}건)\n\n" + "\n\n".join(posts)
        asyncio.run(send_msg(message))
    else:
        print("새 공고 없음")
