from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing_extensions import Annotated
from typing import List


class State(TypedDict):
    """State for the SQL retrieval process
    question: The question to ask the model.
    query: The generated SQL query.
    result: The result of the SQL query.
    answer: The answer to the question.
    """

    question: str
    query: str
    result: str
    generation: str


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]
