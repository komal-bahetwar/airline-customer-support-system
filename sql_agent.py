import os
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.runnables import RunnableSequence

from llm_config import llm, table_schema
from db_utils import execute_sql_query

@tool
def execute_sql_query_tool(sql_query: str) -> str:
    """Executes a given SQL query on the PostgreSQL database and returns the result set.
    Input is an SQL query string."""
    print(f"Executing SQL Query: {sql_query}")
    results = execute_sql_query(sql_query)
    return str(results)

# Define the SQL generation prompt template
SQL_PROMPT_TEMPLATE = """You are an expert PostgreSQL database user. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 10 results.

You have access to a table named `flights` with the following columns:
{table_schema}

For example:
Question: "What is the status of flight 6E477?"
SQL Query: "SELECT status FROM flights WHERE flight_no = '6E477';"

Question: "Show flights from Delhi to Mumbai."
SQL Query: "SELECT * FROM flights WHERE origin = 'BOM' AND destination = 'BLR' LIMIT 10;"

Question: "What is the gate for flight AI101?"
SQL Query: "SELECT gate FROM flights WHERE flight_no = 'AI101';"

Question: "Show available flights from Mumbai to Bengaluru on 2026-11-05."
SQL Query: "SELECT * FROM flights WHERE origin = 'BOM' AND destination = 'BLR' AND departure_date = '2026-11-05' AND seats_booked < seats_total LIMIT 10;"

Question: {query}
SQL Query:"""

sql_generation_prompt = PromptTemplate.from_template(SQL_PROMPT_TEMPLATE)
sql_generation_chain = sql_generation_prompt | llm

# Define the prompt for the final answer generation after SQL execution
answer_generation_prompt = PromptTemplate.from_template(
    """You are an airline customer support agent. Given the user's original question, the SQL query that was executed,
    and the results from the database, provide a clear and concise answer to the user.

    Original Question: {question}
    SQL Query Executed: {sql_query}
    SQL Results: {sql_results}

    Based on the above information, respond to the user:
    """
)
answer_from_sql_results_chain = answer_generation_prompt | llm

def sql_query_agent_chain(question: str) -> str:
    # Step 1: Generate SQL query from the natural language question
    generated_sql_output = sql_generation_chain.invoke({"query": question, "table_schema": table_schema})
    generated_sql = generated_sql_output.content.strip()

    # Extract only the SQL part if the LLM adds extra text or markdown formatting
    if '```sql' in generated_sql:
        start_index = generated_sql.find('```sql') + len('```sql')
        end_index = generated_sql.find('```', start_index)
        if start_index != -1 and end_index != -1:
            sql_to_execute = generated_sql[start_index:end_index].strip()
        else:
            sql_to_execute = generated_sql.strip()
    else:
        sql_to_execute = generated_sql.strip()

    # SQL Guardrail: Prevent DELETE or DROP statements
    if "DELETE" in sql_to_execute.upper() or "DROP" in sql_to_execute.upper() or "UPDATE" in sql_to_execute.upper() or "TRUNCATE" in sql_to_execute.upper():
        print("\nSQL Guardrail: Dangerous SQL command detected.")
        return "I'm sorry, I cannot execute queries that modify or delete data. Please ask a read-only question."

    # Step 2: Execute the generated SQL query using the tool
    sql_results = execute_sql_query_tool.invoke(sql_to_execute)

    # Step 3: Generate the final answer using the original question, SQL query, and results
    final_answer_output = answer_from_sql_results_chain.invoke({
        "question": question,
        "sql_query": sql_to_execute,
        "sql_results": sql_results
    })
    return final_answer_output.content
