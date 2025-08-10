import os
from dotenv import load_dotenv
from src.company_research_and_summarization_system.entity.config_entity import (GoogleSheetsServiceConfig,
                                                                                OpenAIServiceConfig)


class ConfigurationManager:
    """
    Configuration manager for the application.
    """

    def __init__(self):
        """
        Initialize the configuration manager.
        """
        load_dotenv()

    def get_google_sheets_service_config(self) -> GoogleSheetsServiceConfig:
        """
        Get the configuration for Google Sheets service.

        Returns:
            GoogleSheetsServiceConfig: Configuration object for Google Sheets service.
        """
        google_sheets_service_config = GoogleSheetsServiceConfig(
            GOOGLE_SHEETS_CREDENTIALS_FILE=os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE'),
            GOOGLE_SHEETS_ID=os.getenv('GOOGLE_SHEETS_ID')
        )

        return google_sheets_service_config

    def get_openai_service_config(self) -> OpenAIServiceConfig:
        """
        Get the configuration for OpenAI Service.

        Returns:
             OpenAIServiceConfig: Configuration object for OpenAI service.
        """
        openai_service_config = OpenAIServiceConfig(
            OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
            MAX_RETRIES=int(os.getenv('MAX_RETRIES')),
            RATE_LIMIT_CALLS_PER_MINUTE=int(os.getenv('RATE_LIMIT_CALLS_PER_MINUTE')),
            PROMPT_PATH=os.getenv('PROMPT_PATH'),
            MODEL=os.getenv('MODEL'),
            MAX_TOKENS=int(os.getenv('MAX_TOKENS')),
            TEMPERATURE=float(os.getenv('TEMPERATURE')),
            TOP_P=float(os.getenv('TOP_P')),
            FREQUENCY_PENALTY=float(os.getenv('FREQUENCY_PENALTY')),
            PRESENCE_PENALTY=float(os.getenv('PRESENCE_PENALTY'))
        )

        return openai_service_config
