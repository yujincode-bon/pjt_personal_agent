import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# .env 파일에서 OPENAI_API_KEY 등을 로드
load_dotenv()

# --- 1. 설정 ---
# 프로젝트 루트 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# PDF 파일 경로 목록
PDF_FILES = [
    BASE_DIR / "data" / "pdf" / "2-2. 2020 한국인 영양소 섭취기준 - 비타민.pdf",
    BASE_DIR / "data" / "pdf" / "2-3. 2020 한국인 영양소 섭취기준 - 무기질.pdf",
]

# FAISS 벡터 인덱스를 저장할 경로
FAISS_INDEX_PATH = str(BASE_DIR / "faiss_index_rda")

# 임베딩 모델 설정 (요청하신 E5 계열 멀티링궐 모델)
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"


def build_rag_index():
    """
    PDF 파일들을 읽어 FAISS 벡터 인덱스를 생성하고 저장합니다.
    """
    print("🚀 RAG 인덱스 생성을 시작합니다...")
    all_pages = []
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            print(f"⚠️ 경고: '{pdf_path}' 파일을 찾을 수 없습니다. 건너뜁니다.")
            continue
        print(f"📄 '{pdf_path.name}' 파일 로딩 중...")
        # PyPDFLoader는 페이지별로 문서를 나누고, 파일명과 페이지 번호 메타데이터를 자동으로 추가합니다.
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load_and_split()
        all_pages.extend(pages)

    if not all_pages:
        print("🚨 처리할 PDF 파일이 없어 인덱스 생성을 중단합니다.")
        return

    print(f"\n📚 총 {len(all_pages)} 페이지를 로드했습니다. 이제 텍스트를 청킹합니다...")
    # 텍스트를 의미 있는 단위로 분할 (청킹)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    docs = text_splitter.split_documents(all_pages)
    print(f"✂️ 총 {len(docs)}개의 문서 조각(청크)으로 분할되었습니다.")

    print(f"\n🧠 '{EMBEDDING_MODEL_NAME}' 모델을 사용하여 임베딩을 생성합니다...")
    # HuggingFace의 E5 모델로 임베딩 생성
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("💾 FAISS 벡터 인덱스를 생성하고 저장합니다...")
    # FAISS 벡터 DB 생성 및 저장
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)

    print(f"✅ RAG 인덱스 생성이 완료되었습니다. 저장 경로: '{FAISS_INDEX_PATH}'")


def search_rag(query: str, k: int = 5):
    """
    저장된 FAISS 인덱스를 로드하여 질문에 대한 유사도 높은 문서를 검색합니다.
    """
    if not Path(FAISS_INDEX_PATH).exists():
        print("🚨 FAISS 인덱스 파일이 없습니다. 먼저 `build_rag_index()`를 실행해주세요.")
        return None, None

    print(f"\n🔍 질문: '{query}'")
    print("... FAISS 인덱스 로딩 및 검색 중 ...")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

    # 유사도 기반 검색 (MMR을 사용하여 결과의 다양성 확보)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': k})
    retrieved_docs = retriever.invoke(query)

    print(f"\n✅ 총 {len(retrieved_docs)}개의 관련 문서를 찾았습니다.")
    
    # --- 7. 답변 생성용 컨텍스트 패킹 (인용표기 포함) ---
    context_for_llm = ""
    for i, doc in enumerate(retrieved_docs):
        source_file = Path(doc.metadata['source']).name
        page_num = doc.metadata['page'] + 1  # 페이지 번호는 0부터 시작하므로 +1
        context_for_llm += f"[출처 {i+1}: {source_file}, {page_num}페이지]\n"
        context_for_llm += f"{doc.page_content}\n\n"
    
    return retrieved_docs, context_for_llm


def answer_with_rag(query: str, context: str):
    """
    검색된 컨텍스트를 기반으로 LLM을 통해 최종 답변을 생성합니다.
    """
    print("\n💬 LLM을 통해 최종 답변을 생성합니다...")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "당신은 제공된 '출처'의 내용을 기반으로만 질문에 답변하는 영양 정보 전문가입니다. 답변은 반드시 한국어로 작성하고, 각 내용의 근거가 된 '출처' 번호를 문장 끝에 [출처 1], [출처 2]와 같이 명시해야 합니다. 제공된 내용에 답이 없으면 '제공된 정보만으로는 답변할 수 없습니다.'라고 말하세요."),
        ("human", "아래 내용을 참고하여 질문에 답변해 주세요.\n\n[참고 내용]\n{context}\n\n[질문]\n{question}")
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    chain = (
        {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # chain.invoke를 호출할 때 question과 context를 함께 전달
    answer = chain.invoke({"question": query, "context": context})
    return answer


if __name__ == "__main__":
    # --- 1단계: RAG 인덱스 생성 (최초 한 번만 실행하면 됩니다) ---
    # build_rag_index()

    # --- 2단계: 생성된 인덱스를 사용하여 질문 및 답변 ---
    # 예시 질문
    my_question = "30대 남성의 마그네슘 권장 섭취량과 상한 섭취량은 얼마인가요?"
    
    # RAG 검색
    docs, context = search_rag(my_question)
    
    if context:
        # 검색된 문서의 출처와 내용 확인
        print("\n--- [검색된 컨텍스트] ---\n")
        print(context)
        
        # LLM을 통한 답변 생성
        final_answer = answer_with_rag(my_question, context)
        
        print("\n--- [최종 답변] ---\n")
        print(final_answer)

