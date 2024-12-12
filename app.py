import streamlit as st
from bedrock_utils import init_bedrock
from knowledge_base import init_knowledge_base
from chat_service import get_combined_response
import json
import logging
import os
from dotenv import load_dotenv
from streamlit.components.v1 import html as st_html  # Import Streamlit's HTML component
import re
import requests
from dynamo_utils import init_dynamodb, get_customer_orders
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize clients
runtime_client = init_bedrock()
kb_client = init_knowledge_base()
dynamodb_client = init_dynamodb()

# Configure logger
logger = logging.getLogger(__name__)

# Set page config with custom theme and hidden menu
st.set_page_config(
    page_title="Rivertown Ball Company",
    page_icon="🟤",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Hide Streamlit header menu and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide hamburger menu */
    .css-1rs6os {visibility: hidden;}
    
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
if "first_name" not in st.session_state:
    st.session_state.first_name = None
if "phone_request_stage" not in st.session_state:
    st.session_state.phone_request_stage = None

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
if prompt := st.chat_input("Ask about our products..."):
    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display assistant response with thinking indicator
    with st.chat_message("assistant", avatar="🟤"):
        response_placeholder = st.empty()
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("_Thinking..._")
        
        # If we're in the phone request flow
        if st.session_state.phone_request_stage == "name":
            st.session_state.first_name = prompt
            response = "Great! Now, could you please provide your phone number?"
            thinking_placeholder.empty()
            response_placeholder.markdown(response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            st.session_state.phone_request_stage = "phone"
            st.stop()
            
        elif st.session_state.phone_request_stage == "phone":
            st.session_state.phone_number = prompt
            # Now we can make the call
            bland_url = "https://api.bland.ai/v1/calls"
            headers = {
                "Authorization": f"Bearer {os.getenv('BLAND_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            call_data = {
                "phone_number": st.session_state.phone_number,
                "task": "You are Sara from Rivertown Ball Company. Be friendly and professional while helping customers with wooden craft balls.",
                "voice": "alexa",
                "model": "turbo",
                "first_sentence": f"Hello, is this {st.session_state.first_name}?",
                "wait_for_greeting": True,
                "after_greeting": f"Hey {st.session_state.first_name}, this is Sara from the Rivertown Ball Company. You were just online chatting and requested a quick call. How can I help you today?",
                "temperature": 0.8,
                "max_duration": 8
            }
            
            try:
                bland_response = requests.post(bland_url, json=call_data, headers=headers)
                response = "Great! I'm connecting you with Sara right now. You should receive a call shortly." if bland_response.status_code == 200 else "I apologize, but I'm having trouble connecting the call. Please try again."
            except Exception as e:
                logger.error(f"Error making Bland API call: {e}")
                response = "I apologize, but I'm having trouble connecting the call. Please try again."
            
            thinking_placeholder.empty()
            response_placeholder.markdown(response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            st.session_state.phone_request_stage = None
            st.stop()
        
        # Check for order lookup requests first
        if any(phrase in prompt.lower() for phrase in ['orders for', 'order for', 'show orders']):
            try:
                # Extract name using simple split
                name_parts = prompt.lower().replace('orders for', '').replace('order for', '').replace('show orders for', '').strip().split()
                if len(name_parts) >= 2:
                    first_name, last_name = name_parts[0], name_parts[1]
                    
                    # Query DynamoDB - using exact same code as test
                    table = dynamodb_client.Table('Rivertownball-cus')
                    response = table.scan(
                        FilterExpression='#fn = :fn and #ln = :ln',
                        ExpressionAttributeNames={
                            '#fn': 'first_name',
                            '#ln': 'last_name'
                        },
                        ExpressionAttributeValues={
                            ':fn': first_name.title(),
                            ':ln': last_name.title()
                        }
                    )
                    
                    if 'Items' in response and len(response['Items']) > 0:
                        customer = response['Items'][0]
                        formatted_response = [f"## 📦 Orders for {first_name.title()} {last_name.title()}"]
                        
                        if 'orders' in customer and customer['orders']:
                            for order in customer['orders']:
                                date_str = order.get('order_date', '')
                                try:
                                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                    formatted_date = date_obj.strftime('%B %d, %Y')
                                except:
                                    formatted_date = date_str

                                formatted_response.append(f"""
<div style="background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">

🔖 **Order ID**: `{order.get('order_id')}`

🎁 **Product**: {order.get('product')}

📊 **Quantity**: {order.get('quantity')}

📅 **Date**: {formatted_date}

💰 **Total**: ${float(order.get('total_price', 0)):.2f}
</div>""")
                        
                        response_text = "\n".join(formatted_response)
                        thinking_placeholder.empty()
                        response_placeholder.markdown(response_text, unsafe_allow_html=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text
                        })
                        st.stop()
                    else:
                        error_msg = f"I couldn't find any orders for {first_name.title()} {last_name.title()}. Please verify the spelling or try another name."
                        thinking_placeholder.empty()
                        response_placeholder.markdown(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        st.stop()
                        
            except Exception as e:
                logger.error(f"Error looking up orders: {str(e)}")
                error_msg = "I apologize, but I encountered an error while looking up the orders. Please try again."
                thinking_placeholder.empty()
                response_placeholder.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.stop()
        
        # If no order lookup matched, get normal response from Claude
        response = get_combined_response(runtime_client, kb_client, prompt)
        
        # Try to parse JSON from string response
        if isinstance(response['content'], str):
            try:
                json_match = re.search(r'\{[\s\S]*\}', response['content'])
                if json_match:
                    content = json.loads(json_match.group())
                    if content.get('type') == 'phone_request':
                        response['content'] = content
                        st.session_state.phone_request_stage = "name"
            except (json.JSONDecodeError, AttributeError):
                pass

        # Remove thinking message and display response
        thinking_placeholder.empty()
        
        # Display response
        if isinstance(response['content'], dict) and response['content'].get('type') == 'phone_request':
            message = response['content']['message']
            response_placeholder.markdown(message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": message
            })
        else:
            response_placeholder.markdown(response['content'])
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['content']
            })

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
# Make the Bland API call
bland_url = "https://api.bland.ai/v1/calls"
headers = {
    "Authorization": f"Bearer {os.getenv('BLAND_API_KEY')}",
    "Content-Type": "application/json"
}

call_data = {
    "phone_number": st.session_state.phone_number,
    "task": "You are Sara from Rivertown Ball Company. Be friendly and professional while helping customers with wooden craft balls.",
    "voice": "alexa",
    "model": "turbo",
    "first_sentence": f"Hello, is this {st.session_state.first_name}?",
    "wait_for_greeting": True,
    "after_greeting": f"Hey {st.session_state.first_name}, this is Sara from the Rivertown Ball Company. You were just online chatting and requested a quick call. How can I help you today?",
    "temperature": 0.8,
    "max_duration": 8
}
