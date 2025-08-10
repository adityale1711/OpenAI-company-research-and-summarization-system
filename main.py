import time
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.pipelines.input_pipeline import InputPipeline
from src.company_research_and_summarization_system.pipelines.generate_pipeline import GeneratePipeline


def progress_callback(current: int, total: int, company_name: str):
    """
    Callback function to report progress during the summarization process.

    Args:
        current (int): Current company index being processed
        total (int): Total number of companies to process
        company_name (str): Name of the company currently being processed
    """
    progress = (current / total) * 100
    logger.info(f"Processing {current}/{total}: ({progress:.1f}%) - Processed: {company_name})")


def main():
    start_time = time.time()
    logger.info("Starting the company research and summarization system...")

    workflow_results = {
        'status': 'started',
        'companies_processed': 0,
        'successful_summaries': 0,
        'failed_summaries': 0,
        'warnings': 0,
        'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': None,
        'duration': None,
        'output_url': None,
        'errors': []
    }

    try:
        # Initialize the input pipeline to retrieve company data
        input_pipeline = InputPipeline()
        companies = input_pipeline.run()

        if not companies:
            logger.warning("No companies found in the input pipeline.")
            workflow_results['status'] = 'no_companies'
            workflow_results['errors'].append('No companies found in the input pipeline.')

            return workflow_results

        # Generate summaries using OpenAI
        summaries = GeneratePipeline(companies, progress_callback)
        summaries = summaries.run()

        # Analyze results
        for summary in summaries:
            status = summary.get('status', 'unknown')
            if status == 'success':
                workflow_results['successful_summaries'] += 1
            elif status == 'warning':
                workflow_results['warnings'] += 1
            else:
                workflow_results['failed_summaries'] += 1
    except Exception as e:
        logger.error(f"An error occurred during the workflow execution: {str(e)}")
        workflow_results['status'] = 'failed'
        workflow_results['errors'].append(str(e))
        workflow_results['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        workflow_results['duration'] = f'{(time.time() - start_time):.2f} seconds'


if __name__ == "__main__":
    main()