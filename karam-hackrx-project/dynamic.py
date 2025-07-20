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
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# --- Imports ---
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# --- Load Environment Variables ---
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Enhanced document processor with additional features"""
    
    def __init__(self):
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
        self.processing_history = []

def process_document_and_query(uploaded_file, query: str, **kwargs) -> Dict[str, Any]:
    """
    Enhanced document processing with additional features
    
    New features:
    - Confidence scoring
    - Multiple query processing
    - Document metadata extraction
    - Processing statistics
    - Error handling improvements
    - Caching support
    """
    
    processor = DocumentProcessor()
    start_time = datetime.now()
    
    # Extract optional parameters
    include_metadata = kwargs.get('include_metadata', True)
    confidence_threshold = kwargs.get('confidence_threshold', 0.7)
    max_chunks = kwargs.get('max_chunks', 10)
    chunk_size = kwargs.get('chunk_size', 1000)
    chunk_overlap = kwargs.get('chunk_overlap', 100)
    
    logger.info("--- Starting enhanced document processing ---")
    
    try:
        # 1. Enhanced document loading with metadata
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        logger.info(f"⏳ Loading document: {uploaded_file.name}")
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        
        # Extract document metadata
        doc_metadata = {
            "filename": uploaded_file.name,
            "file_size": len(uploaded_file.getvalue()),
            "total_pages": len(docs),
            "processing_timestamp": start_time.isoformat()
        }

        # 2. Enhanced text splitting with adaptive parameters
        logger.info(f"⏳ Splitting into chunks (size: {chunk_size}, overlap: {chunk_overlap})...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)
        
        # Limit chunks if specified
        if max_chunks and len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]
            logger.warning(f"Limited to {max_chunks} chunks")

        # 3. Enhanced vector store creation
        logger.info("⏳ Creating enhanced vector store...")
        vectorstore = Chroma.from_documents(
            documents=chunks, 
            embedding=processor.azure_embeddings,
            collection_metadata={"source": uploaded_file.name}
        )
        retriever = vectorstore.as_retriever(search_kwargs={'k': min(5, len(chunks))})
        
        os.remove(tmp_file_path)

        # 4. Enhanced prompt with confidence scoring
        enhanced_prompt_template = """
        You are an expert insurance policy analyst. Based *only* on the CONTEXT provided, answer the user's QUESTION.
        
        Generate a JSON object with the following enhanced schema:
        {{
            "decision": "A clear 'yes', 'no', or 'partially' based on the context.",
            "confidence_score": "A score from 0.0 to 1.0 indicating your confidence in the decision.",
            "amount": "The coverage amount if specified, otherwise 'Not Specified'.",
            "justification": "A detailed explanation for your decision, quoting directly from the context.",
            "source_clause": "The specific clause or section number from the context that supports your decision.",
            "risk_factors": "Any potential risks or limitations mentioned in the context.",
            "additional_requirements": "Any additional conditions or requirements for coverage.",
            "related_sections": "Other relevant sections that might apply to this query."
        }}
        
        CONTEXT: {context}
        QUESTION: {question}
        ANSWER (in JSON format):
        """
        
        prompt = PromptTemplate(
            template=enhanced_prompt_template, 
            input_variables=["context", "question"]
        )

        def format_docs_enhanced(docs):
            formatted = []
            for i, doc in enumerate(docs):
                content = f"[Chunk {i+1}] {doc.page_content}"
                if hasattr(doc, 'metadata') and doc.metadata:
                    content += f" (Page: {doc.metadata.get('page', 'Unknown')})"
                formatted.append(content)
            return "\n\n".join(formatted)

        # 5. Build enhanced RAG chain
        rag_chain = (
            {"context": retriever | format_docs_enhanced, "question": RunnablePassthrough()}
            | prompt
            | processor.llm
        )
        
        logger.info("--- 🤖 Getting enhanced structured answer ---")
        response_from_llm = rag_chain.invoke(query)
        response_content = response_from_llm.content

        # 6. Enhanced JSON parsing with validation
        parsed_json = parse_and_validate_response(response_content, confidence_threshold)
        
        # 7. Add enhanced metadata and statistics
        retrieved_docs = retriever.invoke(query)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        enhanced_response = {
            **parsed_json,
            "source_documents": retrieved_docs if include_metadata else [],
            "document_metadata": doc_metadata if include_metadata else {},
            "processing_statistics": {
                "processing_time_seconds": processing_time,
                "chunks_processed": len(chunks),
                "chunks_retrieved": len(retrieved_docs),
                "confidence_threshold": confidence_threshold
            },
            "query_metadata": {
                "original_query": query,
                "query_length": len(query),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Store in processing history
        processor.processing_history.append({
            "query": query,
            "result": enhanced_response,
            "timestamp": start_time
        })
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {
            "error": f"Processing failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "query": query
        }

def parse_and_validate_response(response_content: str, confidence_threshold: float) -> Dict[str, Any]:
    """Enhanced JSON parsing with validation"""
    try:
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        json_string = response_content[json_start:json_end]
        parsed_json = json.loads(json_string)
        
        # Validate confidence score
        confidence = parsed_json.get('confidence_score', '0.0')
        try:
            confidence_float = float(confidence)
            if confidence_float < confidence_threshold:
                parsed_json["warning"] = f"Low confidence score ({confidence_float:.2f}). Results may be unreliable."
        except (ValueError, TypeError):
            parsed_json["warning"] = "Unable to parse confidence score."
        
        # Add validation status
        parsed_json["validation_status"] = "success"
        return parsed_json
        
    except (json.JSONDecodeError, IndexError) as e:
        return {
            "error": "Failed to decode JSON from the LLM response.",
            "raw_response": response_content,
            "validation_status": "failed",
            "error_details": str(e)
        }

def process_multiple_queries(uploaded_file, queries: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Process multiple queries against the same document"""
    results = []
    for i, query in enumerate(queries):
        logger.info(f"Processing query {i+1}/{len(queries)}")
        result = process_document_and_query(uploaded_file, query, **kwargs)
        results.append(result)
    return results

def get_document_summary(uploaded_file) -> Dict[str, Any]:
    """Generate a summary of the uploaded document"""
    summary_query = "Provide a brief summary of this insurance policy document, including key coverage areas, limits, and important terms."
    return process_document_and_query(uploaded_file, summary_query, include_metadata=True)