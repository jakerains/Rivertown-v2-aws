import boto3
import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict

logger = logging.getLogger(__name__)

def init_bedrock():
    """Initialize Bedrock runtime client for Claude"""
    try:
        load_dotenv()
        
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        runtime_client = session.client(
            service_name='bedrock-runtime',
            region_name='us-east-1',
            endpoint_url='https://bedrock-runtime.us-east-1.amazonaws.com'
        )
        
        return runtime_client
        
    except Exception as e:
        logger.error(f"Error initializing Bedrock runtime: {str(e)}")
        raise e

def get_claude_response(runtime_client, prompt: str) -> Dict[str, str]:
    """Get response from Claude 3 Haiku"""
    try:
        # Format the system prompt
        system_prompt = """You are assisting customers at Rivertown Ball Company, specializing in high-end wooden craft balls.

Keep responses natural, concise, and friendly. Avoid formal phrases like "Thank you for your inquiry" or "As a knowledgeable assistant." Instead, respond as a helpful person would in a natural conversation.

If a customer asks to speak with someone, wants to make a phone call, or requests a call back, respond with a special JSON format:
{
    "type": "phone_request",
    "message": "I'll help connect you with our team! First, could you tell me your first name?",
    "stage": "name"
}

For all other responses, be direct and friendly while sharing information about our premium wooden craft balls."""

        # Combine system prompt with user prompt
        full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:"

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        })

        response = runtime_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body.encode('utf-8')
        )
        
        response_body = json.loads(response['body'].read())
        
        if 'content' in response_body:
            return {
                "type": "text",
                "content": response_body['content'][0]['text'] if isinstance(response_body['content'], list) else response_body['content']
            }
        else:
            logger.error(f"Unexpected response structure: {response_body.keys()}")
            return {
                "type": "text",
                "content": "Error: Unexpected response format"
            }

    except Exception as e:
        logger.error(f"Error getting Claude response: {str(e)}")
        return {
            "type": "text",
            "content": "I apologize, but I'm having trouble connecting. Please try again."
        }

def verify_bedrock_setup():
    """Verify that Bedrock is set up correctly"""
    try:
        logger.info("Verifying Bedrock setup...")
        logger.info(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:4]}...{os.getenv('AWS_ACCESS_KEY_ID')[-4:]}")
        logger.info(f"AWS_SECRET_ACCESS_KEY: {os.getenv('AWS_SECRET_ACCESS_KEY')[:4]}...{os.getenv('AWS_SECRET_ACCESS_KEY')[-4:]}")
        logger.info(f"AWS_REGION: {os.getenv('AWS_REGION')}")
        
        # Initialize Bedrock client
        runtime_client = init_bedrock()
        
        # Test basic response
        try:
            test_response = get_claude_response(runtime_client, "Say 'test' if you can hear me")
            logger.info(f"Test response: {test_response}")
            logger.info("✅ Bedrock setup verification completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Bedrock setup verification failed: {str(e)}")
            raise e
            
    except Exception as e:
        logger.error(f"❌ Error verifying Bedrock setup: {str(e)}")
        return False