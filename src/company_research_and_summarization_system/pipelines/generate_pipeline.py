import shutil

from src.company_research_and_summarization_system.config.configuration import ConfigurationManager
from src.company_research_and_summarization_system.services.openai_service import OpenAIService


# Pipeline stage identifier for logging and user feedback
STAGE_NAME = "Generate Pipeline"


class GeneratePipeline:
    """
    Generate pipeline for the company research and summarization system.

    This pipeline serves as the second stage in the three-stage processing workflow,
    responsible for generating comprehensive company summaries using OpenAI's language models.

    The pipeline implements intelligent batch processing with progress tracking, error handling,
    and rate limiting to ensure reliable and efficient processing of large company lists.
    """

    def __init__(self, companies: list, progress_callback=None):
        """
        Initialize the generate pipeline with the list of companies and an optional progress callback.

        The initialization prepares the pipeline for batch processing by storing the company list
        and setting up the progress tracking mechanism.

        Args:
            companies (list): List of company names to generate summaries for.
                Each company name should be a string representing the company's legal or common name.

            progress_callback (callable, optional): Callback function to report progress during
                batch processing. The callback should accept three parameters:
                - current (int): Current company index being processed (1-based)
                - total (int): Total number of companies in the batch
                - company_name (str): Name of the company currently being processed
        """
        # Store the list of companies to process
        self.companies = companies

        # Store the optional progress callback for user feedback
        # This allows real-time monitoring of long-running batch operations
        self.progress_callback = progress_callback

    def initiate_generate_pipeline(self):
        """
        Initiate the generate pipeline to retrieve company summaries using OpenAI service.

        The method leverages the OpenAI service's batch processing capabilities,
        which include automatic rate limiting, retry mechanisms, and error handling.

        Returns:
            list: List of dictionaries containing company summaries and metadata.
                Each dictionary contains:
                - company_name (str): Name of the company
                - summary (str): Generated AI summary
                - status (str): Processing status ('success', 'warning', 'error')
                - timestamp (str): Processing timestamp
                - error (str): Error message if processing failed

        Raises:
            Exception: Wraps any underlying exceptions with pipeline context
        """
        try:
            # STEP 1: Load OpenAI service configuration from environment variables
            # The configuration manager handles .env file loading and parameter validation
            config_manager = ConfigurationManager()
            openai_service_config = config_manager.get_openai_service_config()

            # STEP 2: Initialize OpenAI service with authentication and model parameters
            # This handles API key validation, model selection, and parameter configuration
            openai_service = OpenAIService(config=openai_service_config)

            # STEP 3: Execute batch summary generation with progress tracking
            # The service handles rate limiting, retries, and individual error isolation
            summaries = openai_service.generate_batch_summaries(self.companies, self.progress_callback)

            return summaries

        except Exception as e:
            # Wrap any exceptions with pipeline context for better error tracking
            raise Exception(f"Error in {STAGE_NAME}: {str(e)}")

    def run(self):
        """
        Run the generate pipeline to retrieve and return the list of company summaries.

        The method uses terminal width detection to create visually appealing
        separator lines that adapt to different terminal sizes, improving the
        user experience during long-running operations.

        Returns:
            list: List of company summary dictionaries ready for output processing,
                or None if a critical error occurs

        Console Output:
            Displays formatted stage separators showing pipeline progress:
            =============== Generate Pipeline ===============
            [AI generation progress and logging messages]
            =============== Generate Pipeline ===============
        """
        try:
            # Create visually appealing stage separators that adapt to terminal width
            # This improves user experience by clearly showing pipeline progress
            term_width = shutil.get_terminal_size().columns
            separator_length = (term_width - len(STAGE_NAME) - 2) // 2
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            # Execute the core pipeline logic with batch processing and progress tracking
            # This is where the AI-powered summarization happens
            generate_pipeline = self.initiate_generate_pipeline()

            # Display completion separator to indicate pipeline stage completion
            print(f"{'=' * separator_length} {STAGE_NAME} {'=' * separator_length}")

            return generate_pipeline

        except Exception as e:
            # Provide user-friendly error output while maintaining detailed logging
            # This allows the main workflow to handle the error gracefully
            print(f"Error in {STAGE_NAME}: {str(e)}")
            # Note: Returning None allows the main workflow to handle the error gracefully
