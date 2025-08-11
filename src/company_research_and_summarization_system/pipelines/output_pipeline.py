import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.google_sheets_service import GoogleSheetsService


# Pipeline stage identifier for logging and user feedback
STAGE_NAME = "Output Pipeline"


class OutputPipeline:
    """
    Output pipeline for the company research and summarization system.

    This pipeline serves as the third and final stage in the processing workflow,
    responsible for writing company summaries to a Google Sheets document and
    providing users with organized, accessible results.

    The pipeline implements intelligent data processing that extracts structured
    information from AI-generated summaries and organizes it in a user-friendly format.
    """

    def __init__(self, summaries, worksheet_name: str = None):
        """
        Initialize the output pipeline with the summaries and optional worksheet name.

        The initialization prepares the pipeline for data processing and output
        by storing the summary data and configuring the target worksheet.

        Args:
            summaries (list): List of company summary dictionaries to write to Google Sheets.
                Each dictionary should contain:
                - company_name (str): Name of the company
                - summary (str): AI-generated summary text
                - status (str): Processing status ('success', 'warning', 'error')
                - timestamp (str): Processing completion timestamp
                - error (str, optional): Error message if processing failed

            worksheet_name (str, optional): Name of the worksheet to create in Google Sheets.
                If not provided, a default name will be used based on current timestamp.
                The worksheet name should be descriptive and follow Google Sheets naming conventions.
        """
        # Store the summary data for processing and output
        self.summaries = summaries

        # Store the optional worksheet name for custom result organization
        # If None, the Google Sheets service will generate a default name
        self.worksheet_name = worksheet_name

    def initiate_output_pipeline(self):
        """
        Initiate the output pipeline to write company summaries to Google Sheets.

        The method leverages the Google Sheets service's advanced capabilities,
        including automatic formatting, metadata extraction, and URL generation.

        Returns:
            str: Direct URL to the Google Sheets worksheet containing the results.
                This URL can be shared with stakeholders for immediate access to the data.

        Raises:
            Exception: Wraps any underlying exceptions with pipeline context
        """
        try:
            # STEP 1: Load Google Sheets service configuration from environment variables
            # The configuration manager handles .env file loading and parameter validation
            config_manager = ConfigurationManager()
            google_sheets_service_config = config_manager.get_google_sheets_service_config()

            # STEP 2: Initialize Google Sheets service with authentication and spreadsheet access
            # This handles service account authentication and spreadsheet connectivity
            google_sheets_service = GoogleSheetsService(config=google_sheets_service_config)

            # STEP 3: Create a new summary worksheet with proper structure and formatting
            # This sets up headers, formatting, and prepares the worksheet for data
            google_sheets_service.create_summary_worksheet()

            # STEP 4: Process and write summaries with metadata extraction
            # The service extracts structured information from AI summaries and organizes it
            google_sheets_service.write_summaries(self.summaries, self.worksheet_name)

            # STEP 5: Generate and return the direct access URL
            # This provides stakeholders with immediate access to the results
            output_url = google_sheets_service.get_worksheet_url(self.worksheet_name)

            return output_url

        except Exception as e:
            # Wrap any exceptions with pipeline context for better error tracking
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the output pipeline to write summaries to Google Sheets and return the access URL.

        The method uses terminal width detection to create visually appealing
        separator lines that adapt to different terminal sizes, maintaining
        consistency with other pipeline stages.

        Returns:
            str: Direct URL to the Google Sheets worksheet containing organized results,
                or None if a critical error occurs during processing

        Console Output:
            Displays formatted stage separators showing pipeline progress:
            =============== Output Pipeline ===============
            [Data processing and Google Sheets operations]
            =============== Output Pipeline ===============
        """
        try:
            # Create visually appealing stage separators that adapt to terminal width
            # This maintains consistency with other pipeline stages and improves UX
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            # Execute the core pipeline logic with data processing and Google Sheets operations
            # This organizes the AI-generated summaries into a professional, accessible format
            output_url = self.initiate_output_pipeline()

            # Display completion separator to indicate successful pipeline completion
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return output_url

        except Exception as e:
            # Provide user-friendly error output while maintaining detailed logging
            # This allows the main workflow to handle the error gracefully
            print(f"Error in {STAGE_NAME}: {str(e)}")
            # Note: Returning None allows the main workflow to handle the error gracefully
