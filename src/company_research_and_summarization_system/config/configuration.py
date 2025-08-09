import os
from dotenv import load_dotenv
from src.company_research_and_summarization_system.entity.config_entity import GoogleSheetsServiceConfig


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
