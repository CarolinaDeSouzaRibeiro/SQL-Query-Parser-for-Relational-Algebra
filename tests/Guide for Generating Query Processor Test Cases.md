# **Guide for Generating Standardized Test Cases for a Query Processor**

**Version:** 2.0 **Target Audience:** AI Agent for Test Case Elaboration **Based on:** "Projeto 2 \- Processador de Consultas 24.2 (1).pdf" and general database principles.

## **1\. Introduction**

This document outlines the core concepts of relational algebra, query representation as graphs (query trees), and query optimization heuristics. The primary goal is to equip an AI agent with the necessary knowledge to generate comprehensive and standardized test cases for a query processor. These test cases will validate the parser, query graph generator, optimization logic, and overall correctness of the query processor as per the specifications in the "Projeto 2 \- Processador de Consultas 24.2 (1).pdf" (referred to as "the assignment PDF").

All examples and test cases should strictly adhere to the database schema provided in the assignment PDF (pages 2-6, including tables like `Cliente`, `Pedido`, `Produto`, `Endereco`, `Categoria`, `pedido_has_produto`, `TipoCliente`, `Status`, etc.) and the supported SQL syntax.

**Supported SQL (as per assignment PDF):**

* Clauses: `SELECT`, `FROM`, `WHERE`, `INNER JOIN`  
* Operators: `=`, `>`, `<`, `<=`, `>=`, `<>`, `AND`, `(`, `)`

## **2\. Relational Algebra Fundamentals**

Relational algebra is a formal system for manipulating relations (tables). SQL queries are often translated into relational algebra expressions for processing and optimization.

### **2.1. Core Relational Algebra Operations**

* **Selection ($\\sigma$)**  
    
  * **Purpose:** Filters tuples (rows) from a relation that satisfy a given predicate (condition).  
  * **Syntax:** $\\sigma\_{predicate}(Relation)$  
  * **SQL Equivalent:** `WHERE` clause.  
  * **Example (Assignment Schema):** Select all clients from the city 'Fortaleza'.  
    * SQL: `SELECT * FROM Cliente WHERE Cidade = 'Fortaleza';`  
    * Relational Algebra: $\\sigma\_{Cidade \= 'Fortaleza'}(Cliente)$


* **Projection ($\\pi$)**  
    
  * **Purpose:** Selects specific attributes (columns) from a relation, discarding others. Duplicate tuples in the result are eliminated.  
  * **Syntax:** $\\pi\_{attributeList}(Relation)$  
  * **SQL Equivalent:** The list of columns in the `SELECT` clause.  
  * **Example (Assignment Schema):** Get the name and email of all clients.  
    * SQL: `SELECT Nome, Email FROM Cliente;`  
    * Relational Algebra: $\\pi\_{Nome, Email}(Cliente)$


* **Cartesian Product ($\\times$)**  
    
  * **Purpose:** Combines every tuple from one relation with every tuple from another relation.  
  * **Syntax:** $Relation1 \\times Relation2$  
  * **Note:** This operation is computationally expensive and generally avoided in practice by using Joins. The query optimizer should aim to replace Cartesian products followed by selections with Join operations.  
  * **Example (Assignment Schema):** Combine all clients with all orders (conceptually, before a join condition).  
    * Relational Algebra: $Cliente \\times Pedido$


* **Rename ($\\rho$)**  
    
  * **Purpose:** Renames a relation and/or its attributes. Useful for self-joins or to avoid ambiguity.  
  * **Syntax:** $\\rho\_{NewName}(Relation)$ or $\\rho\_{NewName(attr1, attr2, ...)}(Relation)$  
  * **Example:** If we were joining `Cliente` to itself (not directly supported by the assignment's simple SQL, but for conceptual understanding).


* **Join ($\\bowtie$)**  
    
  * **Purpose:** Combines related tuples from two relations based on a specified join condition. The assignment specifically mentions `INNER JOIN`.  
  * **Inner Join Syntax (Theta Join):** $Relation1 \\bowtie\_{join\_predicate} Relation2$  
  * **SQL Equivalent:** `INNER JOIN ... ON ...`  
  * **Example (Assignment Schema):** Get client names and their order dates.  
    * SQL: `SELECT Cliente.Nome, Pedido.DataPedido FROM Cliente INNER JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente;`  
    * Relational Algebra: $Cliente \\bowtie\_{Cliente.idCliente \= Pedido.Cliente\_idCliente} Pedido$  
    * Often, this is combined with projection: $\\pi\_{Cliente.Nome, Pedido.DataPedido} (Cliente \\bowtie\_{Cliente.idCliente \= Pedido.Cliente\_idCliente} Pedido)$

## **3\. Representing Queries as Graphs (Query Trees)**

An SQL query is typically parsed and converted into an internal representation, often a **query tree** (also known as an operator tree or query evaluation plan). This tree visually represents the relational algebra expression.

* **Structure:**  
  * **Leaf Nodes:** Represent the base relations (tables from the database).  
  * **Internal Nodes:** Represent relational algebra operations. The children of an internal node are its operands.  
  * **Edges:** Indicate the flow of data (intermediate results) from child operations to parent operations. Predicates are associated with their respective operator nodes (e.g., selection condition with a $\\sigma$ node, join condition with a $\\bowtie$ node).

The assignment PDF (item 3.b) requires the "Geração do grafo de operadores da consulta," where nodes are operators/tables/constants, and edges show intermediate result flow and predicates.

**Example (Assignment Schema):**

* **SQL Query:** `SELECT Nome, Email FROM Cliente WHERE Cidade = 'Fortaleza' AND TipoCliente_idTipoCliente = 1;`  
    
* **Relational Algebra Expression:** $\\pi\_{Nome, Email} (\\sigma\_{Cidade \= 'Fortaleza' \\land TipoCliente\_idTipoCliente \= 1} (Cliente))$  
    
* **Query Tree (Unoptimized):**  
    
        $\\pi\_{Nome, Email}$  
    
             |  
    
  $\\sigma\_{Cidade \= 'Fortaleza' \\land TipoCliente\\\_idTipoCliente \= 1}$  
    
             |  
    
          Cliente

## **4\. Query Optimization**

Query optimization aims to transform a query (often its query tree representation) into an equivalent one that can be executed more efficiently, minimizing resource usage (CPU, I/O, time). The assignment focuses on heuristic-based optimization.

**Heuristics (as per assignment PDF, item 5):**

1. **Apply operations that reduce the size of intermediate results first:**  
     
   * **Push Selections Down ($\\sigma$):** Perform selection operations as early (as low in the tree) as possible. This reduces the number of tuples propagated to subsequent, more expensive operations like joins.  
     * Rule: $\\sigma\_{cond}(R \\bowtie S) \\equiv (\\sigma\_{cond}(R)) \\bowtie S$ (if `cond` only involves attributes of R)  
     * Rule: $\\sigma\_{cond1 \\land cond2}(R) \\equiv \\sigma\_{cond1}(\\sigma\_{cond2}(R))$ (Cascade of selections can be useful for pushing parts of a condition down).  
   * **Push Projections Down ($\\pi$):** Perform projection operations early to reduce the number of attributes (columns) in intermediate tuples. Only keep attributes needed for subsequent operations or the final result.  
     * Rule: $\\pi\_{attrs}(R \\bowtie S)$ can sometimes be $\\pi\_{attrs}( (\\pi\_{attrs\_R}(R)) \\bowtie (\\pi\_{attrs\_S}(S)) )$, where `attrs_R` and `attrs_S` are attributes from R and S needed for the join and final projection.

   

2. **Apply the most restrictive selections and joins first:**  
     
   * This involves reordering leaf nodes (tables) if it leads to more restrictive joins being performed earlier.  
   * If a selection significantly reduces the cardinality of a relation, it should be done before joining that relation.

   

3. **Avoid Cartesian Products:**  
     
   * A `FROM R, S WHERE R.id = S.id` type of query should be recognized as a join, not a full Cartesian product followed by a filter. The optimizer should ensure that join conditions are used to perform efficient join operations (e.g., transforming $\\sigma\_{join\_cond}(R \\times S)$ into $R \\bowtie\_{join\_cond} S$).

**Example of Optimization (Assignment Schema):**

* **SQL Query:** `SELECT C.Nome, P.ValorTotalPedido FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE C.Cidade = 'Sao Paulo' AND P.ValorTotalPedido >= 500;`  
    
* **Initial (Less Optimized) Query Tree:**  
    
                            $\\pi\_{C.Nome, P.ValorTotalPedido}$  
    
                                       |  
    
  $\\sigma\_{C.Cidade \= 'Sao Paulo' \\land P.ValorTotalPedido \>= 500}$  
    
                                       |  
    
                  $C \\bowtie\_{C.idCliente \= P.Cliente\\\_idCliente} P$  
    
                     /                             \\  
    
                 Cliente (C)                     Pedido (P)  
    
  (Note: Some systems might even put the join above the selection initially if parsing directly from SQL `WHERE` that includes join and filter conditions).  
    
* **Optimized Query Tree (Pushing Selections Down):**  
    
                            $\\pi\_{C.Nome, P.ValorTotalPedido}$  
    
                                       |  
    
                  $C \\bowtie\_{C.idCliente \= P.Cliente\\\_idCliente} P$  
    
                     /                             \\  
    
  $\\sigma\_{C.Cidade \= 'Sao Paulo'}$          $\\sigma\_{P.ValorTotalPedido \>= 500}$  
    
          |                                       |  
    
      Cliente (C)                             Pedido (P)  
    
  This optimized tree first filters `Cliente` and `Pedido` independently before joining them, reducing the number of tuples involved in the potentially expensive join operation.

## **5\. Guidelines for Generating Standardized Tests**

The AI agent should generate test cases to validate each component of the query processor. Each test case should ideally include:

* Test ID  
* Purpose of the test  
* Input SQL Query  
* Expected behavior/output (e.g., successful parse, specific error, specific query tree structure, specific optimized tree structure, expected execution order, or conceptual result set).

### **5.1. Parser Testing (SQL Syntax and Semantics)**

**Objective:** Ensure the parser correctly interprets valid SQL strings according to the assignment's limitations and rejects invalid ones.

* **Valid SQL Test Cases:**  
    
  * **Simple Select:** `SELECT Nome FROM Cliente;`  
  * **Select Multiple Columns:** `SELECT idCliente, Nome, Email FROM Cliente;`  
  * **Select All Columns (if `*` is implicitly supported or to be tested for rejection if not):** `SELECT * FROM Cliente;` (Clarify if `*` is parsed or if specific columns are always required).  
  * **Simple Where:** `SELECT Nome FROM Cliente WHERE Cidade = 'Fortaleza';`  
  * **Where with Different Operators:**  
    * `SELECT idProduto, Nome FROM Produto WHERE Preco > 100;`  
    * `SELECT idProduto, Nome FROM Produto WHERE QuantEstoque < 10;`  
    * `SELECT idPedido FROM Pedido WHERE ValorTotalPedido >= 50.75;`  
    * `SELECT idPedido FROM Pedido WHERE Status_idStatus <= 2;`  
    * `SELECT Nome FROM Cliente WHERE Nome <> 'Teste';`  
  * **Where with `AND`:** `SELECT Nome FROM Cliente WHERE Cidade = 'Fortaleza' AND TipoCliente_idTipoCliente = 1;`  
  * **Where with Parentheses:** `SELECT Nome FROM Cliente WHERE Cidade = 'Fortaleza' AND (TipoCliente_idTipoCliente = 1 AND DataRegistro > '2023-01-01');` (Note: `OR` is not in the specified operators, stick to `AND` and parentheses for precedence).  
  * **Simple Inner Join:** `SELECT Cliente.Nome, Pedido.idPedido FROM Cliente INNER JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente;`  
  * **Inner Join with Where:** `SELECT C.Nome, P.idPedido FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE C.Cidade = 'Fortaleza';`  
  * **Multi-Way Inner Join (if implied by grammar, though likely two tables at a time):** `SELECT C.Nome, PR.Nome, PHP.Quantidade FROM Cliente C INNER JOIN Pedido PE ON C.idCliente = PE.Cliente_idCliente INNER JOIN pedido_has_produto PHP ON PE.idPedido = PHP.Pedido_idPedido INNER JOIN Produto PR ON PHP.Produto_idProduto = PR.idProduto WHERE C.Nome = 'Ana';` (The parser might break this down into a sequence of binary joins).  
  * **Case Insensitivity (for keywords, table/column names if applicable \- clarify):** `select nome from cliente where cidade = 'Fortaleza';`  
  * **Whitespace Variations:** Queries with extra spaces, newlines.


* **Invalid SQL Test Cases (Expected: Parser Error/Rejection, Validation Message):**  
    
  * **Misspelled Keywords:** `SELEC Nome FROM Cliente;`, `FROMM Cliente;`  
  * **Unsupported Clauses:** `SELECT Nome FROM Cliente ORDER BY Nome;`, `SELECT Cidade, COUNT(*) FROM Cliente GROUP BY Cidade;`, `SELECT C.Nome FROM Cliente C LEFT JOIN Pedido P ON C.idCliente = P.Cliente_idCliente;`  
  * **Syntax Errors:**  
    * Missing comma: `SELECT Nome Email FROM Cliente;`  
    * Incomplete condition: `SELECT Nome FROM Cliente WHERE Cidade = ;`  
    * Unbalanced parentheses: `SELECT Nome FROM Cliente WHERE (Cidade = 'Fortaleza';`  
    * Missing `ON` clause for `INNER JOIN`: `SELECT Cliente.Nome FROM Cliente INNER JOIN Pedido;`  
    * Incorrect join condition syntax: `SELECT C.Nome FROM Cliente C INNER JOIN Pedido P WHERE C.idCliente = P.Cliente_idCliente;` (Using `WHERE` for join condition instead of `ON`).  
  * **Semantic Errors (Validation against Schema \- as per assignment PDF item 6.b):**  
    * Non-existent table: `SELECT Nome FROM ClientesDesconhecidos;`  
    * Non-existent column in `SELECT`: `SELECT NomeCliente FROM Cliente;` (assuming `NomeCliente` is not a column)  
    * Non-existent column in `WHERE`: `SELECT Nome FROM Cliente WHERE NomedoMeio = 'X';`  
    * Non-existent column in `JOIN ON`: `SELECT C.Nome FROM Cliente C INNER JOIN Pedido P ON C.id_cliente = P.Cliente_idCliente;`  
    * Type mismatch in conditions (if parser/validator checks this, e.g., comparing string column to number without quotes): `SELECT Nome FROM Produto WHERE Nome = 123;`

### **5.2. Query Graph Generation Testing**

**Objective:** Ensure the initial (unoptimized) query graph correctly represents the parsed SQL query.

* For each valid SQL query from Parser Testing:  
  * **Expected Output:** A specific graph structure.  
    * Leaf nodes correctly map to tables in the `FROM` clause.  
    * Internal nodes correctly represent $\\sigma$, $\\pi$, $\\bowtie$ operations.  
    * Selection predicates are correctly associated with $\\sigma$ nodes.  
    * Join predicates are correctly associated with $\\bowtie$ nodes.  
    * Projection attributes are correctly listed in $\\pi$ nodes.  
    * The flow of data (edges) is logical.

**Example:**

* **SQL:** `SELECT C.Nome, P.DataPedido FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE C.Cidade = 'Fortaleza';`  
    
* **Expected Graph (Conceptual, one possible initial form):**  
    
            $\\pi\_{C.Nome, P.DataPedido}$  
    
                     |  
    
  $C \\bowtie\_{C.idCliente \= P.Cliente\\\_idCliente}$  
    
         /                     \\  
    
  $\\sigma\_{C.Cidade \= 'Fortaleza'}$      Pedido (P)  
    
          |  
    
      Cliente (C)  
    
  (Or the selection might be above the join initially, depending on parsing strategy, before optimization).

### **5.3. Query Optimization Testing**

**Objective:** Verify that the optimization heuristics (as per assignment PDF item 5.a, 5.b) are correctly applied to transform the initial query graph into a more efficient one.

* **Test Cases for Heuristic: Push Selections Down**  
    
  * **Input SQL:** `SELECT C.Nome, P.idPedido FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE C.Cidade = 'Fortaleza' AND P.ValorTotalPedido > 100;`  
  * **Expected Optimized Graph:** Selections $\\sigma\_{C.Cidade='Fortaleza'}(Cliente)$ and $\\sigma\_{P.ValorTotalPedido \> 100}(Pedido)$ should be performed *before* the join $Cliente \\bowtie Pedido$.  
  * **Expected Execution Order:** 1\. Filter Cliente. 2\. Filter Pedido. 3\. Join filtered results. 4\. Project.


* **Test Cases for Heuristic: Push Projections Down**  
    
  * **Input SQL:** `SELECT C.Nome FROM Cliente C INNER JOIN Pedido P ON C.idCliente = P.Cliente_idCliente WHERE P.Status_idStatus = 1;`  
  * **Expected Optimized Graph:**  
    * From `Cliente`, only `idCliente` (for join) and `Nome` (for final projection) are needed.  
    * From `Pedido`, only `Cliente_idCliente` (for join) and `Status_idStatus` (for filter) are needed.  
    * Projections $\\pi\_{idCliente, Nome}(Cliente)$ and $\\pi\_{Cliente\_idCliente, Status\_idStatus}(Pedido)$ should occur early, before or after selection but before join, if beneficial.  
  * **Execution Order:** Should reflect these early projections.


* **Test Cases for Heuristic: Combine Selections (Cascade)**  
    
  * **Input SQL:** `SELECT Nome FROM Cliente WHERE Cidade = 'Sao Paulo' AND TipoCliente_idTipoCliente = 2 AND Email = 'user@example.com';`  
  * **Expected Optimized Graph:** May show as a single $\\sigma$ with multiple conditions or a cascade $\\sigma\_{Email}(\\sigma\_{TipoCliente}(\\sigma\_{Cidade}(Cliente)))$. The key is that all conditions are applied to `Cliente` effectively.


* **Test Cases for Heuristic: Avoid Cartesian Product (Convert to Join)**  
    
  * **Input SQL (Implicit Join):** `SELECT Cliente.Nome, Pedido.DataPedido FROM Cliente, Pedido WHERE Cliente.idCliente = Pedido.Cliente_idCliente AND Cliente.Cidade = 'Recife';` (Note: The assignment specifies `INNER JOIN`, so this form might be out of scope for parsing, but if the parser handles comma-separated tables in `FROM` with conditions in `WHERE` as joins, this is relevant for optimization.)  
  * **Expected Optimized Graph:** Should be equivalent to an `INNER JOIN` with the selection on `Cliente` pushed down: $\\pi\_{Nome, DataPedido}( (\\sigma\_{Cidade='Recife'}(Cliente)) \\bowtie\_{idCliente=Cliente\_idCliente} Pedido )$.


* **For each optimization test case:**  
    
  * Clearly define the input SQL.  
  * Show the *expected* optimized query graph structure.  
  * List the *expected* order of execution of operations (as per assignment PDF item 6.g).

### **5.4. Result Exhibition Testing (Conceptual)**

**Objective:** While the AI agent may not execute queries, it should define test cases that allow for conceptual validation of the entire process.

* For a subset of key queries (especially those testing complex joins or optimizations):  
  1. **Define a small, consistent sample dataset** for the relevant tables (2-5 rows per table is often sufficient).  
     * Ensure data covers conditions (e.g., clients in different cities, orders with different values).  
  2. **Provide the SQL query.**  
  3. **Manually determine the expected final result set** based on the sample data and the query logic.  
  * This helps verify that the intended semantics of the query, as represented by the optimized plan, are correct.

### **5.5. Detailed Example Test Case for the AI to Generate**

This illustrates the level of detail expected for a test case focusing on optimization.

2. **Test ID:** `TC_OPTIM_SELECT_JOIN_001`  
     
3. **Purpose:** Verify selection push-down heuristic for two conditions on different tables involved in an INNER JOIN, and correct final projection.  
     
4. **Input SQL Query:** `SELECT Cliente.Nome, Pedido.DataPedido, Pedido.ValorTotalPedido FROM Cliente INNER JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente WHERE Cliente.Cidade = 'Fortaleza' AND Pedido.ValorTotalPedido > 100.00;`  
     
5. **Initial (Conceptual) Relational Algebra (if selection was above join):** $\\pi\_{Cliente.Nome, Pedido.DataPedido, Pedido.ValorTotalPedido} (\\sigma\_{Cliente.Cidade \= 'Fortaleza' \\land Pedido.ValorTotalPedido \> 100.00} (Cliente \\bowtie\_{Cliente.idCliente \= Pedido.Cliente\_idCliente} Pedido))$  
     
6. **Expected Optimized Relational Algebra / Graph Structure:** $\\pi\_{Cliente.Nome, Pedido.DataPedido, Pedido.ValorTotalPedido} ( (\\sigma\_{Cliente.Cidade \= 'Fortaleza'} (Cliente)) \\bowtie\_{Cliente.idCliente \= Pedido.Cliente\_idCliente} (\\sigma\_{Pedido.ValorTotalPedido \> 100.00} (Pedido)) )$  
     
   * **Graph Description:**  
     * Root Node: $\\pi\_{Cliente.Nome, Pedido.DataPedido, Pedido.ValorTotalPedido}$  
     * Child of Root: $\\bowtie\_{Cliente.idCliente \= Pedido.Cliente\_idCliente}$  
     * Left Child of Join: $\\sigma\_{Cliente.Cidade \= 'Fortaleza'}$  
       * Child of Left Selection: Leaf Node `Cliente`  
     * Right Child of Join: $\\sigma\_{Pedido.ValorTotalPedido \> 100.00}$  
       * Child of Right Selection: Leaf Node `Pedido`

   

7. **Expected Execution Order (from optimized graph):**  
     
   1. `OPERATION: SELECTION ON Cliente; CONDITION: Cliente.Cidade = 'Fortaleza'; RESULT: TempRelation1`  
   2. `OPERATION: SELECTION ON Pedido; CONDITION: Pedido.ValorTotalPedido > 100.00; RESULT: TempRelation2`  
   3. `OPERATION: INNER JOIN TempRelation1 AND TempRelation2; CONDITION: TempRelation1.idCliente = TempRelation2.Cliente_idCliente; RESULT: TempRelation3`  
   4. `OPERATION: PROJECTION ON TempRelation3; ATTRIBUTES: Nome, DataPedido, ValorTotalPedido; RESULT: FinalResult`

   

2. **Sample Data:**  
     
   * **Cliente Table Sample:**  
     

| idCliente | Nome | Email | TipoCliente\_idTipoCliente | Cidade | DataRegistro |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1 | Ana Silva | [ana.s@ex.com](mailto:ana.s@ex.com) | 1 | Fortaleza | 2023-03-10 |
| 2 | Rui Costa | [rui.c@ex.com](mailto:rui.c@ex.com) | 2 | Sao Paulo | 2023-04-15 |
| 3 | Lia Maia | [lia.m@ex.com](mailto:lia.m@ex.com) | 1 | Fortaleza | 2023-05-20 |
| 4 | Gilberto | [gil.b@ex.com](mailto:gil.b@ex.com) | 1 | Recife | 2023-06-01 |

     

   * **Pedido Table Sample:**  
     

| idPedido | Cliente\_idCliente | DataPedido | ValorTotalPedido | Status\_idStatus |
| :---- | :---- | :---- | :---- | :---- |
| 101 | 1 | 2024-01-15 | 150.50 | 1 |
| 102 | 2 | 2024-01-20 | 80.00 | 2 |
| 103 | 1 | 2024-02-10 | 90.75 | 1 |
| 104 | 3 | 2024-02-15 | 250.00 | 3 |
| 105 | 1 | 2024-03-01 | 120.00 | 1 |

   

2. **Expected Final Result (based on sample data and query):**  
   

| Cliente.Nome | Pedido.DataPedido | Pedido.ValorTotalPedido |
| :---- | :---- | :---- |
| Ana Silva | 2024-01-15 | 150.50 |
| Lia Maia | 2024-02-15 | 250.00 |
| Ana Silva | 2024-03-01 | 120.00 |

## **6\. Conclusion**

By systematically generating test cases covering SQL parsing, graph generation, the application of specified optimization heuristics, and conceptual result validation, the AI agent can significantly contribute to ensuring the robustness and correctness of the query processor. Strict adherence to the assignment's database schema and supported SQL features is crucial for the relevance of these tests.  
