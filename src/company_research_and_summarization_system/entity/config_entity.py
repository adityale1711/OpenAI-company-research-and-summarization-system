from dataclasses import dataclass


@dataclass
class GoogleSheetsServiceConfig:
    """
    Configuration for Google Sheets service.
    """
    GOOGLE_SHEETS_CREDENTIALS_FILE: str
    GOOGLE_SHEETS_ID: str


@dataclass
class OpenAIServiceConfig:
    """
    Configuration for OpenAI Service
    """
    OPENAI_API_KEY: str
    MAX_RETRIES: int
    RATE_LIMIT_CALLS_PER_MINUTE: int
    PROMPT_PATH: str
    MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float
    TOP_P: float
    FREQUENCY_PENALTY: float
    PRESENCE_PENALTY: float
