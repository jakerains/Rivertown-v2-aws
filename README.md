# Rivertown Ball Company Customer Service Chatbot

This project implements a customer service chatbot for Rivertown Ball Company, specializing in high-end wooden craft balls.

The Rivertown Ball Company Customer Service Chatbot is an AI-powered application designed to assist customers with inquiries about the company's products, history, and services. It leverages AWS Bedrock for natural language processing and integrates with a knowledge base to provide accurate and context-aware responses. The chatbot also features a phone call request system using Bland AI for seamless customer support escalation.

## Repository Structure

- `app.py`: Main Streamlit application file containing the chatbot interface and logic
- `bedrock_utils.py`: Utility functions for AWS Bedrock integration
- `chat_service.py`: Core chat service combining Bedrock and knowledge base responses
- `convert_to_text.py`: Script to convert JSON knowledge base to plain text format
- `dynamo_utils.py`: Utility functions for DynamoDB operations
- `knowledge_base.py`: Functions for interacting with the Bedrock knowledge base
- `rivertown_knowledge_base_2.json`: JSON file containing the company's knowledge base
- `test_bedrock.py`: Test suite for various components of the application

## Usage Instructions

### Installation

1. Ensure you have Python 3.8+ installed
2. Clone the repository:
   ```
   git clone <repository-url>
   cd rivertown-ball-company-chatbot
   ```
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Set up AWS credentials and configure the following environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `BEDROCK_KB_ID`
   - `BLAND_API_KEY`

2. Ensure you have the necessary AWS permissions to access Bedrock, DynamoDB, and other required services.

### Running the Application

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Open a web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`)

### Testing

Run the test suite to verify the setup and functionality:

```
python test_bedrock.py
```

This will test Claude integration, knowledge base retrieval, combined chat service, Bland AI integration, environment variables, DynamoDB connection, and order lookup functionality.

### Troubleshooting

1. AWS Credentials Issues:
   - Ensure your AWS credentials are correctly set in your environment variables or AWS credentials file.
   - Verify that the IAM user or role has the necessary permissions for Bedrock, DynamoDB, and other AWS services used in the project.

2. Knowledge Base Errors:
   - Check that the `BEDROCK_KB_ID` environment variable is set correctly.
   - Verify that the knowledge base has been properly set up and populated in AWS Bedrock.

3. Bland AI Integration Problems:
   - Confirm that the `BLAND_API_KEY` is set and valid.
   - Check the Bland AI dashboard for any account or API usage issues.

4. DynamoDB Connection Failures:
   - Ensure that the DynamoDB table `Rivertownball-cus` exists in the specified AWS region.
   - Verify that your AWS credentials have read access to the DynamoDB table.

5. Streamlit App Not Loading:
   - Check that all required Python packages are installed.
   - Verify that you're running the app from the correct directory.

For any persistent issues, enable debug logging in `bedrock_utils.py` and `knowledge_base.py` by setting the log level to `DEBUG`. Review the logs for more detailed error information.

## Data Flow

The Rivertown Ball Company chatbot processes user requests through the following data flow:

1. User Input: The user enters a question or request through the Streamlit interface in `app.py`.

2. Claude AI Processing: The input is sent to Claude AI via AWS Bedrock using functions in `bedrock_utils.py`. Claude analyzes the input and determines the appropriate response type.

3. Knowledge Base Retrieval: If additional information is needed, the system queries the knowledge base using functions in `knowledge_base.py`.

4. Response Generation: The `chat_service.py` module combines Claude's response with knowledge base information to create a comprehensive answer.

5. Order Lookup: For order-related queries, the system accesses DynamoDB using functions in `dynamo_utils.py` to retrieve customer order information.

6. Phone Call Request: If a user requests to speak with a representative, the system initiates a call using the Bland AI integration.

7. Response Display: The final response is formatted and displayed to the user through the Streamlit interface.

```
[User Input] -> [Streamlit App] -> [Claude AI] -> [Knowledge Base]
                      ^                |
                      |                v
                [DynamoDB] <-- [Response Generation]
                      ^                |
                      |                v
               [Bland AI] <-- [Phone Call Request]
                                      |
                                      v
                               [User Interface]
```

## Infrastructure

The Rivertown Ball Company chatbot utilizes the following AWS resources:

- Lambda:
  - `rivertownball-lambda`: Main Lambda function for processing chat requests
  - `rivertownball-order-lookup`: Lambda function for DynamoDB order lookups

- DynamoDB:
  - `Rivertownball-cus`: Table for storing customer order information

- Bedrock:
  - Knowledge Base: Stores company and product information
  - Claude AI Model: Handles natural language processing and response generation

- API Gateway:
  - `rivertownball-api`: API endpoint for the chatbot interface

- S3:
  - `rivertownball-assets`: Bucket for storing static assets and configuration files

Note: The actual resource names and configurations may vary based on your specific deployment.