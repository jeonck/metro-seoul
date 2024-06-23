import streamlit as st
import requests
import xmltodict
import pandas as pd
import base64
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키를 입력하세요
API_KEY = os.getenv("API_KEY")

# 서울 지하철 실시간 도착 정보 API URL
API_URL = 'http://swopenapi.seoul.go.kr/api/subway/{}/xml/realtimeStationArrival/1/5/{}'.format(API_KEY, '서울')


def fetch_data(station_name):
    # API 요청 URL 생성
    url = f'http://swopenapi.seoul.go.kr/api/subway/{API_KEY}/xml/realtimeStationArrival/1/5/{station_name}'

    # API 요청
    response = requests.get(url)
    if response.status_code == 200:
        data = xmltodict.parse(response.content)
        if 'realtimeStationArrival' in data and 'row' in data['realtimeStationArrival']:
            return data['realtimeStationArrival']['row']
        else:
            st.error("잘못된 역 이름이거나, 데이터를 불러오는데 실패했습니다.")
            return []
    else:
        st.error("API 요청에 실패했습니다.")
        return []


def main():
    st.title('서울 지하철 실시간 도착 정보')

    # 사용자 입력을 통해 역 이름 받기
    station_name = st.text_input('지하철 역 이름을 입력하세요:', '서울')

    if station_name:
        data = fetch_data(station_name)

        if data:
            df = pd.DataFrame(data)
            st.write(f"**{station_name} 역 실시간 도착 정보**")
            st.dataframe(df[['trainLineNm', 'updnLine', 'arvlMsg2', 'arvlMsg3', 'recptnDt']])
        else:
            st.write("데이터가 없습니다.")

    # 지하철 노선도 이미지 base64로 인코딩
    with open("./routemap.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    zoomable_image_html = f"""
    <div style="overflow: hidden; width: 100%; height: 600px; position: relative;">
        <img src="data:image/jpg;base64,{encoded_image}" style="width:100%; max-width: none; transform-origin: center;" id="zoomable_image">
    </div>
    <script>
        const img = document.getElementById('zoomable_image');
        let scale = 1;
        let originX = 0.5;
        let originY = 0.5;

        img.onwheel = (event) => {{
            event.preventDefault();
            if (event.deltaY < 0) {{
                scale *= 1.1;
            }} else {{
                scale /= 1.1;
            }}
            img.style.transform = `scale(${{scale}})`;
        }};

        img.onclick = (event) => {{
            const rect = img.getBoundingClientRect();
            originX = (event.clientX - rect.left) / rect.width;
            originY = (event.clientY - rect.top) / rect.height;
            img.style.transformOrigin = `${{originX * 100}}% ${{originY * 100}}%`;
        }};
    </script>
    """

    st.markdown(zoomable_image_html, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
