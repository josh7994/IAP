##### 기본 정보 입력 ##### 
## 라이브러리 설치: pip install streamlit PyPDF2 langchain deepl openai langchain-community tiktoken faiss-cpu  
## 프로그램 실행: streamlit run 02_PDF_answer_app.py
# Streamlit 패키지 추가
import streamlit as st
# PDF reader
from PyPDF2 import PdfReader
# Langchain 패키지들
from langchain_community.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
# deepl 번역 패키지 설치 
import deepl     

##### 기능 구현 함수 #####

# 영어 번역
def deepl_trans(messages):
    auth_key = "3b9c5c42-29d9-4cc8-9289-ecf6bf01c2b7:fx" 
    translator = deepl.Translator(auth_key)

    try:
        result = translator.translate_text(messages, target_lang="KO")
        return result.text
    except deepl.exceptions.DeepLException as e:
        print(f"DeepL API 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")


##### 메인 함수 #####
def main():
    st.set_page_config(page_title="PDF analyzer", layout="wide")

    # 사이드바
    with st.sidebar:

        # Open AI API 키 입력받기
        open_apikey = st.text_input(label='OPENAI API 키', placeholder='Enter Your API Key', value='',type='password')
        
        # 입력받은 API 키 표시
        if open_apikey:
            st.session_state["OPENAI_API"] = open_apikey 
        st.markdown('---')
        
    # 메인공간
    st.header("PDF 내용 질문 프로그램📜")
    st.markdown('---')
    st.subheader("PDF 파일을 넣으세요")
    # PDF 파일 받기
    pdf = st.file_uploader(" ", type="pdf")
    if pdf is not None:
        # PDF 파일 텍스트 추출하기
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        # 청크 단위로 분할하기
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        st.markdown('---')
        st.subheader("질문을 입력하세요")
        # 사용자 질문 받기
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            # 임베딩/ 시멘틱 인덱스
            embeddings = OpenAIEmbeddings(openai_api_key=st.session_state["OPENAI_API"])
            knowledge_base = FAISS.from_texts(chunks, embeddings)
            
            docs = knowledge_base.similarity_search(user_question)

            # 질문하기
            llm = ChatOpenAI(temperature=0,
                    openai_api_key=st.session_state["OPENAI_API"],
                    max_tokens=2000,
                    model_name='gpt-3.5-turbo',
                    requesstt_timeout=120
                    )
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)
            # 답변결과
            st.info(response)
            #한국어로 번역하기
            if st.button(label="번역하기"):
                trans = deepl_trans(response)
                st.success(trans)

if __name__=='__main__':
    main()