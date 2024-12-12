# Changelog

## [1.0.0] - 2024-03-21

### Changed
- Migrated from environment variables (.env.local) to AWS Secrets Manager for secure credential management
- Updated all service initialization code to use AWS Secrets Manager
- Removed dependency on python-dotenv package
- Centralized secret management in bedrock_utils.get_secret() function

### Security
- Improved security by moving sensitive credentials to AWS Secrets Manager
- Removed local .env.local file containing sensitive information
- Implemented proper error handling for secret retrieval

### Modified Files
- bedrock_utils.py: Added get_secret() function and updated initialization code
- app.py: Removed dotenv dependency and updated to use AWS Secrets Manager
- knowledge_base.py: Updated to use AWS Secrets Manager for credentials
- dynamo_utils.py: Updated to use AWS Secrets Manager for AWS credentials 