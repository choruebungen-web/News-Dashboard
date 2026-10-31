import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="미디어/방송 뉴스 모니터링", layout="wide")
st.title("Media News Dashboard")

with st.sidebar:
    st.header("설정")
    keyword_input = st.text_area(
        "추적할 키워드 (쉼표로 구분)", 
        value="방송미디어통신위원회, 방미통위, 방미심위, 과방위"
    )
    search_button = st.button("뉴스 수집 시작")

def get_naver_news(keyword):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    # 네이버의 봇 차단을 피하기 위해 진짜 크롬 브라우저처럼 위장하는 부분 (강화됨)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        articles = []
        news_list = soup.select(".news_area")
        
        for news in news_list[:10]:
            title_tag = news.select_one(".news_tit")
            # 언론사 태그 선택자를 더 유연하게 변경
            info_tag = news.select_one(".info_group .press") 
            
            if title_tag:
                press_name = info_tag.text.replace("언론사 선정", "").strip() if info_tag else "언론사 미상"
                articles.append({
                    "키워드": keyword,
                    "언론사": press_name,
                    "제목": title_tag.get("title") or title_tag.text,
                    "링크": title_tag.get("href")
                })
        return articles
    except Exception as e:
        return []

if search_button:
    keywords = [k.strip() for k in keyword_input.split(',') if k.strip()]
    all_news = []
    with st.spinner('뉴스를 수집하는 중입니다...'):
        for kw in keywords:
            all_news.extend(get_naver_news(kw))
    
    if all_news:
        df = pd.DataFrame(all_news)
        st.success(f"총 {len(df)}건의 기사를 가져왔습니다. ({datetime.now().strftime('%Y-%m-%d %H:%M 기준')})")
        st.dataframe(df, column_config={"링크": st.column_config.LinkColumn("기사 링크")}, hide_index=True, use_container_width=True)
    else:
        st.warning("검색된 뉴스가 없거나, 네이버에서 접근을 일시적으로 차단했습니다. 잠시 후 다시 시도해 주세요.")
