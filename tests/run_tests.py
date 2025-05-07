import unittest
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import json

# Create logs directory if it doesn't exist
Path('tests/logs').mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/test_run.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestResultCollector(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.test_results = []
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results.append({
            'test': str(test),
            'status': 'PASS',
            'error': None
        })
        
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append({
            'test': str(test),
            'status': 'FAIL',
            'error': str(err[1])
        })
        
    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append({
            'test': str(test),
            'status': 'ERROR',
            'error': str(err[1])
        })

def run_tests():
    """Run all tests and generate a comprehensive report"""
    # Start test run
    start_time = datetime.now()
    logger.info(f"Starting test run at {start_time}")
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Create custom result collector
    result_collector = TestResultCollector()
    
    # Run tests
    test_suite.run(result_collector)
    
    # End test run
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Generate report
    report = {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration': str(duration),
        'total_tests': len(result_collector.test_results),
        'passed_tests': len([r for r in result_collector.test_results if r['status'] == 'PASS']),
        'failed_tests': len([r for r in result_collector.test_results if r['status'] == 'FAIL']),
        'error_tests': len([r for r in result_collector.test_results if r['status'] == 'ERROR']),
        'test_results': result_collector.test_results
    }
    
    # Save report to file
    report_file = f'tests/logs/test_report_{start_time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Log summary
    logger.info(f"Test run completed in {duration}")
    logger.info(f"Total tests: {report['total_tests']}")
    logger.info(f"Passed: {report['passed_tests']}")
    logger.info(f"Failed: {report['failed_tests']}")
    logger.info(f"Errors: {report['error_tests']}")
    logger.info(f"Detailed report saved to: {report_file}")
    
    # Return non-zero exit code if any tests failed
    return 1 if (report['failed_tests'] > 0 or report['error_tests'] > 0) else 0

if __name__ == '__main__':
    sys.exit(run_tests()) 