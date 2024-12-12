import boto3
import os
from dotenv import load_dotenv
import json
import logging
from dynamo_utils import get_customer_orders, init_dynamodb
import re
import requests
from typing import Dict, Any, Tuple, Union
import streamlit as st

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def init_bedrock():
    """Initialize Bedrock client"""
    try:
        # Load AWS credentials from environment
        load_dotenv()
        
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        # Use the bedrock-runtime endpoint for inference
        runtime_client = session.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            endpoint_url='https://bedrock-runtime.us-east-1.amazonaws.com'
        )
        
        return None, runtime_client
        
    except Exception as e:
        logger.error(f"Error initializing Bedrock: {str(e)}")
        raise e

def extract_customer_name(prompt: str) -> tuple[str, str] | None:
    """Extract first and last name from prompt using regex"""
    patterns = [
        r"show\s+(?:me\s+)?(?:the\s+)?(?:orders?\s+(?:for|of)\s+)?([a-zA-Z]+)\s+([a-zA-Z]+)",
        r"(?:what\s+(?:are|were)\s+)?([a-zA-Z]+)\s+([a-zA-Z]+)(?:'s)?\s+orders?",
        r"find\s+(?:the\s+)?orders?\s+(?:for|of)\s+([a-zA-Z]+)\s+([a-zA-Z]+)",
        r"(?:get|fetch|pull|retrieve)\s+([a-zA-Z]+)\s+([a-zA-Z]+)(?:'s)?\s+orders?",
        r"([a-zA-Z]+)\s+([a-zA-Z]+)(?:'s)?\s+(?:order|purchase|transaction)s?",
        r"orders?\s+(?:for|by|from)\s+([a-zA-Z]+)\s+([a-zA-Z]+)",
        # Add a catch-all pattern for when names are mentioned near "order" keywords
        r".*?(?:order|purchase|history).*?([a-zA-Z]+)\s+([a-zA-Z]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            return match.group(1).title(), match.group(2).title()
    return None

def format_order_table(orders: list) -> str:
    """Format orders into a beautifully styled display"""
    if not orders:
        return "<div>No orders found.</div>"
        
    html = """
    <div style="
        font-family: sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    ">
        <h2 style="
            color: #1e3a8a;
            text-align: center;
            margin-bottom: 20px;
        ">📦 Order History</h2>
    """
    
    for order in orders:
        html += f"""
        <div style="
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="
                font-size: 1.2em;
                font-weight: bold;
                color: #1e3a8a;
                margin-bottom: 15px;
            ">
                Order #{order['order_id'][:8]}...
            </div>
            
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            ">
                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <div style="font-size: 0.9em; color: #666;">Product</div>
                    <div style="font-weight: 500; color: #333;">{order['product']}</div>
                </div>
                
                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <div style="font-size: 0.9em; color: #666;">Quantity</div>
                    <div style="font-weight: 500; color: #333;">{order['quantity']} units</div>
                </div>
                
                <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <div style="font-size: 0.9em; color: #666;">Order Date</div>
                    <div style="font-weight: 500; color: #333;">{order['order_date']}</div>
                </div>
            </div>
            
            <div style="
                text-align: right;
                font-size: 1.1em;
                color: #1e3a8a;
                font-weight: bold;
                padding-top: 10px;
                border-top: 1px solid #eee;
            ">
                Total Amount: ${order['total_price']:.2f}
            </div>
        </div>
        """
    
    html += "</div>"
    return html

def get_response_with_rag(runtime_client, prompt: str) -> Union[Dict[str, str], str]:
    try:
        # Debug: Print initial prompt
        logger.debug(f"Incoming prompt: {prompt}")

        system_prompt = """You are a helpful customer service AI assistant for Rivertown Ball Company, a manufacturer of artisanal wooden balls. Your name is River.

Key Information:
- You specialize in helping customers with questions about our wooden balls, orders, and general inquiries
- You can look up customer orders when given a name
- You can connect customers with a live representative named Sara if needed
- You maintain a friendly, professional, and helpful tone

Guidelines:
- If customers ask about orders, use the extract_customer_name function to find their orders
- If customers want to speak to a person, use the handle_customer_service_request function
- Always be truthful - if you don't know something, say so
- Focus on providing accurate information about our wooden ball products
- Keep responses concise but informative

Products:
- We specialize in handcrafted wooden balls made from sustainable materials
- Each ball is carefully inspected for quality
- Our balls come in various sizes and wood types

Customer Service:
- Phone support is available at (719) 266-2837
- Live chat with Sara can be arranged through the system
- We aim to respond to all inquiries within 24 hours"""

        # Combine system prompt and user prompt
        combined_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:"

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": combined_prompt
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        })

        try:
            response = runtime_client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                contentType="application/json",
                accept="application/json",
                body=body.encode('utf-8')
            )
            
            response_body = json.loads(response['body'].read())
            logger.debug(f"Raw response: {response_body}")
            
            # Handle Claude 3's response structure
            if 'content' in response_body:
                return {
                    "type": "text",
                    "content": response_body['content'][0]['text'] if isinstance(response_body['content'], list) else response_body['content']
                }
            else:
                logger.error(f"Unexpected response structure. Keys found: {response_body.keys()}")
                return {
                    "type": "text",
                    "content": "Error: Unexpected response format from language model"
                }

        except Exception as e:
            logger.error(f"Bedrock API error: {str(e)}")
            return {
                "type": "text",
                "content": "I apologize, but I'm having trouble connecting to my language model. Please try again in a moment."
            }

    except Exception as e:
        logger.error(f"Error getting response from Bedrock: {str(e)}")
        raise e

def verify_bedrock_setup():
    """Utility function to verify Bedrock configuration"""
    logger.info("Verifying Bedrock setup...")
    
    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            return False
        else:
            # Print first/last 4 chars of credentials for debugging
            if 'KEY' in var:
                value = os.getenv(var)
                logger.info(f"{var}: {value[:4]}...{value[-4:]}")
            else:
                logger.info(f"{var}: {os.getenv(var)}")

    try:
        # Test Bedrock client initialization
        _, runtime_client = init_bedrock()
        if runtime_client is None:
            logger.error("Failed to initialize Bedrock runtime client")
            return False
        
        # Test simple model invocation
        test_response = get_response_with_rag(runtime_client, "Say 'test' if you can hear me")
        logger.info(f"Test response: {test_response}")
        
        if test_response.get('type') == 'text' and 'error' not in test_response.get('content', '').lower():
            logger.info("✅ Bedrock setup verification completed successfully")
            return True
        else:
            logger.error("❌ Bedrock test invocation failed")
            return False

    except Exception as e:
        logger.error(f"❌ Bedrock setup verification failed: {str(e)}", exc_info=True)
        return False

def init_bland():
    """Initialize Bland API configuration"""
    load_dotenv('.env.local')
    return {
        'headers': {
            'Authorization': os.getenv('BLAND_API_KEY')
        },
        'base_url': 'https://us.api.bland.ai/v1'
    }

def extract_phone_number(prompt: str) -> str | None:
    """Extract phone number from prompt using regex"""
    # Clean the input string of any whitespace and common separators
    cleaned_number = ''.join(filter(str.isdigit, prompt))
    
    # If we have exactly 10 digits, assume it's a valid US phone number
    if len(cleaned_number) == 10:
        return f"+1{cleaned_number}"
    
    # If we have 11 digits and it starts with 1, also valid
    if len(cleaned_number) == 11 and cleaned_number.startswith('1'):
        return f"+{cleaned_number}"
    
    # For any other length, return None
    return None

def handle_customer_service_request(prompt: str, phone_number: str = None) -> str:
    """Handles customer service related requests and initiates calls if needed"""
    try:
        # Check if this is a customer service request or just a phone number
        is_cs_request = any(keyword in prompt.lower() for keyword in [
            'speak to someone', 'talk to a person', 'customer service',
            'representative', 'speak to a human', 'talk to someone',
            'call me', 'contact me'
        ])
        is_just_numbers = sum(c.isdigit() for c in prompt) >= 10
        
        # Initial CS request
        if is_cs_request:
            return ("I'd be happy to have Sara, our customer service specialist, give you a call! "
                   "What's the best phone number to reach you at? You can share it in any format "
                   "like: 123-456-7890 or (123) 456-7890")
        
        # Handle phone number input
        if is_just_numbers:
            formatted_phone = f"+1{''.join(filter(str.isdigit, prompt))[-10:]}"
            
            # Initiate the call
            data = {
                "phone_number": formatted_phone,
                "task": """You are Sara from Rivertown Ball Company following up on a chat conversation they were just having, looking to ask them if they have any questions you can help with. 
                Start the call with: "Hi, this is Sara from Rivertown Ball Company!"
                Be warm, friendly and helpful while assisting with their questions about our artisanal wooden balls.
                Make them feel valued and excited about our products!""",
                "model": "turbo",
                "voice": "Alexa",
                "max_duration": 12,
                "wait_for_greeting": True,
                "temperature": 0.8
            }
            
            bland_config = init_bland()
            response = requests.post(
                f"{bland_config['base_url']}/calls",
                json=data,
                headers=bland_config['headers']
            )
            
            if response.status_code == 200:
                return (f"Perfect! Sara will be calling you right now at " 
                       f"{formatted_phone[-10:-7]}-{formatted_phone[-7:-4]}-{formatted_phone[-4:]}. "
                       "She's looking forward to helping you with any questions you have about our "
                       "artisanal wooden balls!")
            else:
                logger.error(f"Failed to initiate customer service call: {response.text}")
                return ("I apologize, but I'm having trouble connecting with Sara at the moment. "
                       "Please try again in a few minutes or call us directly at (719) 266-2837")
        
        return None
        
    except Exception as e:
        logger.error(f"Error in customer service request handling: {str(e)}", exc_info=True)
        return ("I apologize, but I'm experiencing technical difficulties arranging the call. "
               "Please contact our customer service directly at (719) 266-2837")