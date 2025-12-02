##### 기본 정보 불러오기 ####
# Streamlit 패키지 추가
import streamlit as st
# OpenAI 패키지 추가
import openai
# google-cloud-translate-v2 라이브러리 사용
from google.cloud import translate_v2 as translate
# Deepl 번역 패키지 추가
import deepl
# 파파고 API요청을 위한 Requests 패키지 추가 
import requests

##### 기능 구현 함수 #####
# ChatGPT 번역
def gpt_translate(text: str, apikey: str) -> str:
    """
    주어진 영어 텍스트를 GPT 모델을 사용해 한국어로 번역합니다.

    Args:
        text (str): 번역할 영어 텍스트입니다.
        apikey (str): OpenAI API 키입니다.

    Returns:
        str: 번역된 한국어 텍스트 또는 에러 메시지를 반환합니다.
    """
    try:
        client = openai.OpenAI(api_key=apikey)

        # 시스템 역할을 지정하여 모델의 작동 방식을 명확히 설정합니다.
        # 사용자 메시지에는 번역할 텍스트만 간단히 전달합니다.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates English to Korean."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        # API 호출 중 발생할 수 있는 모든 에러를 처리합니다.
        print(f"An error occurred: {e}")
        return f"번역 중 에러가 발생했습니다: {e}"

# 파파고 번역
def papago_translate(text,PAPAGO_ID,PAPAGO_PW):
    data = {'text' : text,
            'source' : 'en',
            'target': 'ko'}

    url = "https://papago.apigw.ntruss.com/nmt/v1/translation"

    header = {"X-NCP-APIGW-API-KEY-ID":PAPAGO_ID,
              "X-NCP-APIGW-API-KEY":PAPAGO_PW}

    response = requests.post(url, headers=header, data=data)
    rescode = response.status_code

    if(rescode==200):
        send_data = response.json()
        trans_data = (send_data['message']['result']['translatedText'])
        return trans_data
    else:
        print("Error Code:" , rescode)

# 구글 번역
def google_trans(messages):
     google = Translator()
     result = google.translate(messages, dest="ko")

     return result.text

def google_trans(messages):
  """
  공식 Google Cloud Translation API를 사용하여 텍스트를 번역합니다.
  """
  try:
    # 번역 클라이언트 초기화
    translate_client = translate.Client()

    # 문자열 입력 확인
    if not isinstance(messages, str):
      raise ValueError("Input must be a string")

    # 번역 실행
    result = translate_client.translate(messages, target_language="ko")
    
    # 번역된 텍스트만 반환
    return result['translatedText']
    
  except Exception as e:
    return f"Translation error: {str(e)}"

# 디플 번역
def deepl_translate(text, deeplAPI):
    translator = deepl.Translator(deeplAPI)

    try:
        result = translator.translate_text(text, target_lang="KO")
    except deepl.exceptions.DeepLException as e:
        print(f"DeepL API 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")   
         
    return result.text

##### 메인 함수 #####
def main():
    # 기본 설정
    st.set_page_config(
        page_title="번역 플랫폼 모음",
        layout="wide")

    # session state 초기화
    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""

    if "PAPAGO_ID" not in st.session_state:
        st.session_state["PAPAGO_ID"] = ""

    if "PAPAGO_PW" not in st.session_state:
        st.session_state["PAPAGO_PW"] = ""

    if "DeeplAPI" not in st.session_state:
        st.session_state["DeeplAPI"] = ""


    # 사이드바 바 생성
    with st.sidebar:

        # Open AI API 키 입력받기
        st.session_state["OPENAI_API"] = st.text_input(label='OPENAI API 키', placeholder='Enter Your OpenAI API Key', value='',type='password')

        st.markdown('---')

        # PAPAGO API ID/PW 입력받기
        st.session_state["PAPAGO_ID"] = st.text_input(label='PAPAGO API ID', placeholder='Enter PAPAGO ID', value='')
        st.session_state["PAPAGO_PW"] = st.text_input(label='PAPAGO API PW', placeholder='Enter PAPAGO PW', value='',type='password')

        st.markdown('---')

        # Deepl API 키 입력받기
        st.session_state["DeeplAPI"] = st.text_input(label='Deepl API 키', placeholder='Enter Your Deepl API API Key', value='',type='password')
    
        st.markdown('---')

    # 제목 
    st.header('번역 플랫폼 비교하기 프로그램')
    # 구분선
    st.markdown('---')
    st.subheader("번역을 하고자 하는 텍스트를 입력하세요")
    txt = st.text_area(label="",placeholder="input English..", height=200)
    st.markdown('---')

    st.subheader("ChatGPT 번역 결과")
    st.text("https://openai.com/blog/chatgpt")
    if st.session_state["OPENAI_API"] and txt:
        result = gpt_translate(txt,st.session_state["OPENAI_API"])
        st.info(result)
    else:
        st.info('API 키를 넣으세요')
    st.markdown('---')

    st.subheader("파파고 번역 결과")
    st.text("https://papago.naver.com/")
    if st.session_state["PAPAGO_ID"] and st.session_state["PAPAGO_PW"] and txt:
        result = papago_translate(txt,st.session_state["PAPAGO_ID"],st.session_state["PAPAGO_PW"])
        st.info(result)
    else:
        st.info('파파고 API ID, PW를 넣으세요')
    st.markdown('---')

    st.subheader("Deepl 번역 결과")
    st.text("https://www.deepl.com/translator")
    if st.session_state["DeeplAPI"] and txt:
        result = deepl_translate(txt,st.session_state["DeeplAPI"])
        st.info(result)
    else:
        st.info('API 키를 넣으세요')

    st.subheader("구글 번역 결과")
    st.text("https://translate.google.co.kr/")
    if txt:
        result = google_trans(txt)
        st.info(result)
    else:
        st.info("API키가 필요 없습니다")
    st.markdown('---')

if __name__=="__main__":
    main()
