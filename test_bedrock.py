import logging
from bedrock_utils import init_bedrock, get_claude_response
from knowledge_base import init_knowledge_base, get_knowledge_base_response, verify_kb_setup
from chat_service import get_combined_response
from dotenv import load_dotenv
import os
import requests

def test_claude():
    """Test Claude's basic functionality"""
    print("\nTesting Claude Integration:")
    print("=" * 50)
    
    try:
        runtime_client = init_bedrock()
        test_prompt = "Say 'test' if you can hear me"
        
        response = get_claude_response(runtime_client, test_prompt)
        if not response or not response.get('content'):
            print("❌ Claude returned empty response")
            return False
            
        print(f"Claude Test Response: {response['content']}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Claude test failed: {str(e)}")
        return False

def test_knowledge_base():
    """Test the knowledge base retrieval functionality"""
    print("\nTesting Knowledge Base Retrieval:")
    print("=" * 50)
    
    try:
        # First verify KB setup
        kb_id = os.getenv('BEDROCK_KB_ID')
        print(f"Testing Knowledge Base ID: {kb_id}")
        
        kb_client = init_knowledge_base()
        
        # Test queries
        test_queries = [
            "What is the company history?",
            "What are your product specifications?",
            "What materials do you use in your products?"
        ]
        
        all_passed = True
        for query in test_queries:
            print(f"\nTesting query: {query}")
            kb_response = get_knowledge_base_response(kb_client, query)
            
            # Check if response is empty
            if not kb_response:
                print("❌ Knowledge Base returned empty response")
                all_passed = False
                continue
                
            print(f"Knowledge Base Response: {kb_response}")
            print("-" * 50)
        
        return all_passed
    except Exception as e:
        print(f"❌ Knowledge Base test failed: {str(e)}")
        return False

def test_combined_service():
    """Test the combined chat service"""
    print("\nTesting Combined Chat Service:")
    print("=" * 50)
    
    try:
        runtime_client = init_bedrock()
        kb_client = init_knowledge_base()
        
        # Test cases organized by category
        test_prompts = {
            "Company Information": [
                "What is the company history?",
                "How long have you been in business?"
            ],
            "Product Information": [
                "What kind of balls do you sell?",
                "Can you tell me about your product specifications?",
                "What materials do you use for your balls?"
            ],
            "Customer Service": [
                "Can you help me with my order?",
                "I'd like to speak to someone about a custom order",
                "What's your quality control process?"
            ]
        }
        
        all_passed = True
        for category, prompts in test_prompts.items():
            print(f"\nTesting {category}:")
            print("-" * 30)
            
            for prompt in prompts:
                print(f"\nTest prompt: {prompt}")
                response = get_combined_response(runtime_client, kb_client, prompt)
                if not response or not response.get('content'):
                    print("❌ Empty response received")
                    all_passed = False
                    continue
                    
                print(f"Combined Response: {response['content']}")
                print("-" * 50)
        
        return all_passed
    except Exception as e:
        print(f"❌ Combined service test failed: {str(e)}")
        return False

def test_bland_integration():
    """Test Bland AI phone system integration"""
    print("\nTesting Bland AI Integration:")
    print("=" * 50)
    
    try:
        # Test Bland API key exists
        bland_api_key = os.getenv('BLAND_API_KEY')
        if not bland_api_key:
            print("❌ Missing BLAND_API_KEY environment variable")
            return False
            
        # Test API connection with a real call request
        bland_url = "https://api.bland.ai/v1/calls"
        headers = {
            "Authorization": f"Bearer {bland_api_key}",
            "Content-Type": "application/json"
        }
        
        # Real call data
        test_data = {
            "phone_number": "+17122230473",
            "task": "You are Sara from Rivertown Ball Company. Be friendly and professional while helping customers with wooden craft balls.",
            "voice": "alexa",
            "model": "turbo",
            "first_sentence": "Hello, is this Jake?",
            "wait_for_greeting": True,
            "after_greeting": "Hey Jake, this is Sara from the Rivertown Ball Company. You were just online chatting and requested a quick call. How can I help you today?",
            "temperature": 0.8,
            "max_duration": 8
        }
        
        print("Initiating test call...")
        response = requests.post(bland_url, json=test_data, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Bland API test failed: {response.text}")
            return False
            
        print("✅ Bland API call initiated successfully")
        print(f"Response: {response.json()}")
        
        # Test phone request format from Claude
        runtime_client = init_bedrock()
        test_prompt = "I'd like to speak with someone about placing an order"
        
        response = get_claude_response(runtime_client, test_prompt)
        content = response.get('content', '')
        
        # Try to extract JSON from the response text
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                content = json.loads(json_match.group())
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON from Claude response")
                print(f"Raw content: {content}")
                return False
        
        # Updated to match the expected format from bedrock_utils.py
        expected_format = {
            "type": "phone_request",
            "message": "I'll help connect you with our team! First, could you tell me your first name?",
            "stage": "name"
        }
        
        if not isinstance(content, dict) or content.get('type') != 'phone_request' or 'stage' not in content:
            print("❌ Claude not returning correct phone request format")
            print(f"Expected format: {expected_format}")
            print(f"Received format: {content}")
            return False
            
        print("✅ Claude phone request format correct")
        print(f"Response format: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bland integration test failed: {str(e)}")
        return False

def verify_environment():
    """Verify environment variables"""
    required_vars = {
        'AWS_ACCESS_KEY_ID': 'AWS Access Key',
        'AWS_SECRET_ACCESS_KEY': 'AWS Secret Key',
        'AWS_REGION': 'AWS Region',
        'BEDROCK_KB_ID': 'Bedrock Knowledge Base ID',
        'BLAND_API_KEY': 'Bland AI API Key',
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{description} ({var})")
    
    if missing_vars:
        print("\n�� Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    return True

def test_dynamodb_connection():
    """Test DynamoDB connection and table access"""
    print("\nTesting DynamoDB Connection and Table Access:")
    print("=" * 50)
    
    try:
        from dynamo_utils import init_dynamodb
        import boto3
        
        dynamodb = init_dynamodb()
        table_name = 'Rivertownball-cus'
        table = dynamodb.Table(table_name)
        
        print(f"✅ Successfully connected to {table_name}")
        return True
            
    except Exception as e:
        print(f"❌ DynamoDB connection test failed: {str(e)}")
        logger.error(f"Error details: {str(e)}", exc_info=True)
        return False

def test_order_lookup(last_name: str = None):
    """Test DynamoDB order lookup functionality"""
    print("\nTesting Order Lookup:")
    print("=" * 50)
    
    try:
        from dynamo_utils import init_dynamodb
        import boto3
        
        # Initialize DynamoDB client
        dynamodb = init_dynamodb()
        table_name = 'Rivertownball-cus'
        table = dynamodb.Table(table_name)
        
        if last_name:
            # Search by last name only
            print(f"\nSearching for orders with last name: {last_name}")
            response = table.scan(
                FilterExpression='#ln = :ln',
                ExpressionAttributeNames={
                    '#ln': 'last_name'
                },
                ExpressionAttributeValues={
                    ':ln': last_name.title()  # Convert to title case for consistency
                }
            )
        else:
            # Default test case for Jake Rains
            print("\nNo last name provided, using default test case (Jake Rains)")
            response = table.scan(
                FilterExpression='#fn = :fn and #ln = :ln',
                ExpressionAttributeNames={
                    '#fn': 'first_name',
                    '#ln': 'last_name'
                },
                ExpressionAttributeValues={
                    ':fn': 'Jake',
                    ':ln': 'Rains'
                }
            )
        
        if 'Items' in response and len(response['Items']) > 0:
            print(f"\n✅ Found {len(response['Items'])} matching customer(s)")
            
            for customer in response['Items']:
                print(f"\nCustomer: {customer.get('first_name')} {customer.get('last_name')}")
                print("-" * 40)
                
                if 'orders' in customer and customer['orders']:
                    print(f"Number of Orders: {len(customer['orders'])}")
                    print("\nOrder Details:")
                    
                    for order in customer['orders']:
                        print("\n" + "-" * 20)
                        print(f"Order ID: {order.get('order_id')}")
                        print(f"Product: {order.get('product')}")
                        print(f"Quantity: {order.get('quantity')}")
                        print(f"Date: {order.get('order_date')}")
                        print(f"Total: ${float(order.get('total_price', 0)):.2f}")
                else:
                    print("No orders found for this customer")
            return True
        else:
            print(f"❌ No customers found with last name: {last_name}")
            return False
            
    except Exception as e:
        print(f"❌ Order lookup test failed: {str(e)}")
        logger.error(f"Error details: {str(e)}", exc_info=True)
        return False

def run_specific_test(test_name: str = None, last_name: str = None):
    """Run a specific test by name"""
    if not verify_environment():
        return False
        
    tests = {
        "claude": test_claude,
        "kb": test_knowledge_base,
        "combined": test_combined_service,
        "bland": test_bland_integration,
        "orders": lambda: test_order_lookup(last_name),
        "dynamodb": test_dynamodb_connection
    }
    
    if test_name and test_name in tests:
        print(f"\nRunning {test_name} test...")
        return tests[test_name]()
    else:
        print("\nRunning all tests...")
        results = {}
        for name, test_func in tests.items():
            results[name] = test_func()
        return results

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    load_dotenv()
    
    # Get test name and last name from command line arguments if provided
    import sys
    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    last_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run tests
    results = run_specific_test(test_name, last_name)
    
    # Print summary
    if isinstance(results, dict):
        print("\nTest Summary:")
        print("=" * 50)
        for name, passed in results.items():
            status = '✅ Passed' if passed else '❌ Failed'
            print(f"{name}: {status}")
    else:
        status = '✅ Passed' if results else '❌ Failed'
        print(f"\nTest Result: {status}") 