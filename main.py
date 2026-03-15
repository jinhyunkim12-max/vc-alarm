import os
import feedparser
import requests
import google.generativeai as genai

# 1. 환경 변수 로드 (GitHub Secrets에서 가져옴)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 2. Gemini AI 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_latest_news(query="스타트업 OR 벤처캐피탈 OR 투자유치", limit=5):
    """구글 뉴스 RSS를 통해 최신 뉴스 수집"""
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    return feed.entries[:limit]

def generate_insights(title, link):
    """Gemini를 이용한 요약 및 발제 아이디어 생성"""
    # 기자님의 교정 스타일을 반영한 페르소나 설정
    prompt = f"""
    당신은 머니투데이 유니콘팩토리의 베테랑 기사이자 데스크입니다. 
    다음 기사를 읽고 전문적인 요약과 취재 발제안을 작성하세요.

    [작성 및 교정 규칙]
    1. 숫자에 천 단위 쉼표를 절대 쓰지 마세요. (예: 1,000 -> 1000)
    2. '억원', '천만원' 등 금액 단위는 숫자 뒤에 붙여 쓰세요. (예: 150억 원 -> 150억원)
    3. 통화 기호나 화폐 단위는 숫자 앞에 붙이세요.
    4. 문체는 시장 분석가답게 냉철하고 명확하게 작성하세요.

    기사 제목: {title}
    기사 링크: {link}

    [형식]
    ■ 핵심 요약: (2~3줄 내외)
    ■ 취재 발제: (기존 보도와 차별화되는 심층 취재 아이디어 1개)
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"분석 오류 발생: {e}"

def send_telegram_message(text):
    """텔레그램 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    articles = get_latest_news(limit=5)
    
    header = "🚀 **[Daily VC/Startup Briefing]**\n\n"
    send_telegram_message(header)
    
    for article in articles:
        content = generate_insights(article.title, article.link)
        msg = f"🔗 **[{article.title}]({article.link})**\n{content}\n"
        msg += "──────────────"
        send_telegram_message(msg)
