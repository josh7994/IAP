# 가상환경을 만들어서 아래의 라이브러리를 설치해야 합니다.
# pip install langchain langchain-community langchain-openai faiss-cpu 
# pip install sentence-transformers python-dotenv langchain-huggingface
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader  # 수정: langchain_community로 변경
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # 수정: langchain_huggingface로 변경
from langchain_community.vectorstores import FAISS  # 수정: langchain_community로 변경
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 환경 변수 로드 (OpenAI API 키 설정) 
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")  # .env 파일에 API 키 저장

# 1. 데이터 로드 
# 실제로 WikipediaLoader로 확장 가능
loader = TextLoader("documents.txt")  # 위 데이터 파일 경로
documents = loader.load()

# 2. 텍스트 분할 (chunking) (오버랩으로 맥락 유지) 
# 문서 분할(Chunking): RAG 시스템에서는 입력 문서가 너무 길 경우, 이를 작은 조각(chunk)으로 나누는 과정이 필요함 
# 이는 벡터 스토어(예: FAISS)에 저장하거나 검색(retrieval)할 때 효율성을 높이고, LLM의 토큰 제한을 준수하기 위함
# RecursiveCharacterTextSplitter는 LangChain에서 제공하는 텍스트 분할 도구로, 문서를 지정된 크기의 조각으로 나눔 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# 3. 임베딩 모델 및 벡터 스토어 생성 
# Hugging Face의 오픈소스 모델 사용 (OpenAI 임베딩으로 대체 가능)  
# "sentence-transformers/all-MiniLM-L6-v2" 모델은 가볍고 빠름
# FAISS로 검색 가능한 인덱스 생성
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(texts, embeddings)

# 4. 리트리버 설정 
# 벡터 스토어(vectorstore, 여기서는 FAISS)를 사용하여 입력 질문과 가장 관련성 높은 문서 조각을 검색하는 리트리버 객체 생성 
# "similarity" 검색 방식과 상위 2개 문서 검색(k=2) 설정
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})  # 상위 2개 문서 검색

# 5. LLM 설정 및 RAG 체인 구성
# LLM 설정: ChatOpenAI를 사용해 GPT-3.5-turbo 모델을 초기화하여 질문에 대한 답변을 생성할 준비를 함  
# RAG 체인 구성: RetrievalQA 체인을 설정하여 검색(retrieval)과 생성(generation)을 결합함 
# 이는 질문에 대해 관련 문서를 검색하고, 해당 문서를 기반으로 LLM이 답변을 생성하도록 함 
# RAG에서의 역할: 이 코드는 RAG 파이프라인의 생성(generation) 단계를 담당하며, 검색된 문서를 LLM에 입력하여 정확하고 
# 문맥에 맞는 답변을 생성함 
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)  # 0.7은 사실성과 창의성의 균형을 맞춘 일반적인 설정 
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # "stuff"는 검색된 문서를 단순히 연결하여 LLM에 전달하는 방식을 의미
    retriever=retriever,
    return_source_documents=True # 답변과 함께 출처 문서도 반환하도록 설정
)

# 6. 테스트 질문
query = "What is deep learning?"
result = qa_chain.invoke({"query": query})  # 수정: __call__ 대신 invoke 사용

# 결과 출력
print("Answer:", result["result"])
print("\nSource Documents:")
for doc in result["source_documents"]:
    print(doc.page_content)