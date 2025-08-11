from dataclasses import dataclass


@dataclass
class GoogleSheetsServiceConfig:
    """
    Configuration dataclass for Google Sheets service integration.

    This class encapsulates all configuration parameters required for Google Sheets API
    operations, including authentication credentials and spreadsheet identification.

    The configuration uses Google Service Account authentication, which is ideal for
    server-to-server applications where user interaction is not required.

    Attributes:
        GOOGLE_SHEETS_CREDENTIALS_FILE (str): Absolute or relative path to the Google
            Service Account credentials JSON file. This file contains the private key
            and client information needed for authentication.

        GOOGLE_SHEETS_ID (str): The unique identifier of the Google Sheets document.
            This can be found in the URL of the spreadsheet:
            https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/edit
    """
    GOOGLE_SHEETS_CREDENTIALS_FILE: str # Path to service account JSON credentials file
    GOOGLE_SHEETS_ID: str               # Google Sheets document unique identifier


@dataclass
class OpenAIServiceConfig:
    """
    Configuration dataclass for OpenAI API service integration.

    This class encapsulates all configuration parameters required for OpenAI API
    operations, including authentication, model parameters, rate limiting, and
    operational settings.

    The configuration supports fine-tuning of language model behavior through
    various parameters that control creativity, consistency, and output characteristics.

    Attributes:
        Authentication:
            OPENAI_API_KEY (str): OpenAI API authentication key for accessing the service.

        Operational Settings:
            MAX_RETRIES (int): Maximum number of retry attempts for failed API calls.
                Recommended: 3-5 retries to handle temporary network issues.

            RATE_LIMIT_CALLS_PER_MINUTE (int): Maximum API calls per minute to respect
                OpenAI's rate limits and prevent quota exhaustion.

            PROMPT_PATH (str): File path to the prompt template used for company research.
                Allows for easy modification of prompts without code changes.

        Model Configuration:
            MODEL (str): OpenAI model identifier (e.g., 'gpt-4-turbo', 'gpt-3.5-turbo').
                Different models have varying capabilities, costs, and performance.

            MAX_TOKENS (int): Maximum number of tokens in the generated response.
                Controls output length and directly impacts API costs.

        Generation Parameters:
            TEMPERATURE (float): Sampling temperature (0.0-2.0). Controls randomness:
                - 0.0: Deterministic, always chooses most likely tokens
                - 1.0: Balanced creativity and consistency
                - 2.0: Highly creative but potentially inconsistent

            TOP_P (float): Nucleus sampling parameter (0.0-1.0). Controls diversity:
                - 1.0: Consider all possible tokens
                - 0.1: Only consider top 10% most likely tokens

            FREQUENCY_PENALTY (float): Penalty for token frequency (-2.0 to 2.0):
                - Positive values: Reduce repetition of the same phrases
                - Negative values: Encourage repetition (rarely used)

            PRESENCE_PENALTY (float): Penalty for token presence (-2.0 to 2.0):
                - Positive values: Encourage discussion of new topics
                - Negative values: Encourage staying on current topics
    """
    # Authentication configuration
    OPENAI_API_KEY: str                 # OpenAI API authentication key

    # Operational settings for reliability and rate management
    MAX_RETRIES: int                    # Maximum retry attempts for failed requests
    RATE_LIMIT_CALLS_PER_MINUTE: int    # API rate limiting (calls per minute)
    PROMPT_PATH: str                    # Path to prompt template file

    # Model selection and basic parameters
    MODEL: str                          # OpenAI model identifier
    MAX_TOKENS: int                     # Maximum tokens in response

    # Advanced generation parameters for fine-tuning output behavior
    TEMPERATURE: float                  # Sampling temperature (creativity level)
    TOP_P: float                        # Nucleus sampling (diversity control)
    FREQUENCY_PENALTY: float            # Penalty for repetitive content
    PRESENCE_PENALTY: float             # Penalty for staying on same topics
