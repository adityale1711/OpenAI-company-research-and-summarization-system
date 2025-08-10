import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.openai_service import OpenAIService


STAGE_NAME = "Generate Pipeline"
class GeneratePipeline:
    """
    Generate pipeline for the company research and summarization system.
    This pipeline retrieves company summaries using the OpenAI service.
    """

    def __init__(self, companies: list, progress_callback=None):
        """
        Initialize the generate pipeline with the list of companies and an optional progress callback.

        Args:
            companies (list): List of company names to summarize.
            progress_callback (callable, optional): Callback function to report progress.
        """
        self.companies = companies
        self.progress_callback = progress_callback

    def initiate_generate_pipeline(self):
        """
        Initiate the generate pipeline to retrieve company summaries using OpenAI service.
        """
        try:
            # Load configuration
            config_manager = ConfigurationManager()
            openai_service_config = config_manager.get_openai_service_config()

            # Initialize Google Sheets service
            openai_service = OpenAIService(config=openai_service_config)

            # Retrieve company list from Google Sheets
            summaries = openai_service.generate_batch_summaries(self.companies, self.progress_callback)

            return summaries
        except Exception as e:
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the generate pipeline to retrieve and return the list of company summaries.
        """
        try:
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")
            generate_pipeline = self.initiate_generate_pipeline()
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return generate_pipeline
        except Exception as e:
            print(f"Error in {STAGE_NAME}: {str(e)}")

