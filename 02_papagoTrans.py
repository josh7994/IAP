import requests

PAPAGO_ID = "gl7k8cgtqy" 
PAPAGO_PW = "mz8WDxHWF4SDYn7R7ZfE2S3P2dOhRB7RDTyZPuRy" 

#영어를 한국어로
def papago_translate(text):
     
    data = {'text' : text,
            'source' : 'en',
            'target': 'ko'} 

    url = "https://papago.apigw.ntruss.com/nmt/v1/translation"
    header = {"X-NCP-APIGW-API-KEY-ID":PAPAGO_ID,
              "X-NCP-APIGW-API-KEY":PAPAGO_PW}

    response = requests.post(url, headers=header, data=data)
    rescode = response.status_code

    if(rescode==200): #제대로 실행되었을때
        send_data = response.json()
        trans_data = (send_data['message']['result']['translatedText'])
        return trans_data
    else:
        print("Error Code:" , rescode)



text ="GPT-4 is more creative and collaborative than ever before. It can generate, edit, and iterate with users on creative and technical writing tasks, such as composing songs, writing screenplays, or learning a user??s writing style."

result = papago_translate(text)
print(result)