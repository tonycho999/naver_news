import os
import requests
from datetime import datetime, timedelta
import email.utils

CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
SEARCH_QUERY = os.environ.get("SEARCH_QUERY", "기본 검색어")

def fetch_recent_news():
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    params = {
        "query": SEARCH_QUERY,
        "display": 100,  # 최대 100개
        "sort": "date"   # 최신순
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # 24시간 전 시간 계산
    now = datetime.now()
    time_limit = now - timedelta(hours=24)

    print(f"[{SEARCH_QUERY}] 관련 24시간 이내 뉴스 제목\n" + "-"*40)

    count = 0
    for item in data.get('items', []):
        pub_date_tuple = email.utils.parsedate_tz(item['pubDate'])
        if pub_date_tuple:
            pub_date = datetime.fromtimestamp(email.utils.mktime_tz(pub_date_tuple))
            
            if pub_date >= time_limit:
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                print(f"- {title}")
                count += 1
                
    if count == 0:
        print("24시간 이내에 새로 올라온 관련 기사가 없습니다.")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("오류: GitHub Secrets에 API 키가 설정되지 않았습니다.")
    else:
        fetch_recent_news()
