import unittest
from parser import parse_validate_sql, convert_to_relational_algebra
from plantando_arvores.processamento_consultas import processar, desenhar_arvore
from plantando_arvores.otimizador import otimizar
from plantando_arvores.arvore import NoArvore
from pathlib import Path
import io
import sys

# Helper to traverse and find nodes by operation prefix
def find_node_by_prefix(node, prefix):
    if node.operacao.startswith(prefix):
        return node
    for filho in getattr(node, 'filhos', []):
        found = find_node_by_prefix(filho, prefix)
        if found:
            return found
    return None

def get_all_nodes(node):
    nodes = [node]
    for filho in getattr(node, 'filhos', []):
        nodes.extend(get_all_nodes(filho))
    return nodes

def print_tree(node, indent=0, out=None):
    line = '  ' * indent + f"{node.operacao}\n"
    if out is not None:
        out.write(line)
    else:
        print(line, end='')
    for filho in getattr(node, 'filhos', []):
        print_tree(filho, indent + 1, out=out)

def save_tree_image(node, filename):
    dot = desenhar_arvore(node)
    out_path = Path('tests/graphviz_outputs')
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / filename
    dot.render(str(file_path), format='png', cleanup=True)
    return str(file_path.with_suffix('.png'))

# --- Expected tree builders ---
def build_expected_selection_and_projection_tree():
    root = NoArvore("𝝿 cliente.nome, cliente.email")
    sigma = NoArvore("𝛔 cliente.tipocliente_idtipocliente = 1")
    leaf = NoArvore("cliente[cliente]")
    sigma.adicionar_filho(leaf)
    root.adicionar_filho(sigma)
    return root

def build_expected_join_with_selection_on_both_sides_tree():
    root = NoArvore("𝝿 c.nome, p.datapedido")
    join = NoArvore("⨝")
    sigma_c = NoArvore("𝛔 c.tipocliente_idtipocliente = 1")
    sigma_p = NoArvore("𝛔 p.valortotalpedido > 100")
    leaf_c = NoArvore("cliente[c]")
    leaf_p = NoArvore("pedido[p]")
    sigma_c.adicionar_filho(leaf_c)
    sigma_p.adicionar_filho(leaf_p)
    join.adicionar_filho(sigma_c)
    join.adicionar_filho(sigma_p)
    root.adicionar_filho(join)
    return root

def build_expected_projection_pushdown_tree():
    root = NoArvore("𝝿 c.nome")
    join = NoArvore("⨝")
    proj_c = NoArvore("𝝿 c.nome, c.idcliente")
    sigma_p = NoArvore("𝛔 p.status_idstatus = 1")
    proj_p = NoArvore("𝝿 p.cliente_idcliente, p.status_idstatus")
    leaf_c = NoArvore("cliente[c]")
    leaf_p = NoArvore("pedido[p]")
    proj_c.adicionar_filho(leaf_c)
    proj_p.adicionar_filho(leaf_p)
    sigma_p.adicionar_filho(proj_p)
    join.adicionar_filho(proj_c)
    join.adicionar_filho(sigma_p)
    root.adicionar_filho(join)
    return root

def build_expected_multi_condition_selection_tree():
    root = NoArvore("𝝿 cliente.nome")
    sigma = NoArvore("𝛔 cliente.tipocliente_idtipocliente = 2 ∧ cliente.email = 'user@example.com'")
    leaf = NoArvore("cliente[cliente]")
    sigma.adicionar_filho(leaf)
    root.adicionar_filho(sigma)
    return root

# --- Markdown report helpers ---
REPORT_PATH = Path('TEST_REPORT.md')
def start_report():
    with REPORT_PATH.open('w', encoding='utf-8') as f:
        f.write('# Query Processor Test Report\n\n')

def append_report(section_md):
    with REPORT_PATH.open('a', encoding='utf-8') as f:
        f.write(section_md)

class TestAlgebraAndOptimization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        start_report()

    def clean_algebra_string(self, s):
        # Remove extra spaces, normalize parentheses, and strip
        s = s.strip()
        # Remove redundant outer parentheses
        while s.startswith('(') and s.endswith(')'):
            inner = s[1:-1].strip()
            # Only remove if parentheses are balanced
            if inner.count('(') == inner.count(')'):
                s = inner
            else:
                break
        return s

    def compare_trees(self, node1, node2, path="root"):
        """
        Recursively compare two NoArvore trees. Returns (True, "") if equal, else (False, reason).
        """
        if node1.operacao != node2.operacao:
            return False, f"Mismatch at {path}: '{node1.operacao}' != '{node2.operacao}'"
        if len(node1.filhos) != len(node2.filhos):
            return False, f"Mismatch in number of children at {path}: {len(node1.filhos)} != {len(node2.filhos)}"
        for i, (f1, f2) in enumerate(zip(node1.filhos, node2.filhos)):
            eq, reason = self.compare_trees(f1, f2, path + f" -> child[{i}]")
            if not eq:
                return False, reason
        return True, ""

    def run_test_with_report(self, test_name, description, sql, build_expected_tree_fn):
        section = f'## Test: {test_name}\n\n**Description:** {description}\n\n**SQL:**\n```\n{sql}\n```\n'
        debug_output = io.StringIO()
        try:
            parsed = parse_validate_sql(sql)
            ra = convert_to_relational_algebra(parsed)
            print(f"[DEBUG] Relational Algebra for '{test_name}':", ra, file=debug_output)
            ra_clean = self.clean_algebra_string(ra)
            print(f"[DEBUG] Cleaned Relational Algebra for '{test_name}':", ra_clean, file=debug_output)
            tree = processar(ra_clean)
            opt_tree = otimizar(tree)
            expected = build_expected_tree_fn()

            print(f"[DEBUG] Actual tree root: {opt_tree.operacao}", file=debug_output)
            print(f"[DEBUG] Expected tree root: {expected.operacao}", file=debug_output)

            # Save images
            img_initial = save_tree_image(tree, f'{test_name}_initial')
            img_optimized = save_tree_image(opt_tree, f'{test_name}_optimized')
            img_expected = save_tree_image(expected, f'{test_name}_expected')

            # Capture tree structures
            buf_init = io.StringIO()
            print_tree(tree, out=buf_init)
            buf_opt = io.StringIO()
            print_tree(opt_tree, out=buf_opt)
            buf_exp = io.StringIO()
            print_tree(expected, out=buf_exp)

            section += f'**Initial Tree:**\n![Initial]({img_initial})\n\n'
            section += f'**Optimized Tree:**\n![Optimized]({img_optimized})\n\n'
            section += f'**Expected Tree:**\n![Expected]({img_expected})\n\n'
            section += '**Initial Tree Structure:**\n```\n' + buf_init.getvalue() + '```\n'
            section += '**Optimized Tree Structure:**\n```\n' + buf_opt.getvalue() + '```\n'
            section += '**Expected Tree Structure:**\n```\n' + buf_exp.getvalue() + '```\n'

            # Robust tree comparison
            eq, reason = self.compare_trees(opt_tree, expected)
            if eq:
                section += '**Result:** ✅ PASS\n\n---\n\n'
            else:
                section += f'**Result:** ❌ FAIL\n\n**Tree Difference:** {reason}\n\n---\n\n'
        except Exception as e:
            section += f'**Result:** ❌ FAIL\n\n**Error:** {e}\n\n---\n\n'
        section += '\n**Debug Output:**\n```\n' + debug_output.getvalue() + '\n```\n'
        append_report(section)

    def test_selection_and_projection(self):
        self.run_test_with_report(
            test_name='selection_and_projection',
            description='Tests selection pushdown and projection.',
            sql="SELECT Nome, Email FROM Cliente WHERE TipoCliente_idTipoCliente = 1",
            build_expected_tree_fn=build_expected_selection_and_projection_tree
        )

    def test_join_with_selection_on_both_sides(self):
        self.run_test_with_report(
            test_name='join_with_selection_on_both_sides',
            description='Tests join with selection on both tables and join predicate.',
            sql=("SELECT C.Nome, P.DataPedido FROM Cliente C "
                 "INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente "
                 "WHERE C.TipoCliente_idTipoCliente = 1 AND P.ValorTotalPedido > 100"),
            build_expected_tree_fn=build_expected_join_with_selection_on_both_sides_tree
        )

    def test_projection_pushdown(self):
        self.run_test_with_report(
            test_name='projection_pushdown',
            description='Tests projection pushdown in join context.',
            sql=("SELECT C.Nome FROM Cliente C "
                 "INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente "
                 "WHERE P.Status_idStatus = 1"),
            build_expected_tree_fn=build_expected_projection_pushdown_tree
        )

    def test_multi_condition_selection(self):
        self.run_test_with_report(
            test_name='multi_condition_selection',
            description='Tests multiple conditions in selection.',
            sql=("SELECT Nome FROM Cliente WHERE TipoCliente_idTipoCliente = 2 AND Email = 'user@example.com'"),
            build_expected_tree_fn=build_expected_multi_condition_selection_tree
        )

    def test_minimal_working_projection(self):
        """Minimal working test for processar with projection only."""
        test_name = 'minimal_working_projection'
        description = 'Directly tests processar with a simple projection.'
        ra = "𝝿[nome](cliente[cliente])"
        section = f'## Test: {test_name}\n\n**Description:** {description}\n\n**Algebra:**\n```\n{ra}\n```\n'
        debug_output = io.StringIO()
        try:
            print(f"[DEBUG] Algebraic input: {ra}", file=debug_output)
            tree = processar(ra)
            print(f"[DEBUG] Tree root: {tree.operacao}", file=debug_output)
            print(f"[DEBUG] Child root: {tree.filhos[0].operacao}", file=debug_output)
            section += '**Tree Structure:**\n```\n'
            buf = io.StringIO()
            print_tree(tree, out=buf)
            section += buf.getvalue() + '```\n'
            if tree.operacao == "𝝿 nome" and tree.filhos[0].operacao == "cliente[cliente]":
                section += '**Result:** ✅ PASS\n\n---\n\n'
            else:
                section += f'**Result:** ❌ FAIL\n\n**Tree root:** {tree.operacao}, **Child:** {tree.filhos[0].operacao}\n\n---\n\n'
        except Exception as e:
            section += f'**Result:** ❌ FAIL\n\n**Error:** {e}\n\n---\n\n'
        section += '\n**Debug Output:**\n```\n' + debug_output.getvalue() + '\n```\n'
        append_report(section)

    def test_minimal_selection(self):
        """Minimal working selection with qualified attribute"""
        ra = "𝛔[cliente.idade > 18](cliente[cliente])"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "𝛔 cliente.idade > 18")
        self.assertEqual(tree.filhos[0].operacao, "cliente[cliente]")

    def test_minimal_join(self):
        """Minimal working join with qualified attributes"""
        ra = "⨝(cliente[cliente], pedido[pedido])"
        tree = processar(ra)
        self.assertEqual(tree.operacao, "⨝")
        self.assertEqual(tree.filhos[0].operacao, "cliente[cliente]")
        self.assertEqual(tree.filhos[1].operacao, "pedido[pedido]")

if __name__ == '__main__':
    unittest.main() 