import unittest
import logging
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_validate_sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/parser_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load queries from file
        cls.should_pass = []
        cls.should_fail = []
        path = Path('docs/exemplos_consultas.txt')
        current = None
        with path.open(encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('---------'): # Section header or empty
                    if 'SEM ERRO' in line:
                        current = cls.should_pass
                    elif 'COM ERRO' in line:
                        current = cls.should_fail
                    continue
                if current is not None:
                    current.append(line)
        Path('tests/logs').mkdir(parents=True, exist_ok=True)

    def setUp(self):
        logger.info(f"Starting test: {self._testMethodName}")
    def tearDown(self):
        logger.info(f"Completed test: {self._testMethodName}")

    def test_queries_should_pass(self):
        for query in self.should_pass:
            with self.subTest(query=query):
                try:
                    result = parse_validate_sql(query)
                    self.assertIsNotNone(result)
                    logger.info(f"Accepted as expected: {query}")
                except Exception as e:
                    logger.error(f"Unexpected error for valid query: {query} | {e}")
                    self.fail(f"Query should have been accepted but failed: {query} | {e}")

    def test_queries_should_fail(self):
        for query in self.should_fail:
            with self.subTest(query=query):
                with self.assertRaises(Exception):
                    parse_validate_sql(query)
                logger.info(f"Rejected as expected: {query}")

if __name__ == '__main__':
    unittest.main() 