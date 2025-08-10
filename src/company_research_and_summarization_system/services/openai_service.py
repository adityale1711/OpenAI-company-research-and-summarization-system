import time
import openai

from typing import List, Dict
from ratelimit import sleep_and_retry, limits
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.entity.config_entity import OpenAIServiceConfig


class OpenAIService:
    def __init__(self, config: OpenAIServiceConfig):
        """
        Initialize the OpenAI service with the provided configuration.

        Args:
            config (OpenAIServiceConfig): Configuration for OpenAI service.
        """
        self.config = config

        openai.api_key = self.config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.max_retries = self.config.MAX_RETRIES
        self.rate_limit = self.config.RATE_LIMIT_CALLS_PER_MINUTE

    def _create_company_research_prompt(self, company_name: str) -> str:
        """
        Create a comprehensive prompt for company research.

        This prompt is engineered for:
        1. Consistency: Structured output format
        2. Accuracy: Focus on verifiable information
        3. Completeness: Systematic coverage of key areas
        4. Reliability: Clear handling of limited information

        Args:
            company_name (str): Name of the company to research.

        Returns:
            str: Formatted prompt string.
        """
        try:
            with open(self.config.PROMPT_PATH, 'r') as file:
                prompt_template = file.read()
            prompt = prompt_template.format(company_name=company_name)
            return prompt
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {self.config.PROMPT_PATH}")
            raise

    @sleep_and_retry
    @limits(calls=60, period=60)  # Rate limit to 60 call per minute
    def _make_api_call(self, prompt: str) -> str:
        """
        Make an API call to OpenAI's GPT model with the provided prompt.

        Args:
            prompt (str): The prompt to send to the OpenAI API.

        Returns:
            str: The response from the OpenAI API.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional business analyst with expertise in company research and market analysis. "
                                       "Provide accurate, well-structured business summaries."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE,
                    top_p=self.config.TOP_P,
                    frequency_penalty=self.config.FREQUENCY_PENALTY,
                    presence_penalty=self.config.PRESENCE_PENALTY
                )
                return response.choices[0].message.content.strip()
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit exceeded on attempt {attempt + 1}/{self.max_retries}. Waiting...")
                if attempt < self.max_retries - 1:
                    time.sleep(60)  # Wait 1 minute before retry
                else:
                    logger.error("Max retries exceeded for rate limit error.")
                    raise e
            except openai.APIError as e:
                logger.error(f"OpenAI API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)  # Short wait before retry
                else:
                    logger.error("Max retries exceeded for API error.")
                    raise e
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    raise e

    def _validate_response(self, response: str) -> bool:
        """
        Validate the quality of the response from OpenAI.

        Args:
            response (str): The response text to validate.

        Returns:
            bool: True if the response is valid, False otherwise.
        """
        if not response or len(response.strip()) < 100:
            logger.warning("Received an empty or too short response from OpenAI.")
            return False

        # Check for required sections in the response
        required_sections = [
            'COMPANY OVERVIEW',
            'INDUSTRY & SECTOR',
            'KEY BUSINESS ACTIVITIES'
        ]
        sections_found = sum(1 for section in required_sections if section in response)

        return sections_found >= 2

    def generate_company_summary(self, company_name: str) -> Dict[str, str]:
        """
        Generate a summary for a given company using OpenAI's API.

        Args:
            company_name (str): Name of the company to summarize.

        Returns:
            Dict[str, str]: Dictionary containing the company name and its summary.
        """
        logger.info(f'Generating summary for company: {company_name}')
        try:
            prompt = self._create_company_research_prompt(company_name)
            summary = self._make_api_call(prompt)

            # Validate response quality
            if self._validate_response(summary):
                logger.info(f'Successfully generated summary for {company_name}')
                return {
                    'company_name': company_name,
                    'summary': summary,
                    'status': 'success',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': None
                }
            else:
                logger.warning(f'Low quality response for {company_name}, retrying...')
                return {
                    'company_name': company_name,
                    'summary': summary,
                    'status': 'warning',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': 'Response quality below threshold'
                }
        except Exception as e:
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
        Generate summaries for a batch of companies.

        Args:
            company_names (List[str]): List of company names to summarize.
            progress_callback (callable, optional): Callback function to report progress.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing company names and their summaries.
        """
        summaries = []
        total_companies = len(company_names)

        logger.info(f'Starting batch processing of {total_companies} companies')
        for i, company_name in enumerate(company_names):
            try:
                summary = self.generate_company_summary(company_name)
                summaries.append(summary)

                # Progress callback
                if progress_callback:
                    progress_callback(i + 1, total_companies, company_name)

                # Small delay to be respectful to the API
                time.sleep(1)
            except Exception as e:
                logger.error(f'Error processing {company_name}: {str(e)}')
                summaries.append({
                    'company_name': company_name,
                    'summary': f'Error generating summary: {str(e)}',
                    'status': 'critical_error',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': str(e)
                })

        logger.info(f"Completed batch processing. Processed {len(summaries)} companies")
        return summaries
