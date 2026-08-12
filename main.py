import os
import requests
import subprocess
from datetime import datetime, timedelta
import email.utils

# 1. 환경 변수 세팅
raw_queries = os.environ.get("SEARCH_QUERIES", "바이브코딩")
SEARCH_QUERIES = [q.strip() for q in raw_queries.split(",") if q.strip()]

CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

def process_query(query, time_limit, now_kst):
    """개별 검색어에 대해 뉴스를 검색하고 단독 이슈(게시글)를 생성합니다."""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    params = {"query": query, "display": 100, "sort": "date"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    date_str = now_kst.strftime("%Y-%m-%d")
    issue_title = f"[{date_str}] '{query}' 관련 뉴스"
    
    body_lines = [
        f"## 📰 '{query}' 24시간 이내 최신 뉴스",
        f"**업데이트 시간:** {now_kst.strftime('%Y-%m-%d %H:%M')} (KST)\n",
        "---"
    ]

    count = 0
    for item in data.get('items', []):
        pub_date_tuple = email.utils.parsedate_tz(item['pubDate'])
        if pub_date_tuple:
            pub_date = datetime.fromtimestamp(email.utils.mktime_tz(pub_date_tuple))
            if pub_date >= time_limit:
                title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                link = item['originallink'] or item['link']
                pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M')
                body_lines.append(f"- [{title}]({link}) `({pub_date_str})`")
                count += 1

    if count == 0:
        body_lines.append("- 24시간 이내에 새로 올라온 관련 기사가 없습니다.")

    # 2. 본문 내용을 임시 파일로 저장
    temp_filename = "temp_issue_body.md"
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(body_lines))
    
    # 3. 파이썬에서 직접 GitHub CLI 명령어를 실행하여 이슈 생성!
    print(f"'{query}' 이슈 생성 중...")
    subprocess.run([
        "gh", "issue", "create", 
        "--title", issue_title, 
        "--body-file", temp_filename
    ], check=True)

def main():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    time_limit = now_kst - timedelta(hours=24)
    
    # 4. 등록된 검색어 개수만큼 반복 실행 (각각 따로 파일/게시글 생성)
    for query in SEARCH_QUERIES:
        process_query(query, time_limit, now_kst)

if __name__ == "__main__":
    main()
