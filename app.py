# app.py
import streamlit as st
import os
from embedchain import App

# Page configuration
st.set_page_config(
    page_title="VideoRAG",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main-header {
            text-align: center;
            color: #1E88E5;
        }
        .api-input {
            margin-bottom: 2rem;
        }
        .stButton button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🎥 VideoRAG - YouTube Video Analysis</h1>", unsafe_allow_html=True)

# API Key Input Section
if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False

if not st.session_state.api_key_entered:
    st.markdown("### Enter Your OpenAI API Key")
    api_key = st.text_input("OpenAI API Key:", type="password", key="api_key_input")
    if st.button("Submit API Key"):
        if api_key.startswith('sk-') and len(api_key) > 50:
            st.session_state.api_key = api_key
            st.session_state.api_key_entered = True
            st.experimental_rerun()
        else:
            st.error("Please enter a valid OpenAI API key.")
    
    # Add helpful information
    st.markdown("""
    #### How to get your OpenAI API key:
    1. Go to [OpenAI API](https://platform.openai.com/api-keys)
    2. Sign in or create an account
    3. Create a new API key
    4. Copy and paste it here
    
    Note: Your API key is only stored temporarily during your session.
    """)
    st.stop()

# Initialize bot after API key is entered
if 'bot' not in st.session_state and st.session_state.api_key_entered:
    try:
        st.session_state.bot = App.from_config(
            config={
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.5,
                        "api_key": st.session_state.api_key
                    }
                },
                "vectordb": {
                    "provider": "chroma",
                    "config": {
                        "dir": "chromadb"
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "api_key": st.session_state.api_key
                    }
                }
            }
        )
    except Exception as e:
        st.error(f"Error initializing the bot: {str(e)}")
        st.session_state.api_key_entered = False
        st.stop()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Main Interface (only shown after API key is entered)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Add YouTube Video")
    youtube_url = st.text_input("Enter YouTube URL:", key="youtube_url")
    
    if youtube_url:
        if st.button("Process Video"):
            with st.spinner("Processing video..."):
                try:
                    st.session_state.bot.add(youtube_url, data_type="youtube_video")
                    st.success("Video processed successfully! You can now ask questions about it.")
                except Exception as e:
                    st.error(f"Error processing video: {str(e)}")

with col2:
    st.markdown("### How to Use")
    st.markdown("""
    1. Paste a YouTube URL
    2. Click 'Process Video'
    3. Ask questions about the video
    4. Get AI-powered answers!
    """)
    
    # Add option to reset API key
    if st.button("Reset API Key"):
        st.session_state.api_key_entered = False
        st.session_state.api_key = None
        st.experimental_rerun()

# Chat interface
st.markdown("### Ask Questions")
query = st.text_input("What would you like to know about the video?", key="query")

if query:
    if st.button("Get Answer"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.bot.query(query)
                st.session_state.chat_history.append({"question": query, "answer": response})
                
                # Display the latest answer
                st.markdown("### Answer")
                st.write(response)
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.markdown("### Chat History")
    for i, chat in enumerate(st.session_state.chat_history):
        with st.expander(f"Q: {chat['question'][:50]}..."):
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit, EmbedChain, and OpenAI",
    unsafe_allow_html=True
)
