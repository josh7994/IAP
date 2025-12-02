import openai
import urllib.request  # urllib.request를 명시적으로 임포트
from openai import OpenAI  # OpenAI 클래스 직접 임포트

# API 키 설정
client = OpenAI(api_key="")

try:
    # 이미지 생성 요청  
    # dall-e-2 모델을 사용하여 이미지를 생성합니다.
    # prompt_는 생성할 이미지에 대한 설명입니다. 
    response = client.images.generate(
        model="dall-e-2",
        prompt="racing car",
        size="1024x1024",
        # quality="standard",
        n=1, # 생성할 이미지 수
    )

    # 이미지 URL 추출
    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")

    # 이미지 다운로드
    urllib.request.urlretrieve(image_url, "test1.jpg")
    print("Image downloaded successfully as 'test1.jpg'")

except openai.APIError as e:
    print(f"OpenAI API error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")