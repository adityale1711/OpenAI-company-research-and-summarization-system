import gspread
import pandas as pd

from typing import Optional, List, Dict
from google.auth.exceptions import GoogleAuthError
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.entity.config_entity import GoogleSheetsServiceConfig


class GoogleSheetsService:
    """
    Comprehensive Google Sheets service for company research data management.

    This service provides a complete interface for Google Sheets operations,
    handling everything from authentication to advanced data processing and formatting.

    The service is designed to work with the company research pipeline, providing
    flexible input capabilities and professional output formatting that makes
    results easily accessible and shareable.
    """

    def __init__(self, config: GoogleSheetsServiceConfig):
        """
        Initialize the Google Sheets service with the provided configuration.

        Sets up the service with authentication credentials and default worksheet names,
        then immediately authenticates with the Google Sheets API to ensure connectivity.

        Args:
            config (GoogleSheetsServiceConfig): Configuration object containing:
                - GOOGLE_SHEETS_CREDENTIALS_FILE: Path to service account JSON file
                - GOOGLE_SHEETS_ID: Google Sheets document identifier
        """
        # Store configuration for use throughout the service
        self.config = config

        # Define default worksheet names for input and output operations
        # These can be customized based on specific use cases
        self.worksheet_name_input = 'Company List'          # Default input worksheet name
        self.worksheet_name_output = 'Company Summaries'    # Default output worksheet name

        # Initialize spreadsheet reference (will be set during authentication)
        self.spreadsheet = None

        # Authenticate immediately to ensure service is ready for operations
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with Google Sheets API using service account credentials.

        The authentication uses Google Service Account which is ideal for
        server-to-server applications where user interaction is not required.

        Raises:
            GoogleAuthError: If Google authentication fails (invalid credentials, permissions)
            FileNotFoundError: If the credentials file doesn't exist or can't be accessed
            Exception: For other unexpected authentication errors
        """
        try:
            # STEP 1: Authenticate using service account credentials
            # This loads the JSON credentials file and establishes API connection
            self.client = gspread.service_account(filename=self.config.GOOGLE_SHEETS_CREDENTIALS_FILE)

            # STEP 2: Open the target spreadsheet by ID
            # This validates that the service account has access to the specified document
            self.spreadsheet = self.client.open_by_key(self.config.GOOGLE_SHEETS_ID)

            logger.info("Successfully authenticated with Google Sheets API")

        except GoogleAuthError as e:
            # Handle authentication-specific errors (invalid credentials, permissions)
            logger.error(f"Google authentication failed: {str(e)}")
            raise e

        except FileNotFoundError as e:
            # Handle missing credentials file
            logger.error(f"Credentials file not found: {str(e)}")
            raise e

        except Exception as e:
            # Handle any other unexpected errors during authentication
            logger.error(f"Unexpected error during Google Sheets authentication: {str(e)}")
            raise e

    def get_company_list(self, worksheet_name: Optional[str] = None) -> List[str]:
        """
        Retrieve a list of companies from the specified Google Sheets worksheet.

        The method is flexible and can work with worksheets that use different
        column names or structures, making it adaptable to various data sources.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to retrieve companies from.
                If None, defaults to the configured input worksheet name.

        Returns:
            List[str]: List of cleaned company names ready for processing.
                Empty list if no companies are found or data is invalid.

        Raises:
            Exception: For worksheet access errors or data processing failures
        """
        # Use provided worksheet name or fall back to default input worksheet
        sheet_name = worksheet_name or self.worksheet_name_input

        try:
            # STEP 1: Retrieve the target worksheet
            # This validates that the worksheet exists and is accessible
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # STEP 2: Get all values from the worksheet
            # This retrieves the complete dataset for processing
            data = worksheet.get_all_values()

            if not data:
                logger.warning(f"No data found in worksheet '{sheet_name}'")
                return []

            # STEP 3: Convert to DataFrame for easier data manipulation
            # This provides powerful data processing capabilities
            df = pd.DataFrame(data[1:], columns=data[0])  # First row as headers

            # STEP 4: Intelligent company column detection
            # Try to find company column using various common naming conventions
            company_column = None
            possible_names = ['company', 'company name', 'company_name', 'name', 'companies']

            for col_name in df.columns:
                if col_name.lower() in possible_names:
                    company_column = col_name
                    break

            if company_column is None:
                # If no specific column found, use first column as fallback
                company_column = df.columns[0]
                logger.info(f"No 'company' column found, using first column: '{company_column}'")

            # STEP 5: Extract and clean company names
            # Remove null values, trim whitespace, and filter empty strings
            companies = df[company_column].dropna().str.strip().tolist()
            companies = [company for company in companies if company]  # Remove empty strings

            logger.info(f"Successfully loaded {len(companies)} companies from '{sheet_name}'")

            return companies

        except gspread.WorksheetNotFound:
            # Handle missing worksheet error with helpful message
            logger.error(f"Worksheet '{sheet_name}' not found in the spreadsheet")
            raise Exception(f"Worksheet '{sheet_name}' not found. Please check the worksheet name.")

        except Exception as e:
            # Handle any other errors during data retrieval
            logger.error(f"Error reading company list from Google Sheets: {str(e)}")
            raise e

    def create_summary_worksheet(self, worksheet_name: Optional[str] = None) -> None:
        """
        Create a new worksheet for company summaries if it doesn't exist.

        The created worksheet includes columns for all aspects of company summaries
        including metadata extracted from AI-generated content.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to create.
                If None, defaults to the configured output worksheet name.

        Raises:
            Exception: For worksheet creation or formatting errors
        """
        # Use provided worksheet name or fall back to default output worksheet
        sheet_name = worksheet_name or self.worksheet_name_output

        try:
            # STEP 1: Check if worksheet already exists
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                logger.info(f"Worksheet '{sheet_name}' already exists")

                # Clear existing content to ensure clean slate
                worksheet.clear()
                logger.info(f"Cleared existing content in worksheet '{sheet_name}'")

            except gspread.WorksheetNotFound:
                # Create new worksheet with optimized dimensions
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                logger.info(f"Created new worksheet '{sheet_name}'")

            # STEP 2: Setup comprehensive column headers
            # These headers support structured data organization and metadata extraction
            headers = [
                'Company Name',         # Original company identifier
                'Summary',              # Full AI-generated summary text
                'Processing Status',    # Success/warning/error status
                'Timestamp',            # Processing completion time
                'Error Message',        # Detailed error information
                'Data Confidence',      # AI confidence level
                'Industry',             # Extracted industry classification
                'Key Activities',       # Primary business activities
                'Target Market',        # Customer segment identification
                'Business Model'        # Revenue and operational model
            ]
            worksheet.append_row(headers)

            # STEP 3: Apply professional header formatting
            # This creates a visually appealing and clearly organized worksheet
            worksheet.format(
                'A1:J1', {
                    'textFormat': {
                        'bold': True  # Make headers bold for emphasis
                    },
                    # Light gray background
                    'backgroundColor': {
                        'red': 0.9,
                        'green': 0.9,
                        'blue': 0.9
                    }
                }
            )

            logger.info(f"Setup headers in worksheet '{sheet_name}'")

        except Exception as e:
            # Handle any errors during worksheet creation or formatting
            logger.error(f'Error creating summary worksheet: {str(e)}')
            raise e

    def _extract_confidence(self, summary_text: str) -> str:
        """
        Extract confidence level from AI-generated summary text.

        This method parses the structured summary output to identify the AI's
        confidence level in the generated information. This helps users understand
        the reliability of the summary data.

        The method looks for specific confidence indicators in the summary text
        and categorizes them into standardized levels (HIGH, MEDIUM, LOW).

        Args:
            summary_text (str): The AI-generated summary text to parse for confidence indicators.
                Expected to contain a "DATA CONFIDENCE:" section with confidence level.

        Returns:
            str: Extracted confidence level ('HIGH', 'MEDIUM', 'LOW') or 'Not specified'
                if no confidence information is found in the summary.
        """
        if 'DATA CONFIDENCE:' in summary_text:
            try:
                # Extract the confidence section from the summary
                confidence_section = summary_text.split('DATA CONFIDENCE:')[1].split('\n')[0]

                # Perform case-insensitive matching for confidence levels
                if 'HIGH' in confidence_section.upper():
                    return 'HIGH'
                elif 'MEDIUM' in confidence_section.upper():
                    return 'MEDIUM'
                elif 'LOW' in confidence_section.upper():
                    return 'LOW'
            except Exception:
                # Handle any parsing errors gracefully
                pass
        return 'Not specified'

    def _extract_industry(self, summary_text: str) -> str:
        """
        Extract industry classification from AI-generated summary text.

        This method parses the structured summary to identify the company's
        primary industry sector, providing valuable categorization for analysis
        and organization of results.

        Args:
            summary_text (str): The AI-generated summary text to parse for industry information.
                Expected to contain an "INDUSTRY & SECTOR:" section.

        Returns:
            str: Extracted industry classification (limited to 100 characters) or
                'Not specified' if no industry information is found.
        """
        if 'INDUSTRY & SECTOR:' in summary_text:
            try:
                industry_section = summary_text.split('INDUSTRY & SECTOR:')[1].split('\n')[0]
                return industry_section.strip()[:100]  # Limit to 100 characters for display
            except Exception:
                pass
        return 'Not specified'

    def _extract_key_activities(self, summary_text: str) -> str:
        """
        Extract key business activities from AI-generated summary text.

        This method identifies and extracts the primary business activities
        that define what the company does, providing insight into their
        core operations and value proposition.

        Args:
            summary_text (str): The AI-generated summary text to parse for business activities.
                Expected to contain a "KEY BUSINESS ACTIVITIES:" section.

        Returns:
            str: Extracted key business activities (limited to 200 characters) or
                'Not specified' if no activity information is found.
        """
        if 'KEY BUSINESS ACTIVITIES:' in summary_text:
            try:
                activities_section = summary_text.split('KEY BUSINESS ACTIVITIES:')[1]
                # Stop at the next section marker if present
                if 'TARGET MARKET:' in activities_section:
                    activities_section = activities_section.split('TARGET MARKET:')[0]
                return activities_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _extract_target_market(self, summary_text: str) -> str:
        """
        Extract target market information from AI-generated summary text.

        This method identifies the company's target customer segments and
        market focus, providing valuable insights for competitive analysis
        and market positioning understanding.

        Args:
            summary_text (str): The AI-generated summary text to parse for target market data.
                Expected to contain a "TARGET MARKET:" section.

        Returns:
            str: Extracted target market information (limited to 200 characters) or
                'Not specified' if no market information is found.
        """
        if 'TARGET MARKET:' in summary_text:
            try:
                market_section = summary_text.split('TARGET MARKET:')[1]
                # Stop at the next section marker if present
                if 'BUSINESS MODEL:' in market_section:
                    market_section = market_section.split('BUSINESS MODEL:')[0]
                return market_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _extract_business_model(self, summary_text: str) -> str:
        """
        Extract business model information from AI-generated summary text.

        This method identifies how the company generates revenue and operates,
        providing crucial insights into their financial structure and
        operational approach.

        Args:
            summary_text (str): The AI-generated summary text to parse for business model data.
                Expected to contain a "BUSINESS MODEL:" section.

        Returns:
            str: Extracted business model information (limited to 200 characters) or
                'Not specified' if no business model information is found.
        """
        if 'BUSINESS MODEL:' in summary_text:
            try:
                model_section = summary_text.split('BUSINESS MODEL:')[1]
                # Stop at the next section marker if present
                if 'KEY DIFFERENTIATORS:' in model_section:
                    model_section = model_section.split('KEY DIFFERENTIATORS:')[0]
                return model_section.strip()[:200]  # Limit to 200 characters
            except Exception:
                pass
        return 'Not specified'

    def _format_worksheet(self, worksheet) -> None:
        """
        Apply professional formatting to the worksheet for optimal readability.

        The formatting improves user experience when viewing results and
        ensures that all data is properly displayed regardless of content length.

        Args:
            worksheet: The Google Sheets worksheet object to format.
                This should be an authenticated gspread worksheet instance.
        """
        try:
            # Auto-resize all columns (A through J) to fit content optimally
            # This ensures all data is visible without manual column adjustment
            worksheet.columns_auto_resize(0, 9)

            # Configure text wrapping for the summary column (B) to handle long AI-generated content
            # This prevents summary text from being cut off and improves readability
            worksheet.format(
                'B:B',
                {
                    'wrapStrategy': 'WRAP',  # Enable text wrapping for long summaries
                }
            )

            logger.info("Worksheet formatted successfully")

        except Exception as e:
            # Log formatting errors but don't interrupt the data writing process
            logger.error(f"Error formatting the worksheet: {str(e)}")

    def write_summaries(self, summaries: List[Dict], worksheet_name: Optional[str] = None) -> None:
        """
        Write company summaries to the specified Google Sheets worksheet with metadata extraction.

        This method processes and writes the AI-generated summaries to Google Sheets,
        extracting structured metadata and organizing it into a professional format
        that facilitates analysis and sharing.

        The method performs intelligent data processing to extract valuable insights
        from unstructured AI summaries and presents them in organized columns.

        Args:
            summaries (List[Dict]): List of summary dictionaries containing:
                - company_name (str): Name of the company
                - summary (str): AI-generated summary text
                - status (str): Processing status ('success', 'warning', 'error')
                - timestamp (str): Processing completion timestamp
                - error (str, optional): Error message if processing failed

            worksheet_name (Optional[str]): Name of the worksheet to write to.
                If None, defaults to the configured output worksheet name.

        Raises:
            Exception: For worksheet access errors or data writing failures
        """
        # Use provided worksheet name or fall back to default output worksheet
        sheet_name = worksheet_name or self.worksheet_name_output

        try:
            # STEP 1: Access the target worksheet for data writing
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # STEP 2: Prepare data rows with metadata extraction
            rows_to_add = []

            for summary in summaries:
                # Extract the AI-generated summary text for metadata parsing
                summary_text = summary.get('summary', '')

                # Extract structured metadata from the unstructured summary text
                confidence = self._extract_confidence(summary_text)
                industry = self._extract_industry(summary_text)
                key_activities = self._extract_key_activities(summary_text)
                target_market = self._extract_target_market(summary_text)
                business_model = self._extract_business_model(summary_text)

                # Organize all data into a structured row for the worksheet
                row = [
                    summary.get('company_name', ''),    # Company identifier
                    summary_text,                       # Full AI summary
                    summary.get('status', ''),          # Processing status
                    summary.get('timestamp', ''),       # Processing time
                    summary.get('error', ''),           # Error information
                    confidence,                         # AI confidence level
                    industry,                           # Industry classification
                    key_activities,                     # Business activities
                    target_market,                      # Target customers
                    business_model                      # Revenue model
                ]
                rows_to_add.append(row)

            # STEP 3: Write all data efficiently in a single batch operation
            if rows_to_add:
                worksheet.append_rows(rows_to_add)
                logger.info(f"Successfully wrote {len(rows_to_add)} summaries to '{sheet_name}'")

                # STEP 4: Apply professional formatting for optimal presentation
                self._format_worksheet(worksheet)
            else:
                logger.warning("No summaries to write to Google Sheets")

        except Exception as e:
            # Handle any errors during data writing with detailed logging
            logger.error(f"Error writing summaries to Google Sheets: {str(e)}")
            raise e

    def get_worksheet_url(self, worksheet_name: Optional[str] = None) -> str:
        """
        Generate the direct URL to the specified Google Sheets worksheet.

        This method creates a direct link to the results worksheet that can be
        shared with stakeholders for immediate access to the company summaries.
        The URL includes the specific worksheet tab for precise navigation.

        Args:
            worksheet_name (Optional[str]): Name of the worksheet to generate URL for.
                If None, defaults to the configured output worksheet name.

        Returns:
            str: Direct URL to the Google Sheets worksheet containing the results.
                Format: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={WORKSHEET_ID}
        """
        # Use provided worksheet name or fall back to default output worksheet
        sheet_name = worksheet_name or self.worksheet_name_output

        try:
            # STEP 1: Access the specific worksheet to get its unique ID
            worksheet = self.spreadsheet.worksheet(sheet_name)

            # STEP 2: Construct the direct URL with worksheet-specific anchor
            # This URL navigates directly to the results tab
            url = f"https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEETS_ID}/edit#gid={worksheet.id}"

            return url

        except Exception as e:
            # Log the error for debugging purposes
            logger.error(f"Error getting worksheet URL: {str(e)}")

            # Return fallback URL to main spreadsheet if worksheet-specific URL fails
            return f'https://docs.google.com/spreadsheets/d/{self.config.GOOGLE_SHEETS_ID}/edit'
