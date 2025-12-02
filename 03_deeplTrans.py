import deepl

# TODO: 실제 DeepL API 인증 키로 교체하세요.
auth_key = "3b9c5c42-29d9-4cc8-9289-ecf6bf01c2b7:fx" 
translator = deepl.Translator(auth_key)

# 텍스트 내의 '??' 부분을 's' 또는 올바른 아포스트로피 '’'로 수정하는 것을 권장합니다.
text = "GPT-4 is more creative and collaborative than ever before. It can generate, edit, and iterate with users on creative and technical writing tasks, such as composing songs, writing screenplays, or learning a user's writing style."

try:
    result = translator.translate_text(text, target_lang="KO")
    print(result.text)
except deepl.exceptions.DeepLException as e:
    print(f"DeepL API 오류 발생: {e}")
except Exception as e:
    print(f"예상치 못한 오류 발생: {e}")