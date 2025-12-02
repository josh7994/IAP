# 가상환경을 만들어서 아래의 라이브러리를 설치해야 합니다.
# pip install streamlit langchain langchain-openai langchain-community langchain-huggingface 
# pip install faiss-cpu wikipedia python-dotenv sentence-transformers

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import WikipediaLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 환경 변수 로드 (OpenAI API 키 설정)
# .env 파일에 OPENAI_API_KEY=your_openai_api_key 형식으로 키를 저장해야 합니다.
# 예: OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     
load_dotenv() # .env 파일에서 환경 변수 로드
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") # 환경 변수 설정
if not os.environ["OPENAI_API_KEY"]:
    st.error("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    st.stop()

# Streamlit 앱 제목
st.title("Wikipedia 기반 RAG Q&A 앱")

# 사이드바: Wikipedia 주제 입력 및 로드
with st.sidebar:
    st.header("데이터 로드")
    wiki_query = st.text_input("Wikipedia 주제 입력 (예: Artificial Intelligence)", value="Artificial Intelligence")
    load_button = st.button("Wikipedia 데이터 로드")

    # FAISS 인덱스 경로 (로컬 저장)
    persist_directory = "./faiss_index"

# 세션 상태 초기화
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False

# 데이터 로드 버튼 클릭 시
if load_button:
    with st.spinner("Wikipedia 데이터 로딩 중..."):
        # 1. Wikipedia 데이터 로드 (최대 5개 문서로 제한)
        loader = WikipediaLoader(query=wiki_query, load_max_docs=5)
        documents = loader.load()
        if not documents:
            st.error("Wikipedia에서 데이터를 로드하지 못했습니다. 주제를 확인하거나 네트워크를 점검하세요.")
            st.session_state.documents_loaded = False
            st.stop()
        st.success(f"{len(documents)}개의 Wikipedia 문서 로드 완료!")
        st.session_state.documents_loaded = True

        # 2. 텍스트 분할 (chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        texts = text_splitter.split_documents(documents)

        # 3. 임베딩 모델 및 FAISS 벡터 스토어 생성
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # 기존 FAISS 인덱스가 있으면 로드, 없으면 새로 생성
        if os.path.exists(persist_directory):
            st.session_state.vectorstore = FAISS.load_local(
                persist_directory,
                embeddings,
                allow_dangerous_deserialization=True
            )
            st.success("기존 FAISS 벡터 스토어 로드 완료!")
        else:
            st.session_state.vectorstore = FAISS.from_documents(
                texts,
                embeddings
            )
            st.session_state.vectorstore.save_local(persist_directory)
            st.success("새 FAISS 벡터 스토어 생성 완료!")

        # 4. 리트리버 설정
        retriever = st.session_state.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

        # 5. LLM 설정 및 RAG 체인 구성
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, timeout=30)
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        st.success("RAG 체인 구성 완료! 이제 질문을 입력하세요.")

# 메인 영역: 질문 입력 및 답변 표시
st.header("질문 입력")
user_query = st.text_input("질문을 입력하세요 (예: What is deep learning?)", key="user_query")

if user_query and st.session_state.qa_chain and st.session_state.documents_loaded:
    with st.spinner("답변 생성 중..."):
        result = st.session_state.qa_chain.invoke({"query": user_query})
        st.subheader("답변:")
        st.write(result["result"])
        
        st.subheader("소스 문서:")
        for doc in result["source_documents"]:
            st.write(doc.page_content)
            st.write("---")
else:
    if user_query:
        st.warning("먼저 Wikipedia 데이터를 로드하세요!")

# 앱 정보
st.info("이 앱은 Streamlit으로 구현된 RAG 예제입니다. FAISS 벡터 스토어를 사용해 벡터를 저장하고, Wikipedia API로 데이터를 로드합니다.")