import unittest
import logging
from pathlib import Path
import sys
import os
from parser import parse_validate_sql, convert_to_relational_algebra
from plantando_arvores.processamento_consultas import processar
from plantando_arvores.otimizador import otimizar

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plantando_arvores.processamento_consultas import desenhar_arvore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/graph_construction_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestGraphConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create logs directory if it doesn't exist
        Path('tests/logs').mkdir(parents=True, exist_ok=True)
        
    def setUp(self):
        logger.info(f"Starting test: {self._testMethodName}")
    def tearDown(self):
        logger.info(f"Completed test: {self._testMethodName}")

    def test_simple_query_graph(self):
        query = "𝝿[nome](Cliente)"
        try:
            node = processar(query)
            graph = desenhar_arvore(node)
            self.assertIsNotNone(graph)
            logger.info(f"Successfully constructed graph for simple query: {query}")
        except Exception as e:
            logger.error(f"Failed to construct graph for simple query: {str(e)}")
            raise

    def test_join_query_graph(self):
        query = "(Cliente[C] ⨝ Pedido[P])"
        try:
            node = processar(query)
            graph = desenhar_arvore(node)
            self.assertIsNotNone(graph)
            logger.info(f"Successfully constructed graph for join query: {query}")
        except Exception as e:
            logger.error(f"Failed to construct graph for join query: {str(e)}")
            raise

    def test_aggregation_query_graph(self):
        # Not directly supported in algebra, so we use a projection
        query = "𝝿[Cliente.Nome](Cliente)"
        try:
            node = processar(query)
            graph = desenhar_arvore(node)
            self.assertIsNotNone(graph)
            logger.info(f"Successfully constructed graph for aggregation-like query: {query}")
        except Exception as e:
            logger.error(f"Failed to construct graph for aggregation-like query: {str(e)}")
            raise

    def test_complex_query_graph(self):
        query = "𝝿[C.Nome, P.DataPedido]( (Cliente[C] ⨝ Pedido[P]) )"
        try:
            node = processar(query)
            graph = desenhar_arvore(node)
            self.assertIsNotNone(graph)
            logger.info(f"Successfully constructed graph for complex query: {query}")
        except Exception as e:
            logger.error(f"Failed to construct graph for complex query: {str(e)}")
            raise

class TestAlgebraAndOptimization(unittest.TestCase):
    def test_selection_and_projection(self):
        sql = "SELECT Nome, Email FROM Cliente WHERE Cidade = 'Fortaleza'"
        parsed = parse_validate_sql(sql)
        ra = convert_to_relational_algebra(parsed)
        tree = processar(ra)
        # Check initial tree structure
        self.assertTrue(tree.operacao.startswith("π"))
        self.assertTrue(tree.filhos[0].operacao.startswith("σ"))
        self.assertIn("Cidade = 'Fortaleza'", tree.filhos[0].operacao)
        self.assertEqual(tree.filhos[0].filhos[0].operacao, "Cliente")
        # Now optimize and check structure remains the same (already optimal)
        opt_tree = otimizar(tree)
        self.assertEqual(opt_tree.operacao, tree.operacao)
        self.assertEqual(opt_tree.filhos[0].operacao, tree.filhos[0].operacao)

if __name__ == '__main__':
    unittest.main() 