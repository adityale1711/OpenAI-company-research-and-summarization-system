import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.google_sheets_service import GoogleSheetsService


STAGE_NAME = "Input Pipeline"
class InputPipeline:
    """
    Input pipeline for the company research and summarization system.
    This pipeline retrieves a list of companies from a Google Sheets document.
    """

    def __init__(self):
        """
        Initialize the input pipeline with the necessary configurations and services.
        """
        pass

    def initiate_input_pipeline(self):
        """
        Initiate the input pipeline to retrieve company data from Google Sheets.
        """
        try:
            # Load configuration
            config_manager = ConfigurationManager()
            google_sheets_service_config = config_manager.get_google_sheets_service_config()

            # Initialize Google Sheets service
            google_sheets_service = GoogleSheetsService(config=google_sheets_service_config)

            # Retrieve company list from Google Sheets
            companies = google_sheets_service.get_company_list()

            return companies
        except Exception as e:
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the input pipeline to retrieve and return the list of companies.
        """
        try:
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")
            input_pipeline = self.initiate_input_pipeline()
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return input_pipeline
        except Exception as e:
            print(f"Error in {STAGE_NAME}: {str(e)}")

