# Query Processor Test Report

## Test: join_with_selection_on_both_sides

**Description:** Tests join with selection on both tables and join predicate.

**SQL:**
```
SELECT C.Nome, P.DataPedido FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE C.TipoCliente_idTipoCliente = 1 AND P.ValorTotalPedido > 100
```
**Result:** ❌ FAIL

**Error:** maximum recursion depth exceeded

---


**Debug Output:**
```
[DEBUG] Relational Algebra for 'join_with_selection_on_both_sides': 𝝿[c.nome, p.datapedido](𝛔[c.tipocliente_idtipocliente = 1 ∧ p.valortotalpedido > 100 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))
[DEBUG] Cleaned Relational Algebra for 'join_with_selection_on_both_sides': 𝝿[c.nome, p.datapedido](𝛔[c.tipocliente_idtipocliente = 1 ∧ p.valortotalpedido > 100 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))

```
## Test: minimal_working_projection

**Description:** Directly tests processar with a simple projection.

**Algebra:**
```
𝝿[nome](cliente[cliente])
```
**Tree Structure:**
```
𝝿 nome
  cliente[cliente]
```
**Result:** ✅ PASS

---


**Debug Output:**
```
[DEBUG] Algebraic input: 𝝿[nome](cliente[cliente])
[DEBUG] Tree root: 𝝿 nome
[DEBUG] Child root: cliente[cliente]

```
## Test: multi_condition_selection

**Description:** Tests multiple conditions in selection.

**SQL:**
```
SELECT Nome FROM Cliente WHERE TipoCliente_idTipoCliente = 2 AND Email = 'user@example.com'
```
**Result:** ❌ FAIL

**Error:** maximum recursion depth exceeded

---


**Debug Output:**
```
[DEBUG] Relational Algebra for 'multi_condition_selection': 𝝿[cliente.nome](𝛔[cliente.tipocliente_idtipocliente = 2 ∧ cliente.email = 'user@example.com'](cliente[cliente]))
[DEBUG] Cleaned Relational Algebra for 'multi_condition_selection': 𝝿[cliente.nome](𝛔[cliente.tipocliente_idtipocliente = 2 ∧ cliente.email = 'user@example.com'](cliente[cliente]))

```
## Test: projection_pushdown

**Description:** Tests projection pushdown in join context.

**SQL:**
```
SELECT C.Nome FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE P.Status_idStatus = 1
```
**Result:** ❌ FAIL

**Error:** maximum recursion depth exceeded

---


**Debug Output:**
```
[DEBUG] Relational Algebra for 'projection_pushdown': 𝝿[c.nome](𝛔[p.status_idstatus = 1 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))
[DEBUG] Cleaned Relational Algebra for 'projection_pushdown': 𝝿[c.nome](𝛔[p.status_idstatus = 1 ∧ c.idcliente = p.cliente_idcliente]((cliente[c] ⨝ pedido[p])))

```
## Test: selection_and_projection

**Description:** Tests selection pushdown and projection.

**SQL:**
```
SELECT Nome, Email FROM Cliente WHERE TipoCliente_idTipoCliente = 1
```
**Initial Tree:**
![Initial](tests\graphviz_outputs\selection_and_projection_initial.png)

**Optimized Tree:**
![Optimized](tests\graphviz_outputs\selection_and_projection_optimized.png)

**Expected Tree:**
![Expected](tests\graphviz_outputs\selection_and_projection_expected.png)

**Initial Tree Structure:**
```
𝝿 cliente.nome, cliente.email
  𝛔 cliente.tipocliente_idtipocliente = 1
    cliente[cliente]
```
**Optimized Tree Structure:**
```
𝝿 cliente.nome, cliente.email
  𝛔 cliente.tipocliente_idtipocliente = 1
    cliente[cliente]
```
**Expected Tree Structure:**
```
𝝿 cliente.nome, cliente.email
  𝛔 cliente.tipocliente_idtipocliente = 1
    cliente[cliente]
```
**Result:** ✅ PASS

---


**Debug Output:**
```
[DEBUG] Relational Algebra for 'selection_and_projection': 𝝿[cliente.nome, cliente.email](𝛔[cliente.tipocliente_idtipocliente = 1](cliente[cliente]))
[DEBUG] Cleaned Relational Algebra for 'selection_and_projection': 𝝿[cliente.nome, cliente.email](𝛔[cliente.tipocliente_idtipocliente = 1](cliente[cliente]))
[DEBUG] Actual tree root: 𝝿 cliente.nome, cliente.email
[DEBUG] Expected tree root: 𝝿 cliente.nome, cliente.email

```
