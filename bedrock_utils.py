import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_secret() -> Optional[Dict[str, str]]:
    """Get secrets from AWS Secrets Manager"""
    secret_name = "rivertownchat"
    region_name = "us-east-1"

    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret
        
        logger.error("No SecretString found in the response")
        return None

    except ClientError as e:
        logger.error(f"Error getting secret: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting secret: {str(e)}")
        return None

def init_bedrock():
    """Initialize Bedrock runtime client for Claude"""
    try:
        # Get secrets from AWS Secrets Manager
        secrets = get_secret()
        if not secrets:
            raise Exception("Failed to get secrets from AWS Secrets Manager")
        
        session = boto3.Session(
            aws_access_key_id=secrets.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=secrets.get('AWS_SECRET_ACCESS_KEY'),
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
        
        # Get secrets
        secrets = get_secret()
        if not secrets:
            raise Exception("Failed to get secrets from AWS Secrets Manager")
            
        # Log partial keys for verification
        logger.info(f"AWS_ACCESS_KEY_ID: {secrets.get('AWS_ACCESS_KEY_ID', '')[:4]}...{secrets.get('AWS_ACCESS_KEY_ID', '')[-4:]}")
        logger.info(f"AWS_SECRET_ACCESS_KEY: {secrets.get('AWS_SECRET_ACCESS_KEY', '')[:4]}...{secrets.get('AWS_SECRET_ACCESS_KEY', '')[-4:]}")
        logger.info(f"AWS_REGION: {secrets.get('AWS_REGION', 'us-east-1')}")
        
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