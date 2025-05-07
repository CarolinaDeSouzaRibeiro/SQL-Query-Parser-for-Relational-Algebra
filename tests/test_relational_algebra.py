import unittest
import logging
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plantando_arvores.processamento_consultas import processar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/relational_algebra_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestRelationalAlgebra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create logs directory if it doesn't exist
        Path('tests/logs').mkdir(parents=True, exist_ok=True)
        
    def setUp(self):
        logger.info(f"Starting test: {self._testMethodName}")
    def tearDown(self):
        logger.info(f"Completed test: {self._testMethodName}")

    def test_simple_projection(self):
        query = "𝝿[nome](Cliente)"
        try:
            result = processar(query)
            self.assertIsNotNone(result)
            logger.info(f"Successfully processed simple projection: {query}")
        except Exception as e:
            logger.error(f"Failed to process simple projection: {str(e)}")
            raise

    def test_selection(self):
        query = "𝛔[idade > 18](Cliente)"
        try:
            result = processar(query)
            self.assertIsNotNone(result)
            logger.info(f"Successfully processed selection: {query}")
        except Exception as e:
            logger.error(f"Failed to process selection: {str(e)}")
            raise

    def test_join(self):
        query = "(Cliente[C] ⨝ Pedido[P])"
        try:
            result = processar(query)
            self.assertIsNotNone(result)
            logger.info(f"Successfully processed join: {query}")
        except Exception as e:
            logger.error(f"Failed to process join: {str(e)}")
            raise

    def test_complex_query(self):
        query = "𝝿[C.Nome, P.DataPedido]( (Cliente[C] ⨝ Pedido[P]) )"
        try:
            result = processar(query)
            self.assertIsNotNone(result)
            logger.info(f"Successfully processed complex query: {query}")
        except Exception as e:
            logger.error(f"Failed to process complex query: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 