from uuid import uuid4

import psycopg
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession

from db_models import PendingRequest

load_dotenv()

DB_URL = "postgresql://postgres:admin@localhost:5432/keels"

db = SQLDatabase.from_uri(DB_URL)


model = ChatOpenAI(
    model="gpt-3.5-turbo"
)

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

""".format(
    dialect=db.dialect,
    top_k=5
)

conn = psycopg.connect(DB_URL, autocommit=True)
checkpointer = PostgresSaver(conn=conn)
checkpointer.setup()

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer
)


async def approve_and_execute(
        approval_id:str,
        approve:bool,
        session: AsyncSession
):
    pending_request = await session.get(PendingRequest, approval_id)
    #fetches the record corresponding to PK

    if not pending_request:
        raise ValueError(f"Record not found for this approval id - {approval_id}")

    if pending_request.status != "pending":
        raise ValueError("This request has already been processed")

    if not approve:
        pending_request.status = "Rejected"
        await session.commit()
        return "Rejected"

    result = db.run(pending_request.sql)

    pending_request.status = "approved"
    await session.commit()
    return  str(result)



async def propose_dml_statement_for_human_approval(
        query: str,
        session:AsyncSession
):
    schema_details = db.get_table_info()
    prompt = f"""
    You are a SQL assistant, Generate Exactly INSERT,UPDATE,DELETE Statements
    Depending on the users requirement for {db.dialect}. User Provided Schema and DO NOT
    output  anything except for the SQL statement. Do not Wrap it in code fences. 
    {schema_details} 
    User Request - {query}  
    """
    resp = model.invoke([
        SystemMessage(content="You only Return a single SQL Statement"),
        HumanMessage(content=prompt)
    ])
    sql = resp.content if hasattr(resp, "content") else str(resp)
    approval_id = str(uuid4())

    pending_request = PendingRequest(
        id=approval_id,
        query=query,
        sql=sql,
        status="pending"
    )
    session.add(pending_request)
    await session.commit()
    return {"approval_id": approval_id, "sql": sql}


def query_db_with_natural_language(user_input: str, thread_id: str = "1"):
    try:
        config = {"configurable" : {"thread_id" : thread_id}}

        output_result = None

        for step in agent.stream(
                {"messages" : [{"role" : "user", "content": user_input}]},
                config,
                stream_mode="values"
        ):
            if "messages" in step:
                last_message = step["messages"][-1]
                if hasattr(last_message, "content"):
                    output_result = last_message.content

        return output_result if output_result else "No Content"
    except Exception as e:
        return f"Error Occurred - {str(e)}"