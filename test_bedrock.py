import logging
from bedrock_utils import init_bedrock, get_claude_response
from knowledge_base import init_knowledge_base, get_knowledge_base_response, verify_kb_setup
from chat_service import get_combined_response
from dotenv import load_dotenv
import os

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

def verify_environment():
    """Verify environment variables"""
    required_vars = {
        'AWS_ACCESS_KEY_ID': 'AWS Access Key',
        'AWS_SECRET_ACCESS_KEY': 'AWS Secret Key',
        'AWS_REGION': 'AWS Region',
        'BEDROCK_KB_ID': 'Bedrock Knowledge Base ID',
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{description} ({var})")
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    return True

def run_specific_test(test_name: str = None):
    """Run a specific test by name"""
    # First verify environment
    if not verify_environment():
        return False
        
    tests = {
        "claude": test_claude,
        "kb": test_knowledge_base,
        "combined": test_combined_service
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
    
    # Get test name from command line argument if provided
    import sys
    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run tests
    results = run_specific_test(test_name)
    
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