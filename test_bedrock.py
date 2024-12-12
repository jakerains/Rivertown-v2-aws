import logging
from bedrock_utils import verify_bedrock_setup, init_bedrock, get_response_with_rag
from dotenv import load_dotenv

def test_chatbot_responses():
    _, runtime_client = init_bedrock()
    
    # Test cases
    test_prompts = [
        "Hi, what kind of balls do you sell?",
        "Can you help me with my order?",
        "I'd like to speak to someone about a custom order",
        "What materials do you use for your balls?"
    ]
    
    print("\nTesting chatbot responses:")
    print("=" * 50)
    
    for prompt in test_prompts:
        print(f"\nTest prompt: {prompt}")
        response = get_response_with_rag(runtime_client, prompt)
        print(f"Response: {response['content']}")
        print("-" * 50)

if __name__ == "__main__":
    # Set up logging to see detailed output
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    load_dotenv()
    
    # Run verification
    result = verify_bedrock_setup()
    
    if result:
        print("\n✅ Bedrock setup is working correctly!")
        # Test chatbot responses
        test_chatbot_responses()
    else:
        print("\n❌ Bedrock setup verification failed. Check the logs above for details.") 