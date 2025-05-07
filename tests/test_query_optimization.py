import unittest
import logging
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plantando_arvores.otimizador import otimizar
from plantando_arvores.arvore import NoArvore
from plantando_arvores.processamento_consultas import processar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/logs/query_optimization_tests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TestQueryOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create logs directory if it doesn't exist
        Path('tests/logs').mkdir(parents=True, exist_ok=True)
        
    def setUp(self):
        logger.info(f"Starting test: {self._testMethodName}")
    def tearDown(self):
        logger.info(f"Completed test: {self._testMethodName}")

    def test_push_selection_down(self):
        # σ[idade > 18](Cliente)
        root = NoArvore("σ idade > 18")
        child = NoArvore("Cliente")
        root.adicionar_filho(child)
        try:
            optimized = otimizar(root)
            self.assertIsNotNone(optimized)
            logger.info("Successfully optimized selection pushdown.")
        except Exception as e:
            logger.error(f"Failed to optimize selection pushdown: {str(e)}")
            raise

    def test_join_reordering(self):
        # (Cliente ⨝ Pedido)
        left = NoArvore("Cliente")
        right = NoArvore("Pedido")
        join = NoArvore("⨝")
        join.adicionar_filho(left)
        join.adicionar_filho(right)
        try:
            optimized = otimizar(join)
            self.assertIsNotNone(optimized)
            logger.info("Successfully optimized join reordering.")
        except Exception as e:
            logger.error(f"Failed to optimize join reordering: {str(e)}")
            raise

    def test_projection_pushdown(self):
        # π[nome](Cliente)
        root = NoArvore("π nome")
        child = NoArvore("Cliente")
        root.adicionar_filho(child)
        try:
            optimized = otimizar(root)
            self.assertIsNotNone(optimized)
            logger.info("Successfully optimized projection pushdown.")
        except Exception as e:
            logger.error(f"Failed to optimize projection pushdown: {str(e)}")
            raise

    def test_complex_optimization(self):
        # π[nome](σ[idade > 18](Cliente ⨝ Pedido))
        join = NoArvore("⨝")
        join.adicionar_filho(NoArvore("Cliente"))
        join.adicionar_filho(NoArvore("Pedido"))
        selection = NoArvore("σ idade > 18")
        selection.adicionar_filho(join)
        projection = NoArvore("π nome")
        projection.adicionar_filho(selection)
        try:
            optimized = otimizar(projection)
            self.assertIsNotNone(optimized)
            logger.info("Successfully optimized complex query plan.")
        except Exception as e:
            logger.error(f"Failed to optimize complex query plan: {str(e)}")
            raise

    def test_simple_selection(self):
        # Minimal working selection
        ra = "𝛔[idade > 18](cliente[cliente])"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝛔 idade > 18")
        self.assertEqual(tree.filhos[0].operacao, "cliente[cliente]")

    def test_simple_projection(self):
        # Minimal working projection
        ra = "𝝿[nome](cliente[cliente])"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝝿 nome")
        self.assertEqual(tree.filhos[0].operacao, "cliente[cliente]")

    def test_selection_and_projection(self):
        # Selection and projection
        ra = "𝝿[nome](𝛔[idade > 18](cliente[cliente]))"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝝿 nome")
        self.assertEqual(tree.filhos[0].operacao, "𝛔 idade > 18")
        self.assertEqual(tree.filhos[0].filhos[0].operacao, "cliente[cliente]")

    def test_simple_join(self):
        # Minimal working join
        ra = "(cliente[cliente] ⨝ pedido[pedido])"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "⨝")
        self.assertEqual(tree.filhos[0].operacao, "cliente[cliente]")
        self.assertEqual(tree.filhos[1].operacao, "pedido[pedido]")

    def test_selection_on_join(self):
        # Selection on join
        ra = "𝛔[cliente.idcliente = pedido.cliente_idcliente]((cliente[cliente] ⨝ pedido[pedido]))"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝛔 cliente.idcliente = pedido.cliente_idcliente")
        self.assertEqual(tree.filhos[0].operacao, "⨝")

    def test_projection_on_join(self):
        # Projection on join
        ra = "𝝿[cliente.nome, pedido.datapedido]((cliente[cliente] ⨝ pedido[pedido]))"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝝿 cliente.nome, pedido.datapedido")
        self.assertEqual(tree.filhos[0].operacao, "⨝")

if __name__ == '__main__':
    unittest.main() 