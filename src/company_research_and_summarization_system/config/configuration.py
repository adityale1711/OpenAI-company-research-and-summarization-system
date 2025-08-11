import os
from dotenv import load_dotenv
from src.company_research_and_summarization_system.entity.config_entity import (GoogleSheetsServiceConfig,
                                                                                OpenAIServiceConfig)


class ConfigurationManager:
    """
    Centralized configuration manager for the application.

    This class handles loading environment variables and creating service-specific
    configuration objects. It ensures all configurations are loaded consistently
    and provides a single point of access for all service configurations.

    The manager automatically loads environment variables from a .env file if present,
    making it easy to manage different configurations for development, testing, and production.
    """

    def __init__(self):
        """
        Initialize the configuration manager.

        Automatically loads environment variables from a .env file if present.
        This allows for easy configuration management across different environments
        without hardcoding sensitive information in the source code.
        """
        # Load environment variables from .env file
        # This is essential for keeping sensitive data like API keys out of source code
        load_dotenv()

    def get_google_sheets_service_config(self) -> GoogleSheetsServiceConfig:
        """
        Get the configuration for Google Sheets service.

        Creates and returns a configuration object containing all necessary
        parameters for Google Sheets API integration. This includes service
        account credentials and spreadsheet identification.

        Returns:
            GoogleSheetsServiceConfig: Configuration object for Google Sheets service
                containing credentials file path and spreadsheet ID.

        Environment Variables Used:
            - GOOGLE_SHEETS_CREDENTIALS_FILE: Path to service account JSON credentials
            - GOOGLE_SHEETS_ID: The unique identifier of the Google Sheets document
        """
        google_sheets_service_config = GoogleSheetsServiceConfig(
            # Path to Google Service Account credentials JSON file
            # This file contains the private key and client information needed for authentication
            GOOGLE_SHEETS_CREDENTIALS_FILE=os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),

            # Google Sheets document ID (found in the URL of the spreadsheet)
            # Format: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/edit
            GOOGLE_SHEETS_ID=os.getenv('GOOGLE_SHEETS_ID')
        )

        return google_sheets_service_config

    def get_openai_service_config(self) -> OpenAIServiceConfig:
        """
        Get the configuration for OpenAI Service.

        Creates and returns a configuration object containing all necessary
        parameters for OpenAI API integration. This includes API authentication,
        model parameters, rate limiting, and prompt configuration.

        Returns:
            OpenAIServiceConfig: Configuration object for OpenAI service
                containing API key, model parameters, and operational settings.

        Environment Variables Used:
            Authentication:
                - OPENAI_API_KEY: OpenAI API authentication key

            Operational:
                - MAX_RETRIES: Maximum retry attempts for failed requests
                - RATE_LIMIT_CALLS_PER_MINUTE: API rate limiting (calls per minute)
                - PROMPT_PATH: File path to the prompt template

            Model Parameters:
                - MODEL: OpenAI model identifier (e.g., 'gpt-4-turbo', 'gpt-3.5-turbo')
                - MAX_TOKENS: Maximum tokens in the response
                - TEMPERATURE: Sampling temperature (0.0 = deterministic, 2.0 = very random)
                - TOP_P: Nucleus sampling parameter (0.0-1.0)
                - FREQUENCY_PENALTY: Reduces repetition (-2.0 to 2.0)
                - PRESENCE_PENALTY: Encourages topic diversity (-2.0 to 2.0)
        """
        openai_service_config = OpenAIServiceConfig(
            # OpenAI API authentication key - required for all API calls
            OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),

            # Maximum number of retry attempts for failed API calls
            # Helps handle temporary network issues or rate limiting
            MAX_RETRIES=int(os.getenv('MAX_RETRIES')),

            # Rate limiting configuration to respect OpenAI's usage limits
            # Prevents exceeding API quotas and ensures sustainable usage
            RATE_LIMIT_CALLS_PER_MINUTE=int(os.getenv('RATE_LIMIT_CALLS_PER_MINUTE')),

            # Path to the prompt template file used for company research
            # Allows for easy modification of prompts without code changes
            PROMPT_PATH=os.getenv('PROMPT_PATH'),

            # OpenAI model to use for text generation
            # Different models have different capabilities and costs
            MODEL=os.getenv('MODEL'),

            # Maximum number of tokens in the generated response
            # Controls response length and API costs
            MAX_TOKENS=int(os.getenv('MAX_TOKENS')),

            # Sampling temperature: 0.0 = deterministic, 2.0 = very creative
            # Lower values produce more focused and consistent outputs
            TEMPERATURE=float(os.getenv('TEMPERATURE')),

            # Nucleus sampling parameter: controls diversity of token selection
            # 1.0 = consider all tokens, lower values = more focused
            TOP_P=float(os.getenv('TOP_P')),

            # Frequency penalty: reduces repetition of tokens
            # Positive values decrease likelihood of repeating the same text
            FREQUENCY_PENALTY=float(os.getenv('FREQUENCY_PENALTY')),

            # Presence penalty: encourages talking about new topics
            # Positive values increase likelihood of introducing new topics
            PRESENCE_PENALTY=float(os.getenv('PRESENCE_PENALTY'))
        )

        return openai_service_config
