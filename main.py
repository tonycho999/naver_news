import os
import requests
from datetime import datetime, timedelta
import email.utils

# 1. 환경 변수 불러오기
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
SEARCH_QUERY = os.environ.get("SEARCH_QUERY", "서서울호수공원")

def fetch_and_prepare_issue():
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    params = {"query": SEARCH_QUERY, "display": 100, "sort": "date"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # 한국 시간(KST) 설정 및 24시간 제한 계산
    now_kst = datetime.utcnow() + timedelta(hours=9)
    time_limit = now_kst - timedelta(hours=24)

    # 2. 이슈 제목 생성 (예: [2026-08-11] '서서울호수공원' 뉴스 모음)
    date_str = now_kst.strftime("%Y-%m-%d")
    issue_title = f"[{date_str}] '{SEARCH_QUERY}' 뉴스 모음"

    # 3. 이슈 본문(마크다운) 작성 시작
    body_lines = [
        f"## 📰 '{SEARCH_QUERY}' 24시간 이내 최신 뉴스",
        f"**업데이트 시간:** {now_kst.strftime('%Y-%m-%d %H:%M')} (KST)\n",
        "---"
    ]

    count = 0
    for item in data.get('items', []):
        pub_date_tuple = email.utils.parsedate_tz(item['pubDate'])
        if pub_date_tuple:
            pub_date = datetime.fromtimestamp(email.utils.mktime_tz(pub_date_tuple))
            if pub_date >= time_limit:
                # 특수문자 제거 및 변환
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                link = item['originallink'] or item['link']
                pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M')
                
                # 마크다운 리스트 형태로 추가: - [기사제목](링크) (발행시간)
                body_lines.append(f"- [{title}]({link}) `({pub_date_str})`")
                count += 1

    if count == 0:
        body_lines.append("- 24시간 이내에 새로 올라온 관련 기사가 없습니다.")

    # 4. 제목과 본문을 각각 파일로 저장 (GitHub Actions에서 읽어서 사용)
    with open("issue_title.txt", "w", encoding="utf-8") as f:
        f.write(issue_title)
    
    with open("issue_body.md", "w", encoding="utf-8") as f:
        f.write("\n".join(body_lines))

if __name__ == "__main__":
    fetch_and_prepare_issue()
