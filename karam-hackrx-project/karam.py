import streamlit as st
from app import get_policy_analysis

# --- Page Configuration ---
st.set_page_config(
    page_title="Policy Query Assistant",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Policy Query Assistant")
st.write("Upload a policy document and ask a question in plain English to get an instant analysis.")

# --- Main UI ---
uploaded_file = st.file_uploader("1. Upload your policy document (PDF)", type="pdf")

if uploaded_file:
    user_input = st.text_input("2. Enter your query (e.g., '46M, knee surgery, Pune')", "46M, knee surgery, Pune")

    if st.button("Analyze Query"):
        if user_input:
            with st.spinner("Analyzing document..."):
                try:
                    response = get_policy_analysis(uploaded_file, user_input)
                    
                    if "error" not in response:
                        st.subheader("🎯 Analysis Result")

                        # Display the simple, conversational answer first
                        st.success(response.get('conversational_summary', 'Analysis complete.'))
                        st.divider()

                        # Display the key details in columns
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Decision", response.get('decision', 'N/A'))
                        with col2:
                            st.metric("Coverage Amount", response.get('amount', 'N/A'))

                        st.markdown("#### Justification")
                        st.info(response.get('justification', 'No justification provided.'))
                        
                        # Show the source evidence in an expander
                        with st.expander("View Source Evidence"):
                            st.markdown(f"**Source Clause:** {response.get('source_clause', 'N/A')}")
                            if "source_documents" in response and response["source_documents"]:
                                for i, doc in enumerate(response["source_documents"]):
                                    st.write(f"--- *Source Text {i+1}* ---")
                                    st.write(doc.page_content)
                    else:
                        st.error(f"❌ Error during analysis: {response['error']}")
                
                except Exception as e:
                    st.error(f"❌ A fatal error occurred: {e}")
        else:
            st.warning("Please enter a query.")
else:
    st.info("👆 Upload a PDF to get started.")