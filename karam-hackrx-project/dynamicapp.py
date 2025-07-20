# SQLite3 compatibility fix for ChromaDB on Streamlit Cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import os

# Check for required credentials before importing other modules
def check_credentials():
    required_vars = [
        "EMBEDDING_AZURE_API_KEY",
        "EMBEDDING_AZURE_ENDPOINT", 
        "GENERATION_AZURE_API_KEY",
        "GENERATION_AZURE_ENDPOINT"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    return missing_vars

# Check credentials first
missing_credentials = check_credentials()
if missing_credentials:
    st.error("🔑 **Missing Azure OpenAI Credentials**")
    st.markdown(f"""
    The following environment variables are required but not set:
    
    {chr(10).join([f'• `{var}`' for var in missing_credentials])}
    
    **To fix this on Streamlit Cloud:**
    1. Go to your [Streamlit Cloud dashboard](https://share.streamlit.io/)
    2. Click on your app → ⚙️ Settings → Secrets
    3. Add the following in TOML format:
    
    ```toml
    EMBEDDING_AZURE_API_KEY = "your_api_key_here"
    EMBEDDING_AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
    GENERATION_AZURE_API_KEY = "your_api_key_here" 
    GENERATION_AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
    ```
    
    4. Save and restart your app
    
    **Need help?** Check the `DEPLOYMENT_GUIDE.md` file in your repository.
    """)
    st.stop()

from dynamic import process_document_and_query, process_multiple_queries, get_document_summary

# --- Page Configuration ---
st.set_page_config(
    page_title="Enhanced Policy Query Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Enhanced Policy Query Assistant")
st.write("Upload your policy document (PDF), ask questions, and get AI-powered analysis with confidence scoring.")

# --- Sidebar for Advanced Settings ---
with st.sidebar:
    st.header("⚙️ Advanced Settings")
    
    # Processing parameters
    chunk_size = st.slider("Chunk Size", 500, 2000, 1000, 50)
    chunk_overlap = st.slider("Chunk Overlap", 50, 300, 100, 25)
    max_chunks = st.slider("Max Chunks", 5, 20, 10, 1)
    confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7, 0.1)
    
    # Display options
    include_metadata = st.checkbox("Include Processing Metadata", True)
    show_statistics = st.checkbox("Show Processing Statistics", True)

# --- Main UI ---
uploaded_file = st.file_uploader("1. Upload your policy document", type="pdf")

if uploaded_file is not None:
    # Document info
    st.success(f"✅ Document uploaded: {uploaded_file.name} ({len(uploaded_file.getvalue())} bytes)")
    
    # Tabs for different query modes
    tab1, tab2, tab3 = st.tabs(["🔍 Single Query", "📋 Multiple Queries", "📊 Document Summary"])
    
    # Tab 1: Single Query
    with tab1:
        user_query = st.text_input("Enter your question:", "Is accident coverage included?")
        
        if st.button("Get Answer", key="single_query"):
            if user_query:
                with st.spinner("Processing document and generating answer..."):
                    try:
                        response = process_document_and_query(
                            uploaded_file, 
                            user_query,
                            include_metadata=include_metadata,
                            confidence_threshold=confidence_threshold,
                            max_chunks=max_chunks,
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap
                        )
                        
                        if "error" not in response:
                            # Main result with enhanced display
                            st.subheader("🎯 Analysis Result:")
                            
                            # Display confidence score prominently
                            confidence = response.get('confidence_score', 'N/A')
                            if confidence != 'N/A':
                                try:
                                    conf_float = float(confidence)
                                    color = "green" if conf_float >= 0.8 else "orange" if conf_float >= 0.6 else "red"
                                    st.markdown(f"**Confidence Score:** :{color}[{conf_float:.1%}]")
                                except:
                                    st.markdown(f"**Confidence Score:** {confidence}")
                            
                            # Main response
                            main_response = {k: v for k, v in response.items() 
                                           if k not in ['source_documents', 'document_metadata', 
                                                      'processing_statistics', 'query_metadata']}
                            st.json(main_response)
                            
                            # Warning for low confidence
                            if "warning" in response:
                                st.warning(f"⚠️ {response['warning']}")
                            
                            # Processing statistics
                            if show_statistics and "processing_statistics" in response:
                                with st.expander("📈 Processing Statistics"):
                                    stats = response["processing_statistics"]
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Processing Time", f"{stats.get('processing_time_seconds', 0):.2f}s")
                                    with col2:
                                        st.metric("Chunks Processed", stats.get('chunks_processed', 0))
                                    with col3:
                                        st.metric("Chunks Retrieved", stats.get('chunks_retrieved', 0))
                            
                            # Source documents
                            if "source_documents" in response and response["source_documents"]:
                                with st.expander("📚 Source Evidence"):
                                    for i, doc in enumerate(response["source_documents"]):
                                        st.info(f"**Source {i+1}** (Page {doc.metadata.get('page', 'N/A')})")
                                        st.write(doc.page_content)
                            
                            # Document metadata
                            if include_metadata and "document_metadata" in response:
                                with st.expander("📄 Document Information"):
                                    st.json(response["document_metadata"])
                        
                        else:
                            st.error(f"❌ Error: {response['error']}")
                            if "raw_response" in response:
                                with st.expander("Raw Response"):
                                    st.code(response["raw_response"])
                    
                    except Exception as e:
                        st.error(f"❌ Fatal error: {e}")
            else:
                st.warning("Please enter a question.")
    
    # Tab 2: Multiple Queries
    with tab2:
        st.write("Process multiple questions at once:")
        
        # Pre-defined common queries
        common_queries = [
            "Is accident coverage included?",
            "What is the coverage amount?",
            "What are the exclusions?",
            "What is the deductible amount?",
            "Are pre-existing conditions covered?"
        ]
        
        selected_queries = st.multiselect("Select common queries:", common_queries)
        custom_queries = st.text_area("Add custom queries (one per line):")
        
        all_queries = selected_queries[:]
        if custom_queries:
            all_queries.extend([q.strip() for q in custom_queries.split('\n') if q.strip()])
        
        if st.button("Process All Queries", key="multiple_queries") and all_queries:
            with st.spinner(f"Processing {len(all_queries)} queries..."):
                try:
                    results = process_multiple_queries(
                        uploaded_file,
                        all_queries,
                        include_metadata=False,  # Reduce output size
                        confidence_threshold=confidence_threshold,
                        max_chunks=max_chunks,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    
                    st.subheader("🔍 Multiple Query Results:")
                    
                    for i, (query, result) in enumerate(zip(all_queries, results)):
                        with st.expander(f"Query {i+1}: {query}"):
                            if "error" not in result:
                                # Show key info
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Decision:** {result.get('decision', 'N/A')}")
                                    st.write(f"**Amount:** {result.get('amount', 'N/A')}")
                                with col2:
                                    confidence = result.get('confidence_score', 'N/A')
                                    st.write(f"**Confidence:** {confidence}")
                                
                                st.write(f"**Justification:** {result.get('justification', 'N/A')}")
                                
                                if "warning" in result:
                                    st.warning(result['warning'])
                            else:
                                st.error(f"Error: {result['error']}")
                
                except Exception as e:
                    st.error(f"Error processing multiple queries: {e}")
    
    # Tab 3: Document Summary
    with tab3:
        if st.button("Generate Document Summary", key="doc_summary"):
            with st.spinner("Generating document summary..."):
                try:
                    summary = get_document_summary(uploaded_file)
                    
                    if "error" not in summary:
                        st.subheader("📊 Document Summary")
                        
                        # Display summary in a structured way
                        summary_content = {k: v for k, v in summary.items() 
                                         if k not in ['source_documents', 'document_metadata', 
                                                    'processing_statistics', 'query_metadata']}
                        st.json(summary_content)
                        
                        # Document metadata
                        if "document_metadata" in summary:
                            with st.expander("📄 Document Details"):
                                metadata = summary["document_metadata"]
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Total Pages", metadata.get('total_pages', 'N/A'))
                                    st.metric("File Size", f"{metadata.get('file_size', 0)} bytes")
                                with col2:
                                    st.write(f"**Filename:** {metadata.get('filename', 'N/A')}")
                                    st.write(f"**Processed:** {metadata.get('processing_timestamp', 'N/A')}")
                    else:
                        st.error(f"Error generating summary: {summary['error']}")
                
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

else:
    st.info("👆 Please upload a PDF document to get started.")
    
    # Show feature overview
    st.markdown("### ✨ New Features:")
    st.markdown("""
    - **Confidence Scoring**: Get confidence levels for each answer
    - **Multiple Query Processing**: Ask several questions at once
    - **Document Summaries**: Generate comprehensive policy summaries
    - **Advanced Settings**: Customize processing parameters
    - **Enhanced Metadata**: Detailed processing statistics
    - **Improved Error Handling**: Better error messages and validation
    """)