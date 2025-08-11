import gspread
import pandas as pd

from typing import Optional, List, Dict
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
        self.worksheet_name_output = 'Company Summaries'
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

    def create_summary_worksheet(self, worksheet_name: Optional[str] = None) -> None:
        """
        Create a new worksheet for company summaries if it doesn't exist.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to retrieve companies from.
                If None, defaults to the first worksheet.
        """
        sheet_name = worksheet_name or self.worksheet_name_output

        try:
            # Check if worksheet already exist
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                logger.info(f"Worksheet '{sheet_name}' already exists")

                # Clear existing content
                worksheet.clear()
                logger.info(f"Cleared existing content in worksheet '{sheet_name}'")
            except gspread.WorksheetNotFound:
                # Create new worksheet
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                logger.info(f"Created new worksheet '{sheet_name}'")

            # Setup headers
            headers = [
                'Company Name',
                'Summary',
                'Processing Status',
                'Timestamp',
                'Error Message',
                'Data Confidence',
                'Industry',
                'Key Activities',
                'Target Market',
                'Business Model'
            ]
            worksheet.append_row(headers)

            # Format headers (make them bold)
            worksheet.format(
                'A1:J1', {
                    'textFormat': {
                        'bold': True
                    },
                    'backgroundColor': {
                        'red': 0.9,
                        'green': 0.9,
                        'blue': 0.9
                    }
                }
            )

            logger.info(f"Setup headers in worksheet '{sheet_name}'")
        except Exception as e:
            logger.error(f'Error creating summary worksheet: {str(e)}')
            raise e

    def _extract_confidence(self, summary_text: str) -> str:
        """
        Extract confidence level from the summary text.

        Args:
            summary_text (str): The summary text to extract confidence from.

        Returns:
            str: Extracted confidence level or 'Not specified' if not found.
        """
        if 'DATA CONFIDENCE:' in summary_text:
            try:
                confidence_section = summary_text.split('DATA CONFIDENCE:')[1].split('\n')[0]
                if 'HIGH' in confidence_section.upper():
                    return 'HIGH'
                elif 'MEDIUM' in confidence_section.upper():
                    return 'MEDIUM'
                elif 'LOW' in confidence_section.upper():
                    return 'LOW'
            except Exception:
                pass
        return 'Not specified'

    def _extract_industry(self, summary_text: str) -> str:
        """
        Extract industry from the summary text.

        Args:
            summary_text (str): The summary text to extract industry from.

        Returns:
            str: Extracted industry or 'Not specified' if not found.
        """
        if 'INDUSTRY & SECTOR:' in summary_text:
            try:
                industry_section = summary_text.split('INDUSTRY & SECTOR:')[1].split('\n')[0]
                return industry_section.strip()[:100]  # Limit to 100 characters
            except Exception:
                pass
        return 'Not specified'

    def _extract_key_activities(self, summary_text: str) -> str:
        """
        Extract key activities from the summary text.

        Args:
            summary_text (str): The summary text to extract key activities from.

        Returns:
            str: Extracted key activities or 'Not specified' if not found.
        """
        if 'KEY BUSINESS ACTIVITIES:' in summary_text:
            try:
                activities_section = summary_text.split('KEY BUSINESS ACTIVITIES:')[1]
                if 'TARGET MARKET:' in activities_section:
                    activities_section = activities_section.split('TARGET MARKET:')[0]
                return activities_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _extract_target_market(self, summary_text: str) -> str:
        """
        Extract target market from the summary text.

        Args:
            summary_text (str): The summary text to extract target market from.

        Returns:
            str: Extracted target market or 'Not specified' if not found.
        """
        if 'TARGET MARKET:' in summary_text:
            try:
                market_section = summary_text.split('TARGET MARKET:')[1]
                if 'BUSINESS MODEL:' in market_section:
                    market_section = market_section.split('BUSINESS MODEL:')[0]
                return market_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _extract_business_model(self, summary_text: str) -> str:
        """
        Extract business model from the summary text.

        Args:
            summary_text (str): The summary text to extract business model from.

        Returns:
            str: Extracted business model or 'Not specified' if not found.
        """
        if 'BUSINESS MODEL:' in summary_text:
            try:
                model_section = summary_text.split('BUSINESS MODEL:')[1]
                if 'KEY DIFFERENTIATORS:' in model_section:
                    model_section = model_section.split('KEY DIFFERENTIATORS:')[0]
                return model_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _format_worksheet(self, worksheet) -> None:
        """
        Format the worksheet to ensure proper display of data.

        Args:
            worksheet: The Google Sheets worksheet to format.
        """
        try:
            # Auto-resize columns
            worksheet.columns_auto_resize(0, 9) # Resize columns A to J

            # Format summary column to wrap text
            worksheet.format(
                'B:B',
                {
                    'wrapStrategy': 'WRAP',
                }
            )

            logger.info("Worksheet formatted successfully")
        except Exception as e:
            logger.error(f"Error formatting the worksheet: {str(e)}")

    def write_summaries(self, summaries: List[Dict], worksheet_name: Optional[str] = None) -> None:
        """
        Write company summaries to the specified Google Sheets worksheet.

        Args:
            summaries (List[Dict]): List of dictionaries containing company summaries.
            worksheet_name (Optional[str]): Name of the worksheet to write summaries to.
                If None, defaults to the output worksheet.
        """
        sheet_name = worksheet_name or self.worksheet_name_output

        try:
            # Get the worksheet
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # Prepare data for writing
            rows_to_add = []

            for summary in summaries:
                # Extract additional information from the summary
                summary_text = summary.get('summary', '')
                confidence = self._extract_confidence(summary_text)
                industry = self._extract_industry(summary_text)
                key_activities = self._extract_key_activities(summary_text)
                target_market = self._extract_target_market(summary_text)
                business_model = self._extract_business_model(summary_text)

                row = [
                    summary.get('company_name', ''),
                    summary_text,
                    summary.get('status', ''),
                    summary.get('timestamp', ''),
                    summary.get('error', ''),
                    confidence,
                    industry,
                    key_activities,
                    target_market,
                    business_model
                ]
                rows_to_add.append(row)

            # Add all rows at once for efficiency
            if rows_to_add:
                worksheet.append_rows(rows_to_add)
                logger.info(f"Successfully wrote {len(rows_to_add)} summaries to '{sheet_name}'")

                # Auto-resize columns for better readability
                self._format_worksheet(worksheet)
            else:
                logger.warning("No summaries to write to Google Sheets")
        except Exception as e:
            logger.error(f"Error writing summaries to Google Sheets: {str(e)}")
            raise e

    def get_worksheet_url(self, worksheet_name: Optional[str] = None) -> str:
        """
        Get the URL of the specified Google Sheets worksheet.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to get the URL for.
                If None, defaults to the output worksheet.

        Returns:
            str: URL of the specified worksheet.
        """
        sheet_name = worksheet_name or self.worksheet_name_output
        try:
            # Get the worksheet
            worksheet = self.spreadsheet.worksheet(sheet_name)
            url = f"https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEETS_ID}/edit#gid={worksheet.id}"

            return url
        except Exception as e:
            logger.error(f"Error getting worksheet URL: {str(e)}")
            raise f'https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEETS_ID}/edit'
