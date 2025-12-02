# 가상환경에서 실행하는 것을 권장합니다.
# 구글 클라우드 번역 API를 사용하여 문자열을 번역하는 예제입니다.
# 이 코드를 실행하기 전에 필요한 라이브러리를 설치하고 인증을 설정해야 합니다.

# 1. 공식 구글 클라우드 번역 라이브러리 설치 
# pip install google-cloud-translate

# 2. 구글 클라우드 프로젝트 설정 및 인증
# gcloud auth application-default login 


# google-cloud-translate-v2 라이브러리 사용
from google.cloud import translate_v2 as translates

def google_trans(messages, dest_lang="ko"):
  """
  공식 Google Cloud Translation API를 사용하여 텍스트를 번역합니다.

  Args:
    messages (str): 번역할 문자열.
    dest_lang (str): 번역할 대상 언어 코드 (예: "ko", "en").

  Returns:
    str: 번역된 텍스트 또는 오류 메시지.
  """
  try:
    # 번역 클라이언트 초기화
    translate_client = translate.Client()

    # 문자열 입력 확인
    if not isinstance(messages, str):
      raise ValueError("Input must be a string")

    # 번역 실행
    result = translate_client.translate(messages, target_language=dest_lang)
    
    # 번역된 텍스트만 반환
    return result['translatedText']
    
  except Exception as e:
    return f"Translation error: {str(e)}"

# 번역할 텍스트
text = "GPT-4 is more creative and collaborative than ever before. It can generate, edit, and iterate with users on creative and technical writing tasks, such as composing songs, writing screenplays, or learning a user’s writing style."

# 함수 호출 및 결과 출력
result = google_trans(text)
print(f"Translated text: {result}")

# 영어로 번역하는 경우
# result_en = google_trans("안녕하세요", dest_lang="en")
# print(f"Translated text (EN): {result_en}")