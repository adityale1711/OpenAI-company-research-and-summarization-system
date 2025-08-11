import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.google_sheets_service import GoogleSheetsService


# Pipeline stage identifier for logging and user feedback
STAGE_NAME = "Input Pipeline"


class InputPipeline:
    """
    Input pipeline for the company research and summarization system.

    This pipeline serves as the first stage in the three-stage processing workflow,
    responsible for retrieving a list of companies from a Google Sheets document.

    The pipeline implements a standardized interface that can be easily extended
    or modified to support different data sources in the future.
    """

    def __init__(self):
        """
        Initialize the input pipeline with the necessary configurations and services.

        The initialization is lightweight and doesn't perform any external operations.
        Actual data retrieval happens during the run() method execution.
        """
        pass

    def initiate_input_pipeline(self):
        """
        Initiate the input pipeline to retrieve company data from Google Sheets.

        Returns:
            list: List of company names retrieved from Google Sheets

        Raises:
            Exception: Wraps any underlying exceptions with pipeline context
        """
        try:
            # STEP 1: Load configuration from environment variables
            # The configuration manager handles .env file loading and type conversion
            config_manager = ConfigurationManager()
            google_sheets_service_config = config_manager.get_google_sheets_service_config()

            # STEP 2: Initialize Google Sheets service with authentication
            # This handles service account authentication and spreadsheet access
            google_sheets_service = GoogleSheetsService(config=google_sheets_service_config)

            # STEP 3: Retrieve company list from Google Sheets
            # The service handles data retrieval, validation, and cleaning
            companies = google_sheets_service.get_company_list()

            return companies

        except Exception as e:
            # Wrap any exceptions with pipeline context for better error tracking
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the input pipeline to retrieve and return the list of companies.

        This is the main entry point for the pipeline, providing:
        - User-friendly console output with stage identification
        - Error handling with informative messages
        - Consistent return interface for pipeline chaining

        The method uses terminal width detection to create visually appealing
        separator lines that adapt to different terminal sizes.

        Returns:
            list: List of company names ready for processing, or None if error occurs

        Console Output:
            Displays formatted stage separators showing pipeline progress:
            =============== Input Pipeline ===============
            [Pipeline execution and logging messages]
            =============== Input Pipeline ===============
        """
        try:
            # Create visually appealing stage separators that adapt to terminal width
            # This improves user experience by clearly showing pipeline progress
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            # Execute the core pipeline logic
            input_pipeline = self.initiate_input_pipeline()

            # Display completion separator
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return input_pipeline

        except Exception as e:
            # Provide user-friendly error output while maintaining detailed logging
            print(f"Error in {STAGE_NAME}: {str(e)}")
            # Note: Returning None allows the main workflow to handle the error gracefully
