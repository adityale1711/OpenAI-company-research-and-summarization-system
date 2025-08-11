import time
import openai

from typing import List, Dict
from ratelimit import sleep_and_retry, limits
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.entity.config_entity import OpenAIServiceConfig


class OpenAIService:
    """
    Comprehensive OpenAI service for AI-powered company research and summarization.

    This service provides a complete interface for OpenAI API operations,
    handling everything from authentication to advanced batch processing with
    intelligent error handling and rate limiting.

    The service is specifically designed for company research workflows,
    providing professional-grade prompt engineering and reliable batch
    processing capabilities that ensure high-quality, consistent results.
    """

    def __init__(self, config: OpenAIServiceConfig):
        """
        Initialize the OpenAI service with the provided configuration.

        Sets up the service with API authentication, model parameters, and
        operational settings for reliable AI-powered text generation.

        Args:
            config (OpenAIServiceConfig): Configuration object containing:
                - OPENAI_API_KEY: OpenAI API authentication key
                - MODEL: OpenAI model identifier (e.g., 'gpt-4-turbo')
                - MAX_TOKENS: Maximum tokens per response
                - TEMPERATURE: Creativity/randomness parameter
                - TOP_P: Nucleus sampling parameter
                - FREQUENCY_PENALTY: Repetition reduction parameter
                - PRESENCE_PENALTY: Topic diversity parameter
                - MAX_RETRIES: Maximum retry attempts for failed requests
                - RATE_LIMIT_CALLS_PER_MINUTE: API rate limiting configuration
                - PROMPT_PATH: Path to prompt template file
        """
        # Store configuration for use throughout the service
        self.config = config

        # Configure OpenAI API authentication (legacy and new client)
        # This ensures compatibility with different OpenAI library versions
        openai.api_key = self.config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)

        # Set up operational parameters for reliability and performance
        self.max_retries = self.config.MAX_RETRIES
        self.rate_limit = self.config.RATE_LIMIT_CALLS_PER_MINUTE

    def _create_company_research_prompt(self, company_name: str) -> str:
        """
        Create a comprehensive, professionally engineered prompt for company research.

        This method loads and formats a sophisticated prompt template designed to
        generate high-quality, consistent company summaries. The prompt is engineered
        for optimal results across various company types and industries.

        Args:
            company_name (str): Name of the company to research and analyze.
                Should be the legal or commonly recognized company name.

        Returns:
            str: Formatted prompt string ready for OpenAI API submission.
                Contains company-specific research instructions and output structure.

        Raises:
            FileNotFoundError: If the prompt template file cannot be found
        """
        try:
            # Load the prompt template from the configured file path
            # This allows for easy modification of prompts without code changes
            with open(self.config.PROMPT_PATH, 'r') as file:
                prompt_template = file.read()

            # Format the template with the specific company name
            # This creates a targeted research prompt for the company
            prompt = prompt_template.format(company_name=company_name)
            return prompt

        except FileNotFoundError:
            # Handle missing prompt file with detailed error information
            logger.error(f"Prompt file not found: {self.config.PROMPT_PATH}")
            raise

    @sleep_and_retry
    @limits(calls=60, period=60)  # Rate limit to 60 calls per minute by default
    def _make_api_call(self, prompt: str) -> str:
        """
        Make a rate-limited API call to OpenAI's GPT model with comprehensive error handling.

        This method implements intelligent retry logic, rate limiting, and error handling
        to ensure reliable communication with the OpenAI API even under challenging
        network conditions or API constraints.

        The method uses professional system prompts to ensure high-quality, business-focused
        responses that are suitable for professional company research and analysis.

        Args:
            prompt (str): The research prompt to send to the OpenAI API.
                Should be a well-formatted research question or instruction.

        Returns:
            str: The AI-generated response from the OpenAI API.
                Contains the company summary and analysis.

        Raises:
            openai.RateLimitError: If rate limits are exceeded after all retries
            openai.APIError: If API errors persist after all retries
            Exception: For other unexpected errors after all retries
        """
        # Attempt API call with intelligent retry logic
        for attempt in range(self.max_retries):
            try:
                # Make the API call with configured model parameters
                response = self.client.chat.completions.create(
                    model=self.config.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional business analyst with expertise in company research and market analysis. "
                                       "Provide accurate, well-structured business summaries based on publicly available information. "
                                       "Focus on factual information and clearly indicate when information is limited or uncertain."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    # Model parameters for optimal business analysis results
                    max_tokens=self.config.MAX_TOKENS,                  # Response length control
                    temperature=self.config.TEMPERATURE,                # Creativity/consistency balance
                    top_p=self.config.TOP_P,                            # Token selection diversity
                    frequency_penalty=self.config.FREQUENCY_PENALTY,    # Reduce repetition
                    presence_penalty=self.config.PRESENCE_PENALTY       # Encourage topic diversity
                )

                # Extract and return the generated content
                return response.choices[0].message.content.strip()

            except openai.RateLimitError as e:
                # Handle rate limiting with appropriate wait time
                logger.warning(f"Rate limit exceeded on attempt {attempt + 1}/{self.max_retries}. Waiting...")
                if attempt < self.max_retries - 1:
                    time.sleep(60)  # Wait 1 minute before retry for rate limits
                else:
                    logger.error("Max retries exceeded for rate limit error.")
                    raise e

            except openai.APIError as e:
                # Handle API errors with shorter wait time
                logger.error(f"OpenAI API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)  # Short wait before retry for API errors
                else:
                    logger.error("Max retries exceeded for API error.")
                    raise e

            except Exception as e:
                # Handle unexpected errors with logging
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)  # Short wait before retry
                else:
                    logger.error("Max retries exceeded for unexpected error.")
                    raise e

    def _validate_response(self, response: str) -> bool:
        """
        Validate the quality and completeness of the AI-generated response.

        This method performs quality assurance on the AI-generated summaries to ensure
        they meet minimum standards for completeness and structure. This helps maintain
        consistent quality across all generated summaries.

        The validation checks for both content length and the presence of key sections
        that indicate a well-structured business analysis.

        Args:
            response (str): The AI-generated response text to validate.
                Should contain structured company analysis with specific sections.

        Returns:
            bool: True if the response meets quality standards, False otherwise.
        """
        # Check for minimum content length to ensure substantive response
        if not response or len(response.strip()) < 100:
            logger.warning("Received an empty or too short response from OpenAI.")
            return False

        # Define required sections that indicate a well-structured business analysis
        required_sections = [
            'COMPANY OVERVIEW',         # Basic company information and description
            'INDUSTRY & SECTOR',        # Industry classification and market context
            'KEY BUSINESS ACTIVITIES'   # Core business operations and activities
        ]

        # Count how many required sections are present in the response
        sections_found = sum(1 for section in required_sections if section in response)

        # Require at least 2 out of 3 sections for a valid response
        # This ensures the summary has sufficient structure and completeness
        return sections_found >= 2

    def generate_company_summary(self, company_name: str) -> Dict[str, str]:
        """
        Generate a comprehensive summary for a single company using OpenAI's API.

        This method orchestrates the complete process of generating an AI-powered
        company summary, including prompt creation, API communication, response
        validation, and error handling. It returns a structured result that
        includes both the summary content and processing metadata.

        The method implements comprehensive error handling to ensure that individual
        company failures don't disrupt batch processing operations.

        Args:
            company_name (str): Name of the company to research and summarize.
                Should be the legal or commonly recognized company name.

        Returns:
            Dict[str, str]: Structured dictionary containing:
                - company_name (str): Original company name
                - summary (str): AI-generated summary text or error message
                - status (str): Processing status ('success', 'warning', 'error')
                - timestamp (str): Processing completion timestamp
                - error (str|None): Error message if processing failed, None if successful
        """
        logger.info(f'Generating summary for company: {company_name}')

        try:
            # STEP 1: Create a professionally engineered research prompt
            prompt = self._create_company_research_prompt(company_name)

            # STEP 2: Make API call with intelligent retry and rate limiting
            summary = self._make_api_call(prompt)

            # STEP 3: Validate response quality and completeness
            if self._validate_response(summary):
                # High-quality response - return success status
                logger.info(f'Successfully generated summary for {company_name}')
                return {
                    'company_name': company_name,
                    'summary': summary,
                    'status': 'success',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': None
                }
            else:
                # Low-quality response - return warning status but include content
                logger.warning(f'Low quality response for {company_name}, marking as warning')
                return {
                    'company_name': company_name,
                    'summary': summary,
                    'status': 'warning',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': 'Response quality below threshold'
                }

        except Exception as e:
            # Handle any errors during summary generation
            logger.error(f'Failed to generate summary for {company_name}: {str(e)}')
            return {
                'company_name': company_name,
                'summary': f'Error generating summary: {str(e)}',
                'status': 'error',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(e)
            }

    def generate_batch_summaries(self, company_names: List[str], progress_callback=None) -> List[Dict[str, str]]:
        """
        Generate comprehensive summaries for a batch of companies with progress tracking.

        This method implements intelligent batch processing that handles multiple companies
        efficiently while providing real-time progress feedback and robust error handling.
        Individual company failures don't stop the entire batch operation.

        The method includes rate limiting, progress tracking, and comprehensive error
        isolation to ensure reliable batch processing even with large company lists.

        Args:
            company_names (List[str]): List of company names to research and summarize.
                Each name should be a string representing the company's legal or common name.

            progress_callback (callable, optional): Function to call for progress updates.
                Should accept three parameters: (current, total, company_name)
                - current (int): Current company index (1-based)
                - total (int): Total number of companies to process
                - company_name (str): Name of company currently being processed

        Returns:
            List[Dict[str, str]]: List of summary dictionaries, one for each company.
                Each dictionary contains the same structure as generate_company_summary():
                - company_name, summary, status, timestamp, error
        """
        # Initialize results collection and tracking variables
        summaries = []
        total_companies = len(company_names)

        logger.info(f'Starting batch processing of {total_companies} companies')

        # Process each company individually with error isolation
        for i, company_name in enumerate(company_names):
            try:
                # Generate summary for the current company
                summary = self.generate_company_summary(company_name)
                summaries.append(summary)

                # Provide progress feedback if callback is available
                if progress_callback:
                    progress_callback(i + 1, total_companies, company_name)

                # Respectful delay to avoid overwhelming the API
                # This helps maintain good API citizenship and prevents rate limiting
                time.sleep(1)

            except Exception as e:
                # Handle critical errors that might occur outside of generate_company_summary
                logger.error(f'Critical error processing {company_name}: {str(e)}')
                summaries.append({
                    'company_name': company_name,
                    'summary': f'Critical error generating summary: {str(e)}',
                    'status': 'critical_error',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': str(e)
                })

        logger.info(f"Completed batch processing. Processed {len(summaries)} companies")
        return summaries
