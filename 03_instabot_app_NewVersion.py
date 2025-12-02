### 공식 구글 클라우드 번역 라이브러리 사용 ###
# 1. 공식 구글 클라우드 번역 라이브러리 설치 
# pip install google-cloud-translate
# 2. 구글 클라우드 프로젝트 설정 및 인증
# gcloud auth application-default login

##### 기본 정보 입력 #####
import streamlit as st
# OpenAI 패키기 추가 
import openai
# 인스타그램 패키기 추가
from instagrapi import Client
#이미지 처리
from PIL import Image
import urllib
# Deepl 번역 패키지 추가
import deepl

# #구글 번역
# # google-cloud-translate-v2 라이브러리 사용
# from google.cloud import translate_v2 as translate 

import os


##### 기능 구현 함수 #####
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

# # 구글 번역 API를 사용하여 텍스트를 번역하는 함수
# def google_trans(messages, dest_lang="en"):
#     """
#     Google Cloud Translation API를 사용하여 텍스트를 번역합니다.

#     Args:
#         messages (str): 번역할 문자열.
#         dest_lang (str): 번역할 대상 언어 코드 (예: "ko", "en").

#     Returns:
#         str: 번역된 텍스트 또는 오류 메시지.
#     """
#     try:
#         # 번역 클라이언트 초기화
#         translate_client = translate.Client()

#         # Google 번역 API에 요청을 보낼 때 유효한 텍스트만 처리하기 위해 입력 문자열 확인 
#         if not isinstance(messages, str):
#             raise ValueError("입력은 문자열이어야 합니다.")
#         if not messages.strip():
#             raise ValueError("입력 문자열이 비어 있습니다.")

#         # 번역 실행
#         result = translate_client.translate(messages, target_language=dest_lang)

#         return result['translatedText']

#     except Exception as e:
#         return f"번역 오류: {str(e)}"


# 인스타 업로드
def uploadinstagram(description):
    cl = Client()
    cl.login(st.session_state["instagram_ID"], st.session_state["instagram_Password"])
    cl.photo_upload("instaimg_resize.jpg" , description)


# ChatGPT에게 질문/답변받기
def getdescriptionFromGPT(topic, mood, apikey):
    prompt = f'''
Write me the Instagram post description or caption in just a few sentences for the post 
-topic : {topic}
-Mood : {mood}
Format every new sentence with new lines so the text is more readable.
Include emojis and the best Instagram hashtags for that post.
The first caption sentence should hook the readers.
write all output in korean.'''
    
    # messages_prompt = [{"role": "system", "content": prompt}]
    try: 
        client = openai.OpenAI(api_key = apikey) 

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Instagram post descriptions."},
                {"role": "user", "content": prompt } 
            ], 
            max_tokens=200,
            temperature=0.7
        )
        gptResponse = response.choices[0].message.content.strip()
        return gptResponse
    
    except openai.APIConnectionError as e:
        st.error(f"OpenAI API 연결 오류: {e}")
        return "GPT 호출 실패 - 인터넷 연결 또는 API 설정을 확인하세요."

    except openai.OpenAIError as e:
        st.error(f"OpenAI 오류: {e}")
        return "GPT 호출 중 오류가 발생했습니다."

    except Exception as e:
        st.error(f"예상치 못한 오류: {e}")
        return "예기치 않은 오류가 발생했습니다."

# DALLE.2에게 질문/그림 URL 받기
def getImageURLFromDALLE(topic, mood, apikey):
    t_topic = deepl_translate(topic, st.session_state["Deepl_API"])
    t_mood = deepl_translate(mood, st.session_state["Deepl_API"])
    prompt_ = f'Draw picture about {t_topic}. picture Mood is {t_mood}'
    client = openai.OpenAI(api_key = apikey)

    try:
        # 이미지 생성 요청
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt_,
            size="1024x1024",
            # quality="standard",
            n=1,
        )

        # 이미지 URL 추출
        image_url = response.data[0].url

        # 이미지 다운로드
        urllib.request.urlretrieve(image_url, "instaimg.jpg")
        
    except openai.APIError as e:
        print(f"OpenAI API error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


##### 메인 함수 #####
def main():

    # 기본 설정
    st.set_page_config(page_title="Instabot", page_icon="?")
    
    # session state 초기화
    if "description" not in st.session_state:
        st.session_state["description"] = ""

    # 플래그 초기화
    # 플래그는 생성 버튼을 누른 후에만 True로 변경되어,
    # 이후에 이미지와 설명을 표시하고 업로드 버튼을 활성화합니다.
    if "flag" not in st.session_state:
        st.session_state["flag"] = False

    if "instagram_ID" not in st.session_state:
        st.session_state["instagram_ID"] = ""

    if "instagram_Password" not in st.session_state:
        st.session_state["instagram_Password"] = ""

    if "OPENAI_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""

    if "Deepl_API" not in st.session_state:
        st.session_state["Deepl_API"] = ""

    # 제목 
    st.header('인스타그램 포스팅 생성기')
    # 구분선
    st.markdown('---')

    # 기본 설명
    with st.expander("인스타그램 포스팅 생성기", expanded=True):
        st.write(
        """     
        - 인스타그램 포스팅 생성 UI는 스트림릿을 활용하여 만들었습니다.
        - 포스팅 글은 OpenAI의 GPT모델을 활용하여 생성합니다. 
        - 이미지는 OpenAI의 Dall.e 2를 활용하여 생성합니다. 
        - 자동 포스팅은 instagram API를 활용합니다.
        """
        )

        st.markdown("")

    # 사이드바 바 생성
    with st.sidebar:
        # Open AI API 키 입력받기
        open_apikey = st.text_input(label='OPENAI API 키', placeholder='Enter Your API Key', value='',type="password")

        # 입력받은 API 키 표시
        if open_apikey:
            st.session_state["OPENAI_API"] = open_apikey    
        
        st.markdown('---')

        # Deepl API 키 입력받기
        deepl_apikey = st.text_input(label='Deepl API 키', placeholder='Enter Your Deepl API API Key', value='',type='password')
        
        # 입력받은 API 키 표시
        if deepl_apikey:
            st.session_state["Deepl_API"] = deepl_apikey

        st.markdown('---')




    topic = st.text_input(label="주제", placeholder="축구, 인공지능...")
    mood = st.text_input(label="분위기 (e.g. 재미있는, 진지한, 우울한)",placeholder="재미있는")

    # "생성" 버튼 
    # flag이 False일 때만 동작 
    # 생성 버튼을 누르면 GPT로부터 설명을 받고, DALL-E로부터 이미지를 생성합니다.
    # 이후 flag를 True로 변경하여 이미지와 설명을 표시합니다.
    # flag가 True일 때는 이미지와 설명을 표시하고, 업로드 버튼을 활성화합니다.
    # 업로드 버튼을 누르면 인스타그램에 이미지를 업로드합니다.
    # 업로드 후에는 flag를 다시 False로 변경하여 초기 상태로 돌아갑니다.
    # Streamlit은 이벤트가 발생하면 전체 스크립트를 다시 실행하기 때문에,
    # flag를 사용하여 상태를 유지합니다.
    if st.button(label="생성",type="secondary") and not st.session_state["flag"]:
        # spinner를 사용하여 '생성 중'임을 표시
        # with 이하의 들여쓰기 코드가 실행될 때까지 로딩 스피너가 표시됩니다.
        with st.spinner('생성 중'):
            st.session_state["description"] = getdescriptionFromGPT(topic,mood,st.session_state["OPENAI_API"])
            getImageURLFromDALLE(topic,mood,st.session_state["OPENAI_API"])
            st.session_state["flag"] = True

    if st.session_state["flag"]:
        image = Image.open('instaimg.jpg')  
        st.image(image)
        # st.markdown(st.session_state["description"])
        txt = st.text_area(label = "Edit Description",value  = st.session_state["description"],height=100)
        st.session_state["description"] = txt

        st.markdown('인스타그램 ID/PW')
        # 인스타그램 ID 입력받기
        st.session_state["instagram_ID"] = st.text_input(label='ID', placeholder='Enter Your ID', value='')
        # 인스타그램 비밀번호
        st.session_state["instagram_Password"] = st.text_input(label='Password',type='password', placeholder='Enter Your Password', value='')

        if st.button(label='업로드'):
            image = Image.open("instaimg.jpg")
            image = image.convert("RGB")
            new_image = image.resize((1080, 1080))
            new_image.save("instaimg_resize.jpg")
            uploadinstagram(st.session_state["description"])
            st.session_state["flag"] = False

if __name__=="__main__":
    main()