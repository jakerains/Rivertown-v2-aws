# Project Map

## Rivertown Ball Company Chatbot

### Core Components
- app.py: Main Streamlit application
  - User interface and chat functionality
  - Session state management
  - Phone call integration with Bland API

### AWS Integration
- bedrock_utils.py: AWS Bedrock integration
  - Secret management with AWS Secrets Manager
  - Claude 3 Haiku model integration
  - Bedrock runtime client initialization

### Knowledge Base
- knowledge_base.py: AWS Bedrock Knowledge Base integration
  - Knowledge base querying
  - Response generation
  - Verification utilities

### Database
- dynamo_utils.py: AWS DynamoDB integration
  - Customer order management
  - Data retrieval and formatting
  - AWS credentials management

### Security
- AWS Secrets Manager
  - Centralized secret management
  - Secure credential storage
  - Environment variable replacement

### External Services
- Bland AI
  - Customer service call integration
  - Voice assistant functionality
  - Call status management

### User Interface
- Streamlit
  - Responsive chat interface
  - Custom styling
  - Session state management

### Documentation
- docs/: Documentation directory
  - CHANGELOG.md: Version history
  - project-map.md: Project structure
  - Implementation details
  - Architecture decisions 