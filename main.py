import sys
import time

from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.pipelines.input_pipeline import InputPipeline
from src.company_research_and_summarization_system.pipelines.output_pipeline import OutputPipeline
from src.company_research_and_summarization_system.pipelines.generate_pipeline import GeneratePipeline


def progress_callback(current: int, total: int, company_name: str):
    """
    Callback function to report real-time progress during the batch summarization process.

    This function provides user feedback and logging for long-running batch operations,
    helping users understand the current processing status and estimated completion time.

    Args:
        current (int): Current company index being processed (1-based indexing)
        total (int): Total number of companies to process in the batch
        company_name (str): Name of the company currently being processed
    """
    # Calculate completion percentage for user feedback
    progress = (current / total) * 100
    logger.info(f"Processing {current}/{total}: ({progress:.1f}%) - Processed: {company_name})")


def main():
    """
    Main execution function that orchestrates the entire company research and summarization workflow.

    This function implements a comprehensive pipeline that:
    1. Initializes system components and tracking variables
    2. Executes the three-stage pipeline (Input → Generate → Output)
    3. Handles errors gracefully with detailed logging
    4. Provides comprehensive workflow statistics
    5. Returns appropriate exit codes for system integration

    Workflow Stages:
        Input Pipeline: Retrieves company list from Google Sheets
        Generate Pipeline: Creates AI-powered summaries using OpenAI
        Output Pipeline: Writes results back to Google Sheets

    Returns:
        int: Exit code (0 for success, 1 for failure) for system integration

    Raises:
        Exception: Re-raises any critical errors after logging for debugging
    """
    # Record start time for performance tracking
    start_time = time.time()
    logger.info("Starting the company research and summarization system...")

    # Initialize comprehensive workflow tracking dictionary
    # This tracks all aspects of the workflow for reporting and debugging
    workflow_results = {
        'status': 'started',                                # Current workflow status
        'companies_processed': 0,                           # Total companies attempted
        'successful_summaries': 0,                          # Successfully generated summaries
        'failed_summaries': 0,                              # Failed summary generations
        'warnings': 0,                                      # Non-critical issues encountered
        'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),   # Human-readable start time
        'end_time': None,                                   # Will be set upon completion
        'duration': None,                                   # Total execution time
        'output_url': None,                                 # URL to access results
        'errors': []                                        # List of error messages for debugging
    }

    try:
        # STAGE 1: INPUT PIPELINE
        # Initialize the input pipeline to retrieve company data from Google Sheets
        logger.info("Initializing Input Pipeline...")
        input_pipeline = InputPipeline()
        companies = input_pipeline.run()

        # Validate that companies were successfully retrieved
        if not companies:
            logger.warning("No companies found in the input pipeline.")
            workflow_results['status'] = 'no_companies'
            workflow_results['errors'].append('No companies found in the input pipeline.')
            return workflow_results

        # Update tracking with number of companies to process
        workflow_results['companies_processed'] = len(companies)
        logger.info(f"Successfully loaded {len(companies)} companies for processing")

        # STAGE 2: GENERATE PIPELINE
        # Generate comprehensive summaries using OpenAI's models
        logger.info("Initializing Generate Pipeline...")
        summaries = GeneratePipeline(companies, progress_callback)
        summaries = summaries.run()

        # STAGE 3: RESULT ANALYSIS
        # Analyze the results to categorize success, warnings, and failures
        logger.info("Analyzing generation results...")
        for summary in summaries:
            status = summary.get('status', 'unknown')
            if status == 'success':
                workflow_results['successful_summaries'] += 1
            elif status == 'warning':
                workflow_results['warnings'] += 1
            else:
                workflow_results['failed_summaries'] += 1

        # STAGE 4: OUTPUT PIPELINE
        # Write the generated summaries to Google Sheets for easy access and sharing
        logger.info("Initializing Output Pipeline...")
        output_pipeline = OutputPipeline(summaries)
        output_url = output_pipeline.run()

        # Store the output URL for user access
        workflow_results['output_url'] = output_url

        # STAGE 5: WORKFLOW COMPLETION
        # Calculate final metrics and prepare comprehensive results
        end_time = time.time()
        workflow_results['status'] = 'completed'
        workflow_results['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        workflow_results['duration'] = f'{(end_time - start_time):.2f} seconds'

        logger.info('Workflow completed successfully.')

        # STAGE 6: RESULTS PRESENTATION
        # Display comprehensive workflow results to the user
        print("\n📊 Workflow Results:")
        print(f"Status: {workflow_results['status']}")
        print(f"Companies Processed: {workflow_results['companies_processed']}")
        print(f"Successful Summaries: {workflow_results['successful_summaries']}")
        print(f"Failed Summaries: {workflow_results['failed_summaries']}")
        print(f"Warnings: {workflow_results['warnings']}")
        print(f"Duration: {workflow_results['duration']}")

        # Provide direct link to results if available
        if workflow_results['output_url']:
            print(f"\n🎯 Results available at: {workflow_results['output_url']}")

        # Return appropriate status based on workflow completion
        if workflow_results['status'] == 'completed':
            print("\n✅ Workflow completed successfully!")
            return 0
        else:
            print(f"\n❌ Workflow failed: {', '.join(workflow_results['errors'])}")
            return 1

    except KeyboardInterrupt:
        # Handle graceful shutdown on user interruption
        print("\n⚠️  Operation cancelled by user")
        logger.info("Workflow cancelled by user (KeyboardInterrupt)")
        return 1

    except Exception as e:
        # Handle any unexpected errors with comprehensive logging
        logger.error(f"An error occurred during the workflow execution: {str(e)}")
        workflow_results['status'] = 'failed'
        workflow_results['errors'].append(str(e))
        workflow_results['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        workflow_results['duration'] = f'{(time.time() - start_time):.2f} seconds'

        print(f"\n❌ Critical error: {str(e)}")
        logger.error(f"Critical error in main: {str(e)}")
        return 1


if __name__ == "__main__":
    """
    Entry point for the application when run as a script.
    
    This section ensures the application can be run directly and provides
    proper exit codes for system integration and automation purposes.
    """
    exit_code = main()
    sys.exit(exit_code)
