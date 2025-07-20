# Streamlit Cloud Deployment Configuration Guide

## Environment Variables Required

Your application requires the following environment variables to be set in Streamlit Cloud:

### Required Azure OpenAI Credentials:
1. `EMBEDDING_AZURE_API_KEY` - Your Azure OpenAI API key for embeddings
2. `EMBEDDING_AZURE_ENDPOINT` - Your Azure OpenAI endpoint URL for embeddings
3. `GENERATION_AZURE_API_KEY` - Your Azure OpenAI API key for text generation
4. `GENERATION_AZURE_ENDPOINT` - Your Azure OpenAI endpoint URL for text generation

## How to Set Up Streamlit Cloud Secrets

1. **Go to your Streamlit Cloud app dashboard**
   - Visit: https://share.streamlit.io/
   - Navigate to your deployed app

2. **Access App Settings**
   - Click on your app
   - Click the "⚙️ Settings" button
   - Go to the "Secrets" tab

3. **Add the following secrets in TOML format:**

```toml
EMBEDDING_AZURE_API_KEY = "your_actual_api_key_here"
EMBEDDING_AZURE_ENDPOINT = "https://your-resource-name.openai.azure.com/"
GENERATION_AZURE_API_KEY = "your_actual_api_key_here"
GENERATION_AZURE_ENDPOINT = "https://your-resource-name.openai.azure.com/"
```

4. **Save the secrets and restart your app**

## Alternative: Use st.secrets in Code

You can also access secrets in your code using:
```python
import streamlit as st

# Access secrets
api_key = st.secrets["EMBEDDING_AZURE_API_KEY"]
endpoint = st.secrets["EMBEDDING_AZURE_ENDPOINT"]
```

## Important Notes:
- Keep your API keys secure and never commit them to your repository
- The `.env` file (if you create one locally) should be added to `.gitignore`
- Each Azure OpenAI resource has its own endpoint and API key
- You may use the same credentials for both embedding and generation if your resource supports both services
