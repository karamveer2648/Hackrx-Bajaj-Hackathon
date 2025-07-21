# SQLite3 compatibility fix for ChromaDB on Streamlit Cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import json
import tempfile
import logging
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# --- Imports ---
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Encapsulates the Azure AI clients to avoid re-initialization."""
    def __init__(self):
        try:
            self.azure_embeddings = AzureOpenAIEmbeddings(
                azure_deployment="text-embedding-3-small",
                openai_api_version="2024-02-01",
                api_key=os.getenv("EMBEDDING_AZURE_API_KEY"),
                azure_endpoint=os.getenv("EMBEDDING_AZURE_ENDPOINT")
            )
            self.llm = AzureChatOpenAI(
                azure_deployment="gpt-4o-mini",
                openai_api_version="2024-02-01",
                temperature=0,
                api_key=os.getenv("GENERATION_AZURE_API_KEY"),
                azure_endpoint=os.getenv("GENERATION_AZURE_ENDPOINT")
            )
            logger.info("✅ Azure OpenAI services initialized successfully")
        except Exception as e:
            raise ValueError(f"❌ Failed to initialize Azure OpenAI services: {str(e)}")

def parse_and_validate_response(response_content: str) -> Dict[str, Any]:
    """Robustly parses JSON from a string."""
    try:
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        json_string = response_content[json_start:json_end]
        return json.loads(json_string)
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to decode JSON from the LLM response.", "raw_response": response_content}

def process_document_and_query(processor: DocumentProcessor, uploaded_file, user_input: str, **kwargs) -> Dict[str, Any]:
    """Main pipeline to handle user input, process docs, and generate both structured and conversational responses."""
    start_time = datetime.now()
    chunk_size = kwargs.get('chunk_size', 1000)
    max_chunks = kwargs.get('max_chunks', 5)
    
    logger.info("--- Starting intelligent query processing ---")
    
    try:
        # --- NEW: Step 1 - Formulate a clear question from the user's input ---
        formulation_prompt = PromptTemplate.from_template(
            "You are an expert assistant. Convert the user's statement of facts into a clear, answerable question about insurance coverage.\n\n"
            "Example 1:\nUser Statement: \"46M, knee surgery, Pune, 3-month policy\"\nQuestion: \"Is knee surgery covered by the policy?\"\n\n"
            "Example 2:\nUser Statement: \"Car accident, frontal damage, Mumbai\"\nQuestion: \"What is the coverage for accidental damage to a car in Mumbai?\"\n\n"
            "User Statement: \"{user_input}\"\nQuestion:"
        )
        question_formulation_chain = formulation_prompt | processor.llm
        logger.info(f"🧠 Formulating question from: '{user_input}'")
        formulated_question = question_formulation_chain.invoke({"user_input": user_input}).content
        logger.info(f"✅ Formulated Question: '{formulated_question}'")

        # --- Step 2: RAG Pipeline ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        os.remove(tmp_file_path)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(documents=chunks, embedding=processor.azure_embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={'k': max_chunks})

        rag_prompt = PromptTemplate.from_template(kwargs.get('prompt_template', 
            "You are an expert insurance policy analyst. Based *only* on the CONTEXT provided, answer the user's QUESTION. "
            "Generate a JSON object with the schema: {{\"decision\": \"yes/no/partially\", \"amount\": \"coverage amount or 'Not Specified'\", \"justification\": \"explanation quoting context\", \"source_clause\": \"clause number\"}}\n\n"
            "CONTEXT: {context}\nQUESTION: {question}\nANSWER (JSON):"
        ))

        rag_chain = ({"context": retriever, "question": RunnablePassthrough()} | rag_prompt | processor.llm)
        response_from_llm = rag_chain.invoke(formulated_question)
        structured_response = parse_and_validate_response(response_from_llm.content)

        if "error" in structured_response:
            return structured_response

        # --- NEW: Step 3 - Generate Conversational Summary ---
        summary_prompt = PromptTemplate.from_template(
            "Based on the following analysis, provide a simple, one-sentence conversational answer.\n"
            "Analysis Decision: {decision}\nJustification: {justification}\n"
            "Example: If the decision is 'yes' for knee surgery, respond with 'Yes, knee surgery is covered under the policy.'\n"
            "Conversational Answer:"
        )
        summary_chain = summary_prompt | processor.llm
        conversational_summary = summary_chain.invoke(structured_response).content

        # --- Step 4: Assemble Final Response ---
        processing_time = (datetime.now() - start_time).total_seconds()
        structured_response.update({
            "conversational_summary": conversational_summary,
            "formulated_question": formulated_question,
            "source_documents": retriever.invoke(formulated_question),
            "document_metadata": {'filename': uploaded_file.name, 'total_pages': len(docs)},
            "processing_statistics": {'processing_time_seconds': processing_time, 'chunks_processed': len(chunks)}
        })
        
        return structured_response

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {"error": f"Processing failed: {str(e)}"}

# Dummy functions for the other tabs, can be enhanced later
def process_multiple_queries(processor, uploaded_file, queries, **kwargs):
    return [process_document_and_query(processor, uploaded_file, q, **kwargs) for q in queries]

def get_document_summary(processor, uploaded_file, **kwargs):
    return process_document_and_query(processor, "Generate a detailed summary of this document.", **kwargs)