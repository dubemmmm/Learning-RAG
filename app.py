import tempfile
import streamlit as st
from embedchain import App


# Page config
st.set_page_config(page_title="Chat with YouTube Video", page_icon="📺")

# Initialize session states
if 'app' not in st.session_state:
    st.session_state.app = None
if 'db_path' not in st.session_state:
    st.session_state.db_path = tempfile.mkdtemp()
if 'video_added' not in st.session_state:
    st.session_state.video_added = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def embedchain_bot(db_path, api_key):
    try:
        return App.from_config(
            config={
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-3.5-turbo",  # Changed to gpt-3.5-turbo for better compatibility
                        "temperature": 0.5,
                        "api_key": api_key
                    }
                },
                "vectordb": {
                    "provider": "chroma",
                    "config": {
                        "dir": db_path
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "api_key": api_key
                    }
                }
            }
        )
    except Exception as e:
        st.error(f"Error initializing bot: {str(e)}")
        return None

# Create Streamlit app
st.title("Chat with YouTube Video 📺")
st.caption("This app allows you to chat with a YouTube video using OpenAI API")

# Get OpenAI API key from user
openai_access_token = st.text_input("OpenAI API Key", type="password")

# If OpenAI API key is provided, create an instance of App
if openai_access_token:
    # Only create app instance if it doesn't exist
    if st.session_state.app is None:
        with st.spinner("Initializing bot..."):
            st.session_state.app = embedchain_bot(st.session_state.db_path, openai_access_token)
        
    if st.session_state.app is not None:
        # Get the YouTube video URL from the user
        video_url = st.text_input("Enter YouTube Video URL", type="default")
        
        # Add the video to the knowledge base
        if video_url and not st.session_state.video_added:
            try:
                with st.spinner("Processing video..."):
                    st.session_state.app.add(video_url, data_type="youtube_video")
                st.success(f"Added {video_url} to knowledge base!")
                st.session_state.video_added = True
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
        
        # Only show chat interface if video has been added
        if st.session_state.video_added:
            # Ask a question about the video
            prompt = st.text_input("Ask any question about the YouTube Video")
            
            # Chat with the video
            if prompt:
                try:
                    with st.spinner("Thinking..."):
                        answer = st.session_state.app.chat(prompt)
                        # Add to chat history
                        st.session_state.chat_history.append({"question": prompt, "answer": answer})
                        
                        # Display answer
                        st.write("Answer:", answer)
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")
            
            # Display chat history
            if st.session_state.chat_history:
                st.markdown("### Chat History")
                for chat in st.session_state.chat_history:
                    with st.expander(f"Q: {chat['question'][:50]}..."):
                        st.markdown(f"**Question:** {chat['question']}")
                        st.markdown(f"**Answer:** {chat['answer']}")

# Add reset button
if st.button("Reset App"):
    st.session_state.app = None
    st.session_state.video_added = False
    st.session_state.chat_history = []
    st.experimental_rerun()
