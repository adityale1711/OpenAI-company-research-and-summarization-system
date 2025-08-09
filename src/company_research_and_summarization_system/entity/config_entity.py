from dataclasses import dataclass


@dataclass
class GoogleSheetsServiceConfig:
    """
    Configuration for Google Sheets service.
    """
    GOOGLE_SHEETS_CREDENTIALS_FILE: str
    GOOGLE_SHEETS_ID: str
