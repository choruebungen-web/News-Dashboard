import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="미디어/방송 뉴스 모니터링", layout="wide")
st.title("📰 일일 뉴스 모니터링 대시보드")

with st.sidebar:
    st.header("설정")
    keyword_input = st.text_area(
        "추적할 키워드 (쉼표로 구분)", 
        value="국제OTT포럼, 시청각미디어서비스법안, 국회 과방위, 방송통신위원회, 스포츠 중계권"
    )
    search_button = st.button("뉴스 수집 시작")

def get_naver_news(keyword):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    news_list = soup.select(".news_area")
    
    for news in news_list[:10]:
        title_tag = news.select_one(".news_tit")
        info_tag = news.select_one(".info_group > a.info.press")
        if title_tag and info_tag:
            articles.append({
                "키워드": keyword,
                "언론사": info_tag.text.replace("언론사 선정", ""),
                "제목": title_tag.get("title") or title_tag.text,
                "링크": title_tag.get("href")
            })
    return articles

if search_button:
    keywords = [k.strip() for k in keyword_input.split(',')]
    all_news = []
    with st.spinner('뉴스를 수집하는 중입니다...'):
        for kw in keywords:
            if kw:
                all_news.extend(get_naver_news(kw))
    
    if all_news:
        df = pd.DataFrame(all_news)
        st.success(f"총 {len(df)}건의 기사를 가져왔습니다. ({datetime.now().strftime('%Y-%m-%d %H:%M 기준')})")
        st.dataframe(df, column_config={"링크": st.column_config.LinkColumn("기사 링크")}, hide_index=True, use_container_width=True)
    else:
        st.warning("검색된 뉴스가 없습니다.")
