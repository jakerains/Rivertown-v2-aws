import boto3
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def init_knowledge_base():
    """Initialize Bedrock Agent Runtime client for KB"""
    try:
        # Load environment variables explicitly
        load_dotenv('.env')
        load_dotenv('.env.local', override=True)
        
        # Get and verify KB ID
        kb_id = os.getenv('BEDROCK_KB_ID')
        logger.info(f"Initializing Knowledge Base with ID: {kb_id}")
        
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'
        )
        
        kb_client = session.client(
            service_name='bedrock-agent-runtime',
            region_name='us-east-1'
        )
        
        return kb_client
        
    except Exception as e:
        logger.error(f"Error initializing KB client: {str(e)}")
        raise e

def get_knowledge_base_response(kb_client, query: str) -> str:
    """Query the knowledge base"""
    try:
        if not kb_client:
            logger.error("Knowledge base client is not initialized")
            return ""
            
        # Get the model ARN from environment or use Claude
        model_arn = os.getenv('BEDROCK_MODEL_ARN', 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0')
            
        response = kb_client.retrieve_and_generate(
            input={
                "text": query
            },
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": os.getenv('BEDROCK_KB_ID'),
                    "modelArn": model_arn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 3
                        }
                    }
                }
            }
        )
        
        # Debug logging
        logger.debug(f"Raw KB response: {response}")
        
        # Extract the generated text from the response
        if 'output' in response and 'text' in response['output']:
            return response['output']['text']
        elif 'retrievalResults' in response:
            # Fallback to just concatenating retrieval results if no generated text
            passages = []
            for result in response['retrievalResults']:
                if 'content' in result:
                    passages.append(result['content'])
            return "\n\n".join(passages)
        
        return ""
        
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}")
        return ""

def verify_kb_setup() -> bool:
    """Verify knowledge base setup"""
    try:
        logger.info("Verifying Knowledge Base setup...")
        
        # Check required environment variables
        required_vars = ['BEDROCK_KB_ID', 'BEDROCK_MODEL_ARN']
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                logger.error(f"Missing required environment variable: {var}")
                return False
            logger.info(f"{var} is set")
        
        # Test KB connection
        kb_client = init_knowledge_base()
        test_response = get_knowledge_base_response(kb_client, "test query")
        
        if test_response:
            logger.info("✅ Knowledge Base setup verification completed successfully")
            return True
        else:
            logger.error("❌ Knowledge Base returned empty response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying Knowledge Base setup: {str(e)}")
        return False 