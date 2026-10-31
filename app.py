import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="미디어/방송 뉴스 모니터링", layout="wide")
st.title("Media News Dashboard")

with st.sidebar:
    st.header("설정")
    keyword_input = st.text_area(
        "추적할 키워드 (쉼표로 구분)", 
        value="방송미디어통신위원회, 방미통위, 방미심위, 과방위, 국제OTT포럼"
    )
    search_button = st.button("뉴스 수집 시작")

def get_google_news(keyword):
    # 한글 키워드를 주소용으로 변환
    encoded_keyword = urllib.parse.quote(keyword)
    # 구글 뉴스 RSS 주소 (한국어, 한국 지역 설정)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    
    articles = []
    try:
        # 봇 차단 방지용 헤더 추가
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        root = ET.fromstring(response)
        
        # 기사 내용 추출 (최대 15개)
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text if item.find('title') is not None else "제목 없음"
            link = item.find('link').text if item.find('link') is not None else ""
            source = item.find('source').text if item.find('source') is not None else "언론사 미상"
            
            articles.append({
                "키워드": keyword,
                "언론사": source,
                "제목": title,
                "링크": link
            })
    except Exception as e:
        pass
        
    return articles

if search_button:
    keywords = [k.strip() for k in keyword_input.split(',') if k.strip()]
    all_news = []
    
    with st.spinner('뉴스를 수집하는 중입니다...'):
        for kw in keywords:
            all_news.extend(get_google_news(kw))
    
    if all_news:
        df = pd.DataFrame(all_news)
        st.success(f"총 {len(df)}건의 기사를 가져왔습니다. ({datetime.now().strftime('%Y-%m-%d %H:%M 기준')})")
        
        # 데이터프레임 출력 설정
        st.dataframe(
            df, 
            column_config={"링크": st.column_config.LinkColumn("기사 링크")}, 
            hide_index=True, 
            use_container_width=True
        )
    else:
        st.warning("검색된 뉴스가 없습니다. 키워드를 변경해 보세요.")
