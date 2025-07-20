import os
import json
from dotenv import load_dotenv

# --- All Azure Imports ---
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# --- Load Environment Variables ---
load_dotenv()

# --- Global Paths ---
DATA_PATH = "documents/"
DB_CHROMA_PATH = "chroma_db"

def load_and_split_documents():
    """Loads and splits documents, only if the vector database doesn't exist."""
    if os.path.exists(DB_CHROMA_PATH):
        print("✅ Vector store already exists. Skipping document loading and splitting.")
        return None
    print("⏳ Loading documents...")
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith('.pdf'):
            pdf_path = os.path.join(DATA_PATH, file)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
    print(f"✅ Loaded {len(documents)} pages from PDFs.")
    
    print("⏳ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks.")
    return chunks

def create_and_store_embeddings(chunks):
    """Creates and stores embeddings using Azure, only if chunks are provided."""
    if chunks is None: return
    print("⏳ Creating embeddings with Azure OpenAI and storing in Chroma DB...")
    azure_embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-small",
        openai_api_version="2024-02-01",
        api_key=os.getenv("EMBEDDING_AZURE_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_AZURE_ENDPOINT")
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=azure_embeddings,
        persist_directory=DB_CHROMA_PATH
    )
    print("✅ Saved chunks to Chroma DB.")

def main(query: str):
    """
    Main RAG pipeline function. Initializes services, retrieves context,
    invokes the LLM, and returns a structured response.
    """
    # Load or create the vector database
    load_and_split_documents()

    print("\n--- 🚀 Initializing All-Azure RAG Chain ---")
    
    # 1. Initialize Retriever
    azure_embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-small",
        openai_api_version="2024-02-01",
        api_key=os.getenv("EMBEDDING_AZURE_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_AZURE_ENDPOINT")
    )
    vectorstore = Chroma(persist_directory=DB_CHROMA_PATH, embedding_function=azure_embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={'k': 5})

    # 2. Define Prompt
    prompt_template = """
    You are an expert insurance policy analyst. Based *only* on the CONTEXT provided, answer the user's QUESTION.
    Generate a JSON object with the following schema:
    {{"decision": "A clear 'yes', 'no', or 'partially' based on the context.","amount": "The coverage amount if specified, otherwise 'Not Specified'.","justification": "A concise explanation for your decision, quoting directly from the context.","source_clause": "The specific clause or section number from the context that supports your decision."}}
    CONTEXT:{context}
    QUESTION:{question}
    ANSWER (in JSON format):
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # 3. Initialize LLM
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        openai_api_version="2024-02-01",
        temperature=0,
        api_key=os.getenv("GENERATION_AZURE_API_KEY"),
        azure_endpoint=os.getenv("GENERATION_AZURE_ENDPOINT")
    )
    
    # Function to format retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 4. Build RAG Chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )

    # 5. Invoke Chain and Parse Output
    print(f"\nQuery: '{query}'")
    print("\n--- 🤖 Getting structured answer from Azure LLM ---")
    response_from_llm = rag_chain.invoke(query)
    response_content = response_from_llm.content

    try:
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        json_string = response_content[json_start:json_end]
        parsed_json = json.loads(json_string)
        
        # Add the source documents for the UI to display
        retrieved_docs = retriever.invoke(query)
        parsed_json["source_documents"] = retrieved_docs
        
        return parsed_json
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to decode JSON from the LLM response.", "raw_response": response_content}
    
    
    
    