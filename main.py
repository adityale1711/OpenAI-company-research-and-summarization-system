import time
from src.company_research_and_summarization_system import logger
from src.company_research_and_summarization_system.pipelines.input_pipeline import InputPipeline


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
        input_pipeline = InputPipeline()
        companies = input_pipeline.run()
    except Exception as e:
        logger.error(f"An error occurred during the workflow execution: {str(e)}")
        workflow_results['status'] = 'failed'
        workflow_results['errors'].append(str(e))
        workflow_results['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        workflow_results['duration'] = f'{(time.time() - start_time):.2f} seconds'


if __name__ == "__main__":
    main()