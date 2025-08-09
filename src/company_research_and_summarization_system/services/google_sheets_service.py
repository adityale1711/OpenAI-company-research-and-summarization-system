import gspread
import pandas as pd

from typing import Optional, List
from google.auth.exceptions import GoogleAuthError
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.entity.config_entity import GoogleSheetsServiceConfig


class GoogleSheetsService:
    def __init__(self, config: GoogleSheetsServiceConfig):
        """
        Initialize the Google Sheets service with the provided configuration.

        Args:
            config (GoogleSheetsServiceConfig): Configuration for Google Sheets service.
        """
        self.config = config
        self.worksheet_name_input = 'Company List'
        self.spreadsheet = None
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using service account credentials.
        """
        try:
            # Use service account credentials
            self.client = gspread.service_account(filename=self.config.GOOGLE_SHEETS_CREDENTIALS_FILE)
            self.spreadsheet = self.client.open_by_key(self.config.GOOGLE_SHEETS_ID)

            logger.info("Successfully authenticated with Google Sheets API")
        except GoogleAuthError as e:
            logger.error(f"Google authentication failed: {str(e)}")
            raise e
        except FileNotFoundError as e:
            logger.error(f"Credentials file not found: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during Google Sheets authentication: {str(e)}")
            raise e

    def get_company_list(self, worksheet_name: Optional[str] = None) -> List[str]:
        """
        Retrieve a list of companies from the specified Google Sheets worksheet.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to retrieve companies from.
                If None, defaults to the first worksheet.

        Returns:
            List[str]: List of company names.
        """
        sheet_name = worksheet_name or self.worksheet_name_input

        try:
            # Get the worksheet
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # Get all values from the worksheet
            data = worksheet.get_all_values()

            if not data:
                logger.warning(f"No data found in worksheet '{sheet_name}'")
                return []

            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])

            # Try to find company column (case-insensitive)
            company_column = None
            possible_names = ['company', 'company name', 'company_name', 'name', 'companies']

            for col_name in df.columns:
                if col_name.lower() in possible_names:
                    company_column = col_name
                    break

            if company_column is None:
                # If no specific column found, use first column
                company_column = df.columns[0]
                logger.info(f"No 'company' column found, using first column: '{company_column}'")

            # Extract company names and clean them
            companies = df[company_column].dropna().str.strip().tolist()
            companies = [company for company in companies if company] # Remove empty strings

            logger.info(f"Successfully loaded {len(companies)} companies from '{sheet_name}'")

            return companies
        except gspread.WorksheetNotFound:
            logger.error(f"Worksheet '{sheet_name}' not found in the spreadsheet")
            raise Exception(f"Worksheet '{sheet_name}' not found. Please check the worksheet name.")
        except Exception as e:
            logger.error(f"Error reading company list from Google Sheets: {str(e)}")
            raise e
