import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.google_sheets_service import GoogleSheetsService


STAGE_NAME = "Output Pipeline"
class OutputPipeline:
    """
    Output pipeline for the company research and summarization system.
    This pipeline writes company summaries to a Google Sheets document.
    """

    def __init__(self, summaries, worksheet_name: str = None):
        """
        Initialize the output pipeline with the summaries and worksheet name.

        Args:
            summaries (list): List of company summaries to write to Google Sheets.
            worksheet_name (str): Name of the worksheet to create in Google Sheets.
        """
        self.summaries = summaries
        self.worksheet_name = worksheet_name

    def initiate_output_pipeline(self):
        """
        Initiate the output pipeline to write company summaries to Google Sheets.
        """
        try:
            # Load configuration
            config_manager = ConfigurationManager()
            google_sheets_service_config = config_manager.get_google_sheets_service_config()

            # Initialize Google Sheets service
            google_sheets_service = GoogleSheetsService(config=google_sheets_service_config)

            # Create a new summary worksheet and write summaries
            google_sheets_service.create_summary_worksheet()
            google_sheets_service.write_summaries(self.summaries, self.worksheet_name)

            output_url = google_sheets_service.get_worksheet_url(self.worksheet_name)

            return output_url
        except Exception as e:
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the output pipeline to write summaries to Google Sheets.
        """
        try:
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")
            output_url = self.initiate_output_pipeline()
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return output_url
        except Exception as e:
            print(f"Error in {STAGE_NAME}: {str(e)}")

