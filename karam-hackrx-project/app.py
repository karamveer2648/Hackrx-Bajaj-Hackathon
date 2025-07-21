import os
import json
import tempfile
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

def get_policy_analysis(uploaded_file, user_input: str):
    """
    Processes an uploaded document and a user query to return a structured answer.
    """
    # --- Initialize LLM and Embeddings Clients ---
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o-mini",
        openai_api_version="2024-02-01",
        temperature=0,
        api_key=os.getenv("GENERATION_AZURE_API_KEY"),
        azure_endpoint=os.getenv("GENERATION_AZURE_ENDPOINT")
    )
    azure_embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-small",
        openai_api_version="2024-02-01",
        api_key=os.getenv("EMBEDDING_AZURE_API_KEY"),
        azure_endpoint=os.getenv("EMBEDDING_AZURE_ENDPOINT")
    )

    # --- Step 1: Formulate a clear question from the user's input ---
    formulation_prompt = PromptTemplate.from_template(
        "Convert the user's statement of facts into a clear, answerable question about insurance coverage.\n\n"
        "User Statement: \"{user_input}\"\n"
        "Question:"
    )
    question_formulation_chain = formulation_prompt | llm
    formulated_question = question_formulation_chain.invoke({"user_input": user_input}).content

    # --- Step 2: Load Document and Perform RAG ---
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        os.remove(tmp_file_path)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(documents=chunks, embedding=azure_embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={'k': 5})

        rag_prompt_template = """
        You are an insurance policy analyst. Based ONLY on the CONTEXT provided, answer the user's QUESTION.
        Generate a JSON object with this exact schema: {{"decision": "yes/no/partially", "amount": "coverage amount or 'Not Specified'", "justification": "explanation quoting the context", "source_clause": "the clause number"}}
        CONTEXT:{context}
        QUESTION:{question}
        ANSWER (in JSON format):
        """
        rag_prompt = PromptTemplate.from_template(rag_prompt_template)
        rag_chain = ({
            "context": retriever, 
            "question": lambda x: formulated_question
        } | rag_prompt | llm)

        response_from_llm = rag_chain.invoke(user_input) # Pass original input
        
        # --- Step 3: Parse and Finalize Response ---
        json_start = response_from_llm.content.find('{')
        json_end = response_from_llm.content.rfind('}') + 1
        json_string = response_from_llm.content[json_start:json_end]
        structured_response = json.loads(json_string)

        summary_prompt = PromptTemplate.from_template(
            "Based on the analysis that the decision is '{decision}', provide a simple, one-sentence conversational answer."
        )
        summary_chain = summary_prompt | llm
        conversational_summary = summary_chain.invoke(structured_response).content
        
        final_response = structured_response
        final_response["conversational_summary"] = conversational_summary
        final_response["source_documents"] = retriever.invoke(formulated_question)
        
        return final_response

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}