# Rivertown Ball Company Customer Service Chatbot

This project implements a customer service chatbot for Rivertown Ball Company, specializing in high-end wooden craft balls.

The Rivertown Ball Company Customer Service Chatbot is an AI-powered application designed to assist customers with inquiries about the company's products, history, and services. It leverages Amazon Bedrock for natural language processing and integrates with a knowledge base to provide accurate and context-aware responses.

## Repository Structure

- `app.py`: Main Streamlit application file
- `bedrock_utils.py`: Utility functions for Amazon Bedrock integration
- `chat_service.py`: Core chat service functionality
- `convert_to_text.py`: Script to convert JSON knowledge base to plain text
- `dynamo_utils.py`: Utility functions for DynamoDB operations
- `knowledge_base.py`: Knowledge base integration functions
- `rivertown_knowledge_base_2.json`: JSON file containing the company's knowledge base
- `test_bedrock.py`: Test suite for Bedrock and other integrations

## Usage Instructions

### Installation

1. Ensure you have Python 3.8+ installed.
2. Clone the repository:
   ```
   git clone <repository_url>
   cd rivertown-ball-company-chatbot
   ```
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Set up the following environment variables:
   - `AWS_ACCESS_KEY_ID`: Your AWS Access Key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Access Key
   - `AWS_REGION`: AWS Region (default: us-east-1)
   - `BEDROCK_KB_ID`: Bedrock Knowledge Base ID
   - `BLAND_API_KEY`: Bland AI API Key

2. Ensure you have the necessary AWS permissions to access Bedrock, DynamoDB, and other required services.

### Running the Application

To start the Streamlit application:

```
streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

### Testing

To run the test suite:

```
python test_bedrock.py
```

This will test various components including Claude integration, knowledge base retrieval, combined chat service, Bland AI integration, and DynamoDB connections.

### Troubleshooting

1. **Empty responses from Claude or Knowledge Base**
   - Check your AWS credentials and permissions
   - Verify the Bedrock Knowledge Base ID is correct
   - Ensure the knowledge base is properly populated

2. **DynamoDB connection issues**
   - Verify AWS credentials and region settings
   - Check if the 'Rivertownball-cus' table exists and is accessible

3. **Bland AI integration failures**
   - Confirm the BLAND_API_KEY is set correctly
   - Check Bland AI service status and API documentation for any changes

For any persistent issues, enable debug logging by setting the `LOG_LEVEL` environment variable to `DEBUG` and check the application logs for more detailed error messages.

## Data Flow

The Rivertown Ball Company chatbot processes user requests through the following flow:

1. User input is received through the Streamlit interface in `app.py`.
2. The input is sent to the `get_combined_response` function in `chat_service.py`.
3. This function queries both the Bedrock Claude model and the Knowledge Base.
4. The Knowledge Base response is retrieved using `get_knowledge_base_response` in `knowledge_base.py`.
5. The Claude model processes the user input and Knowledge Base response using `get_claude_response` in `bedrock_utils.py`.
6. The combined response is returned to the Streamlit interface for display.
7. If a phone call is requested, the Bland AI integration is triggered to initiate a call.

```
[User Input] -> [Streamlit Interface] -> [Chat Service]
                                          |
                  [Claude Model] <--------|------> [Knowledge Base]
                        |                 |
                        v                 v
               [Combined Response] <- [Bland AI (if phone call)]
                        |
                        v
              [Streamlit Interface]
```

## Deployment

The application is designed to be deployed as a web service. For production deployment:

1. Set up a secure hosting environment (e.g., AWS EC2 or ECS)
2. Configure environment variables securely (use AWS Secrets Manager)
3. Set up a reverse proxy (e.g., Nginx) for HTTPS
4. Use a process manager (e.g., Gunicorn) to run the Streamlit application
5. Set up monitoring and logging (e.g., CloudWatch)

## Infrastructure

The project utilizes the following AWS resources:

- **Lambda Functions**:
  - `bedrock-runtime`: Handles Bedrock API calls for natural language processing
  - `knowledge-base-query`: Manages queries to the Bedrock Knowledge Base

- **DynamoDB Tables**:
  - `Rivertownball-cus`: Stores customer order information

- **Bedrock Resources**:
  - Knowledge Base: Stores and retrieves company and product information
  - Claude Model: Processes natural language and generates responses

- **API Gateway**:
  - Exposes Lambda functions as RESTful APIs for the frontend application

- **S3 Bucket**:
  - `rivertown-assets`: Stores static assets and potentially the knowledge base JSON file