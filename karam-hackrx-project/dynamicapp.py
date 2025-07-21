# SQLite3 compatibility fix
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import os
from dotenv import load_dotenv

# Load credentials early
load_dotenv()

# --- Main App Logic ---
def main_app():
    # Check for credentials before importing the backend
    required_vars = ["EMBEDDING_AZURE_API_KEY", "EMBEDDING_AZURE_ENDPOINT", "GENERATION_AZURE_API_KEY", "GENERATION_AZURE_ENDPOINT"]
    if any(not os.getenv(var) for var in required_vars):
        st.error("🔑 Missing Azure OpenAI Credentials in your secrets. Please add them to continue.")
        st.stop()
    
    # Import backend now that credentials are confirmed
    from dynamic import DocumentProcessor, process_document_and_query, process_multiple_queries, get_document_summary
    
    st.set_page_config(page_title="Intelligent Document Analyst", page_icon="🤖", layout="wide")
    st.title("🤖 Intelligent Document Analyst")

    # Instantiate the processor once
    if 'processor' not in st.session_state:
        try:
            st.session_state.processor = DocumentProcessor()
        except ValueError as e:
            st.error(str(e))
            st.stop()
    
    processor = st.session_state.processor

    # Main UI
    uploaded_file = st.file_uploader("Upload your document (PDF)", type="pdf")

    if uploaded_file:
        st.success(f"✅ Document '{uploaded_file.name}' ready for analysis.")
        user_input = st.text_input("Enter your query or statement of facts (e.g., '46M, knee surgery, Pune'):", "46M, knee surgery, Pune, 3-month policy")

        if st.button("Analyze Query"):
            if user_input:
                with st.spinner("Analyzing..."):
                    response = process_document_and_query(processor, uploaded_file, user_input)

                    if "error" not in response:
                        # --- NEW: Display conversational summary first ---
                        st.subheader("💡 Quick Answer")
                        st.markdown(f"### {response.get('conversational_summary', 'Analysis complete.')}")
                        st.divider()

                        st.subheader("🎯 Detailed Analysis")
                        col1, col2 = st.columns(2)
                        col1.metric("Decision", response.get('decision', 'N/A'))
                        col2.metric("Coverage Amount", response.get('amount', 'N/A'))

                        with st.expander("Show Justification and Evidence"):
                            st.info(f"**Justification:** {response.get('justification', 'N/A')}")
                            st.success(f"**Source Clause:** {response.get('source_clause', 'N/A')}")
                            st.markdown(f"**AI's Internal Question:** *{response.get('formulated_question')}*")
                            st.markdown("**Source Text:**")
                            if response.get("source_documents"):
                                for doc in response["source_documents"]:
                                    st.write(f"> {doc.page_content}")
                    else:
                        st.error(f"❌ Error: {response['error']}")
            else:
                st.warning("Please enter a query.")
    else:
        st.info("👆 Upload a document to get started.")

if __name__ == "__main__":
    main_app()