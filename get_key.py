import streamlit as st

def get_api_key():
    """Retrieves OpenAI API key, ensuring security best practices."""

    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

        st.write("[Get an OpenAI API key](https://beta.openai.com/account/api-keys)", unsafe_allow_html=True)

        if st.button('Save API Key'):
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
            else:
                # Store the API key securely using environment variables or external storage
                # (not shown in this code example)
                st.session_state.api_key = openai_api_key
                st.write("API key saved successfully!")