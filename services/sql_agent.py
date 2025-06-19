import os
import ast
import logging
import re
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langchain_core.output_parsers import StrOutputParser

from .choose_state import State, QueryOutput
from .prompt import SQLTEMPLATE

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLAgent:
    """
    A class that uses an LLM and SQL database to answer questions.

    The SQLAgent class provides a way to interact with a SQL database using natural language.
    It uses a language model (LLM) to generate SQL queries from user questions, 
    executes those queries against the database,
    and then generates a natural language answer from the query results.

    Attributes:
        db_path (str): The path to the SQLite database.
        top_k (int): The number of results to return from the database.
        database (SQLDatabase): An instance of the SQLDatabase class, 
        used to interact with the database.
        llm (ChatOpenAI): An instance of the ChatOpenAI class, 
        used to generate SQL queries and answers.
        query_prompt_template (PromptTemplate): A prompt template for generating SQL queries.

    Methods:
        clean_sql_string(sql_string: str) -> str: Cleans and formats a SQL string by 
        removing unnecessary characters and whitespace.
        is_list_string(s: str) -> bool: Checks if a string is syntactically a Python list.
        write_query(state: dict) -> dict: Generates a SQL query from the given state (question).
        execute_query(state: dict) -> dict: Executes the SQL query and returns the result.
        generate_answer(state: dict) -> dict: Generates a natural language answer 
        from the SQL query results.
        run(question: str) -> dict: Executes the workflow to answer a question using SQL.
    """
    def __init__(self, db_path, top_k=5):
        logger.info("Initializing SQLAgent with database path: %s", db_path)
        self.db_path = db_path
        self.top_k = top_k
        self.database = SQLDatabase.from_uri(db_path)
        self.llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.2)
        self.query_prompt_template = PromptTemplate.from_template(SQLTEMPLATE)

    def clean_sql_string(self, sql_string):
        """Clean and format SQL string"""
        sql_string = re.sub(r"```sql|```", "", sql_string)
        sql_string = sql_string.replace("\\n", " ")
        sql_string = re.sub(r"\s+", " ", sql_string)
        return sql_string.strip()

    def is_list_string(self, s):
        """Check if a string is syntactically a Python list"""
        try:
            node = ast.parse(s, mode="eval")
            return isinstance(node.body, ast.List)
        except SyntaxError:
            return False

    def write_query(self, state):
        """Generate SQL query from state"""
        logger.info("WRITE QUERY")
        try:
            prompt = self.query_prompt_template.invoke(
                {
                    "dialect": self.database.dialect,
                    "top_k": 25,
                    "table_info": self.database.get_table_info(),
                    "input": state["question"],
                }
            )

            structured_llm = self.llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt)
            logger.info("Generated SQL Query: %s", result)

            if result is None:
                return {"query": "查無結果"}

            cleaned_query = self.clean_sql_string(result["query"])
            return {"query": cleaned_query}

        except Exception as e:
            logger.error("Error generating query: %s", e)
            return {"query": "查無結果"}

    def execute_query(self, state):
        """Execute SQL query"""
        logger.info("EXECUTE QUERY")

        try:
            execute_query_tool = QuerySQLDatabaseTool(db=self.database)
            result = execute_query_tool.invoke(state["query"])

            logger.info("SQL Result: %s", result)

            if not self.is_list_string(result):
                return {"result": "查無結果"}

            return {"result": result}

        except Exception as e:
            logger.error("Error executing query: %s", e)
            return {"result": "查無結果"}

    def generate_answer(self, state):
        """Generate answer from SQL results"""
        logger.info("GENERATE ANSWER")
        try:
            prompt = (
                "Given the following user question, corresponding SQL query, "
                "and SQL result, answer the user question.\n\n"
                f"Question: {state['question']}\n"
                f"SQL Query: {state['query']}\n"
                f"SQL Result: {state['result']}\n\n"
            )

            prompt += "請用繁體中文回答問題。\n"

            sql_output_chain = self.llm | StrOutputParser()
            response = sql_output_chain.invoke(prompt)
            return {"generation": response}

        except Exception as e:
            logger.error("Error generating answer: %s", e)
            return {"generation": "抱歉，生成答案時發生錯誤。"}

    def run(self, question):
        """
        Executes a workflow to answer a question using SQL.

        The workflow consists of writing a SQL query, executing it, and generating an answer based on the results.

        Args:
            question (str): The question to answer.

        Returns:
            dict: A dictionary containing the final output of the workflow.
        """
        workflow = StateGraph(State)
        workflow.add_node("write_query", self.write_query)  # write query
        workflow.add_node("execute_query", self.execute_query)  # execute query
        workflow.add_node("generate_answer", self.generate_answer)  # generate answer

        workflow.add_edge(START, "write_query")
        workflow.add_edge("write_query", "execute_query")
        workflow.add_edge("execute_query", "generate_answer")
        workflow.add_edge("generate_answer", END)

        compiled_app = workflow.compile()
        output = compiled_app.invoke({"question": question})
        return output
