import streamlit as st
from bedrock_utils import init_bedrock, get_response_with_rag, format_order_table
from dynamo_utils import init_dynamodb
import json
import logging
from streamlit.components.v1 import html as st_html  # Import Streamlit's HTML component

# Initialize Bedrock clients
bedrock_client, runtime_client = init_bedrock()
dynamodb = init_dynamodb()

# Configure logger
logger = logging.getLogger(__name__)

# Set page config with custom theme
st.set_page_config(
    page_title="Rivertown Ball Company",
    page_icon="🟤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Global background and theme */
    .stApp {
        background: #fef3c7;
        background-image: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%);
    }
    
    /* Override default dark theme */
    .main {
        background-color: transparent !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Chat input container styling */
    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin: 10px 0 !important;
    }
    
    /* Chat input field styling */
    .stChatInput {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    
    /* Header styling */
    h1 {
        color: #92400e !important;
        text-align: center;
        padding: 20px 0;
        font-family: 'Arial', sans-serif;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #f59e0b;
        color: white;
        border-radius: 10px;
    }
    .stButton > button:hover {
        background-color: #d97706;
    }
    
    /* Add new animation for fade effect */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .fade-in-text {
        animation: fadeIn 0.5s ease-in;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🟤 Rivertown Ball Company")
    st.markdown("""
        <p style='text-align: center; color: #92400e; margin-bottom: 30px;'>
        Crafting Premium Wooden Balls Since 1985
        </p>
    """, unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Welcome to Rivertown Ball Company! How can I help you today?"
    })
if "phone_number" not in st.session_state:
    st.session_state.phone_number = None
if "cs_mode" not in st.session_state:
    st.session_state.cs_mode = False

# Create a container for chat messages
chat_container = st.container()

# Display chat messages from history on app rerun
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🟤" if message["role"] == "assistant" else "👤"):
            if message["role"] == "assistant" and isinstance(message["content"], dict) and message["content"].get("type") == "html":
                st_html(message["content"]["content"], height=600, scrolling=True)
            else:
                st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about our wooden balls..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🟤"):
        try:
            # Get the response
            response = get_response_with_rag(runtime_client, prompt)
            
            # Handle the response based on its type
            if isinstance(response, dict):
                if response.get("type") == "html":
                    st_html(response["content"], height=600, scrolling=True)
                else:
                    st.markdown(response["content"])
            else:
                st.markdown(response)
            
            # Add to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            logger.error(f"Error in chat response: {str(e)}", exc_info=True)

# Sidebar with reset button and additional info
with st.sidebar:
    st.markdown("### Chat Controls")
    if st.button("Reset Chat", key="reset"):
        st.session_state.messages = []
        st.session_state.phone_number = None
        st.session_state.cs_mode = False
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("""
        ### About Us
        Rivertown Ball Company has been crafting premium wooden balls 
        for over a century. Our commitment to quality and craftsmanship 
        makes us the leading choice for wooden ball products.
    """)