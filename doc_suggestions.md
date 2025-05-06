## AI-Focused Documentation Guide for GitHub Copilot

This document provides instructions for GitHub Copilot to generate comprehensive and AI-efficient documentation for the **ProcConsultas** project. The goal is to create documentation that is not only human-readable but also easily understood and utilized by AI agents like Copilot itself for tasks such as code understanding, further code generation, and maintenance.

The "ProcConsultas" project appears to be a **query processor**. Based on the file and directory names, its core functionalities likely include:
* Parsing input queries (potentially SQL or a custom query language).
* Translating queries into an internal representation, possibly relational algebra and query trees.
* Optimizing these query trees/plans.
* Interacting with a database for schema definition, data generation, and query execution.
* Visualizing query trees (suggested by the `graphviz` dependency).

### I. General Principles for AI-Readable Documentation

When generating any documentation, prioritize:

1.  **Clarity and Conciseness:** Use straightforward language. Avoid jargon where possible, or explain it clearly if necessary.
2.  **Structured Information:** Employ headings, bullet points, lists, and code blocks to organize information logically.
3.  **Keywords:** Naturally incorporate relevant keywords throughout the documentation. For this project, keywords include: "query processing," "SQL parser," "relational algebra," "query optimization," "query tree," "syntax tree," "database schema," "data generation," "execution plan," "cost model," etc.
4.  **Explicit Relationships:** Clearly state the relationships between different modules, classes, functions, and files. For instance, "This module parses SQL queries and converts them into a query tree structure defined in `arvore.py`."
5.  **Purpose and Intent:** For every component (project, file, function, class), clearly state its primary purpose or intent.
6.  **Input/Output:** For functions and scripts, clearly document expected inputs (and their formats/types) and outputs (and their formats/types).
7.  **Assumptions and Constraints:** Note any assumptions made by the code or any constraints under which it operates.
8.  **Consistent Terminology:** Use the same terms consistently for the same concepts across all documentation.

### II. Instructions for `README.md`

The main `README.md` file should serve as the central entry point for understanding the project. Copilot should structure it as follows:

```markdown
# Project: ProcConsultas - Query Processor

## 1. Overview
   - **Intent:** Briefly state the main purpose of the ProcConsultas project (e.g., "An educational query processor designed to parse, optimize, and execute database queries, demonstrating concepts of relational algebra and query optimization techniques.").
   - **Core Functionalities:** List the key features using bullet points:
      - SQL Query Parsing
      - Relational Algebra Transformation
      - Query Tree Generation and Manipulation (see `plantando_arvores` and `novo_plantando_arvores` modules)
      - Query Optimization Strategies (e.g., rule-based, cost-based if applicable)
      - Database Interaction (schema creation, data loading, query execution)
      - (If applicable) Visualization of query plans using Graphviz.
   - **Target Audience:** (e.g., "Students learning database systems, researchers in query optimization.")

## 2. Project Structure
   - Provide a high-level overview of the main directories and their roles. Focus on AI-parsable descriptions.
     - **`ProcConsultas/` (Root Directory)**
       - `main.py`: **Purpose:** Main entry point for the query processor application. **Orchestrates:** Query parsing, optimization, and execution flow.
       - `parser.py`: **Purpose:** Handles parsing of input query strings. **Input:** Query string. **Output:** Abstract Syntax Tree (AST) or initial query representation.
       - `diff.py`: **Purpose:** (Infer based on content or provide placeholder: e.g., "Utility for comparing query results or execution plans.")
       - `requirements.txt`: **Purpose:** Lists project dependencies (e.g., `psycopg2-binary`, `graphviz`).
     - **`banco_de_dados/`**: **Purpose:** Manages database setup, definition, and data generation.
       - `definicao_banco/`: **Purpose:** Scripts and modules for defining the database schema, creating tables, indexes, and populating data.
         - `definicao_banco.py`: **Purpose:** Python script to programmatically define/create the database structure.
         - `geracao_dados.py`: **Purpose:** Python script for generating synthetic data for the database tables.
         - `criacao/`: **Purpose:** Contains SQL scripts for creating database objects (tables, indexes).
         - `exclusao/`: **Purpose:** Contains SQL scripts for deleting database objects or data.
         - `configuracoes/`: **Purpose:** Contains SQL scripts for database configuration settings.
     - **`plantando_arvores/` (and `novo_plantando_arvores/`)**: **Purpose:** Modules related to the construction, representation, and processing of query trees (algebraic representations).
       - `arvore.py`: **Purpose:** Defines the data structures for representing query trees (nodes, edges, operations).
       - `processamento_consultas.py` (or `processamento.py`): **Purpose:** Implements the logic for processing queries, possibly converting them to tree form or executing them based on the tree.
       - `otimizacao_consultas.py`: **Purpose:** Implements query optimization algorithms and heuristics. Transforms query trees to more efficient forms.
       - `desmatamento.py`: **Purpose:** (Metaphorical) Likely involved in query tree pruning or simplification as part of optimization.
       - `relational_algebra_parser.py` (in `novo_plantando_arvores`): **Purpose:** Parses relational algebra expressions or converts SQL AST to relational algebra.
       - `algebra_utils_clause.py` (in `novo_plantando_arvores`): **Purpose:** Utility functions for handling clauses in relational algebra expressions.
     - **`docs/`**: **Purpose:** Contains detailed documentation for specific modules or concepts.

## 3. Setup and Installation
   - **Prerequisites:** List necessary software (e.g., Python 3.x, PostgreSQL).
   - **Dependencies:** Explain how to install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - **Database Setup:** Provide clear, step-by-step instructions on how to set up the required database. Include commands for:
     - Creating the database.
     - Running schema creation scripts (e.g., `python banco_de_dados/definicao_banco/definicao_banco.py` or psql commands).
     - Running data generation scripts (e.g., `python banco_de_dados/definicao_banco/geracao_dados.py`).

## 4. Usage
   - Provide examples of how to run the query processor.
   - **Command-line arguments:** If `main.py` (or other scripts) accepts arguments, document them clearly.
     - Example: `python main.py --query "SELECT * FROM table WHERE condition;" --optimize`
   - **Input format:** Specify the expected format for input queries.
   - **Output format:** Describe what the program outputs (e.g., query results, execution time, optimized query plan).

## 5. Key Modules and Logic Flow (AI-Assist Section)
   - **High-Level Data Flow:** Describe the typical lifecycle of a query within the system:
     1. Query Input (e.g., via `main.py`).
     2. Parsing (`parser.py`): Input query string -> AST/Internal Representation.
     3. Semantic Analysis / Initial Tree Construction (`plantando_arvores/arvore.py`, `plantando_arvores/processamento_consultas.py`).
     4. (Optional) Conversion to Relational Algebra (`novo_plantando_arvores/relational_algebra_parser.py`).
     5. Query Optimization (`plantando_arvores/otimizacao_consultas.py`, `plantando_arvores/desmatamento.py`): Original Query Tree -> Optimized Query Tree.
     6. Execution Plan Generation (if distinct from optimization).
     7. Query Execution (interaction with `banco_de_dados`).
     8. Result Output.
   - **Core Algorithms:** Briefly mention or point to where core algorithms are implemented (e.g., "Query optimization uses heuristic rules defined in `otimizacao_consultas.py` such as predicate pushdown...").

## 6. Contribution Guidelines (Optional)
   - If applicable, provide guidelines for contributing to the project.

## 7. License (Optional)
   - Specify the project's license.
```

### III. Instructions for File-Level Documentation Headers

For each significant `.py` and `.sql` file (excluding files in `venv/` or obvious test data unless they are complex), Copilot should add a header comment block. This header should be easily parsable by AI.

**A. For Python Files (`.py`):**

Use a consistent docstring format at the beginning of each file and for each class/function.

```python
"""
File: <filename.py>
Author: <Original Author if known, otherwise placeholder or leave blank>
Date: <Creation/Last Modification Date if known>

Intent:
    - This file defines/implements [primary purpose of the file].
    - For example: "This file implements the SQL parser using [library/method]..."
    - Or: "This file contains the data structures for representing query execution plan nodes."

Key Components:
    - Class `MyClass`: Purpose - [Brief description of the class's role]. Key methods: `method1`, `method2`.
    - Function `my_function(param1, param2)`: Purpose - [Brief description]. Input: `param1` (type, description), `param2` (type, description). Output: (type, description).
    - (List other significant classes/functions)

Dependencies:
    - Internal: `module_x.py`, `class_y` (Briefly state why it's a dependency)
    - External: `psycopg2`, `graphviz` (Briefly state its use in this file)

AI-Notes:
    - Target for AI understanding: [e.g., "Relational algebra node types and transformations", "SQL parsing logic for SELECT statements"]
    - Keywords: [e.g., "query tree", "node", "operator", "parser", "AST", "relational algebra"]
"""

# ... rest of the Python code
```

**B. For SQL Files (`.sql`):**

Use a standard SQL comment block at the beginning of the file.

```sql
-- File: <filename.sql>
-- Author: <Original Author if known, otherwise placeholder or leave blank>
-- Date: <Creation/Last Modification Date if known>
--
-- Intent:
--   - This SQL script is responsible for [primary purpose, e.g., "creating the initial database schema for the university database"].
--   - It defines tables such as [Table1, Table2] and their relationships.
--   - Or: "This script creates indexes on frequently queried columns to improve performance."
--   - Or: "This script populates the 'Students' table with sample data."
--
-- Key Operations:
--   - CREATE TABLE <TableName1>: Defines [brief description of table purpose and key columns].
--   - CREATE INDEX <IndexName> ON <TableName>(<ColumnName>): Purpose - [e.g., "Speeds up lookups by student ID"].
--   - INSERT INTO <TableName>: Populates [brief description of data being inserted].
--
-- Dependencies/Order:
--   - This script should be run [before/after] <other_script.sql>.
--   - Assumes the database <db_name> and schema <schema_name> exist (if applicable).
--
-- AI-Notes:
--   - Target for AI understanding: [e.g., "Database schema definition", "Index creation strategy", "Sample data for 'Courses' table"]
--   - Keywords: [e.g., "CREATE TABLE", "PRIMARY KEY", "FOREIGN KEY", "INDEX", "INSERT DATA", "university schema"]

-- ... rest of the SQL code
```

### IV. Specific Guidance for "ProcConsultas"

* **`arvore.py` files:** Emphasize the structure of the tree nodes, the types of operators they represent (e.g., SELECT, PROJECT, JOIN, AGGREGATE, SCAN), and any methods for manipulating or traversing the tree.
* **`parser.py` / `relational_algebra_parser.py`:** Detail the input language (subset of SQL, specific relational algebra syntax) and the output structure (AST, specific query tree format).
* **`otimizacao_consultas.py`:** Clearly list the optimization rules or heuristics implemented (e.g., predicate pushdown, join reordering, projection pushdown). If cost-based, mention the cost model elements.
* **`definicao_banco.py` / `geracao_dados.py` and SQL DDLs:** Clearly describe the schema being created/populated – table names, column names, data types, primary/foreign keys, and the nature of the generated data.
* **`main.py`:** Document the overall control flow, command-line arguments, and how it integrates the other modules.

By following these guidelines, GitHub Copilot can help create a well-documented "ProcConsultas" project that is significantly easier for both humans and AI agents to understand, maintain, and build upon.

```
This markdown file provides the requested instructions.
```