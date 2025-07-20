import streamlit as st
from app import main  # Import the main logic from your app.py file

# --- Page Configuration ---
st.set_page_config(
    page_title="Policy Query Assistant",
    page_icon="📄",
    layout="wide"
)   

# --- Custom CSS for better styling ---
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<h1 class="main-header">📄 Policy Query Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Get instant answers about your policy documents using AI-powered analysis
        </p>
    </div>
""", unsafe_allow_html=True)

# --- Instructions ---
with st.expander("ℹ️ How to use this tool", expanded=False):
    st.markdown("""
    1. **Enter your question** in the text box below
    2. **Click 'Analyze'** to get AI-powered insights
    3. **Review the answer** and check source documents for verification
    
    **Example questions:**
    - Is accident coverage included in my policy?
    - What is the claim process?
    - What are the exclusions in my policy?
    - What is the premium amount?
    """)

# --- Query Input Section ---
st.markdown('<div class="query-box">', unsafe_allow_html=True)
st.subheader("🤔 What would you like to know?")

# Example questions for quick selection
col1, col2 = st.columns(2)
with col1:
    if st.button("💰 Premium Information"):
        st.session_state.query_text = "What is the premium amount and payment schedule?"
with col2:
    if st.button("🚗 Coverage Details"):
        st.session_state.query_text = "What types of coverage are included?"

col3, col4 = st.columns(2)
with col3:
    if st.button("📋 Claim Process"):
        st.session_state.query_text = "How do I file a claim?"
with col4:
    if st.button("❌ Exclusions"):
        st.session_state.query_text = "What are the policy exclusions?"

# Main query input
user_query = st.text_input(
    "Or type your own question:",
    value=st.session_state.get('query_text', ''),
    placeholder="e.g., Is accident coverage included in my policy?",
    help="Be specific with your question for better results"
)

# Update session state
if user_query:
    st.session_state.query_text = user_query

# Submit button
submit_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Results Section ---
if submit_button and user_query:
    with st.spinner("🤖 AI is analyzing your policy document..."):
        try:
            # Call the main function from app.py with the user's query
            response = main(query=user_query)
            
            if "error" not in response:
                # Success - Display results
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.success("✅ Analysis Complete!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Main answer
                st.subheader("📝 Answer:")
                result_data = {k: v for k, v in response.items() if k != 'source_documents'}
                
                # Display answer in a more readable format
                if 'answer' in result_data:
                    st.markdown(f"**{result_data['answer']}**")
                else:
                    st.json(result_data)
                
                # Confidence/Quality indicators
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Sources Found", len(response.get("source_documents", [])))
                with col2:
                    if "confidence" in response:
                        st.metric("Confidence", f"{response['confidence']}%")

                # Source documents
                if "source_documents" in response and response["source_documents"]:
                    with st.expander("📖 View Source Documents", expanded=False):
                        st.info("These are the document sections the AI used to answer your question:")
                        for i, doc in enumerate(response["source_documents"]):
                            with st.container():
                                st.markdown(f"**📄 Source {i+1}** (Page {doc.metadata.get('page', 'N/A')})")
                                st.text_area(
                                    f"Content {i+1}:", 
                                    doc.page_content, 
                                    height=100, 
                                    key=f"source_{i}",
                                    disabled=True
                                )
                                st.divider()
            else:
                # Error handling
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ Error: {response.get('error')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                with st.expander("🔧 Technical Details"):
                    st.code(response.get('raw_response', 'No additional details available.'))

        except Exception as e:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ A fatal error occurred: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.info("Please try again or contact support if the problem persists.")

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🔒 Your data is processed securely using Azure OpenAI | 
        📞 Need help? Contact our support team</p>
    </div>
""", unsafe_allow_html=True)