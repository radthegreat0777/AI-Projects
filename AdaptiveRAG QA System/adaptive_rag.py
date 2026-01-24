from typing import TypedDict

from dotenv import load_dotenv

from langchain_tavily import TavilySearch
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import StateGraph, START, END

# -------------------------------------------------------------------
# ENV
# -------------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------------
# TOOLS & MODELS
# -------------------------------------------------------------------
web_search_tool = TavilySearch(max_results=4)

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")

llm = ChatOpenAI(
    model="gpt-5-nano-2025-08-07",
    temperature=0
)

# -------------------------------------------------------------------
# STATE
# -------------------------------------------------------------------
class RAGState(TypedDict):
    question: str
    enriched_question: str
    context: str
    is_relevant: bool
    web_results: str
    answer: str

# -------------------------------------------------------------------
# LOAD + INDEX DOCUMENT
# -------------------------------------------------------------------
file_path = "./hr_manual.pdf"

loader = PyPDFLoader(file_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

splits = text_splitter.split_documents(docs)

if not splits:
    raise ValueError("No documents were loaded from the PDF.")

vector_store = InMemoryVectorStore(embedding=embedding_model)
vector_store.add_documents(splits)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def retrieve_context(query: str) -> str:
    docs = vector_store.similarity_search(query=query, k=5)
    return "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in docs
    )

# -------------------------------------------------------------------
# PROMPTS
# -------------------------------------------------------------------

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful assistant.
Answer ONLY using the provided context.
If the context does not contain the answer, say so clearly.
"""),
    ("human", """
Context:
{context}

Question:
{question}
""")
])

validation_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a strict validator.
Answer ONLY with YES or NO.
Say YES only if the context directly answers the question.
"""),
    ("human", """
Question:
{question}

Context:
{context}
""")
])

enrich_prompt = ChatPromptTemplate.from_messages([
    ("system", """
Rewrite the user question to improve document retrieval.
Make it more specific and focused.
DO NOT answer the question.
"""),
    ("human", """
Original Question:
{question}

Rewritten Question:
""")
])

web_answer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You answer questions using web search results.
If the answer is uncertain, say so clearly.
"""),
    ("human", """
Question:
{question}

Web Search Results:
{web_results}
""")
])

# -------------------------------------------------------------------
# CHAINS
# -------------------------------------------------------------------
rag_chain = rag_prompt | llm
validation_chain = validation_prompt | llm
enrich_chain = enrich_prompt | llm
web_answer_chain = web_answer_prompt | llm

# -------------------------------------------------------------------
# NODES
# -------------------------------------------------------------------
def enrich_query_node(state: RAGState):
    result = enrich_chain.invoke({"question": state["question"]})
    return {"enriched_question": result.content}

def retrieve_node(state: RAGState):
    context = retrieve_context(state["enriched_question"])
    return {"context": context}

def validate_node(state: RAGState):
    result = validation_chain.invoke({
        "question": state["enriched_question"],
        "context": state["context"]
    })
    is_relevant = result.content.strip().lower().startswith("yes")
    return {"is_relevant": is_relevant}

def answer_node(state: RAGState):
    result = rag_chain.invoke({
        "context": state["context"],
        "question": state["question"]
    })
    return {"answer": result.content}

def web_search_node(state: RAGState):
    resp = web_search_tool.invoke({"query": state["question"]})
    content = "\n".join(
        r["content"][:1000] for r in resp["results"]
    )
    return {"web_results": content}

def web_answer_node(state: RAGState):
    result = web_answer_chain.invoke({
        "question": state["question"],
        "web_results": state["web_results"]
    })
    return {"answer": result.content}

def is_relevant_condition(state: RAGState):
    return state["is_relevant"]

# -------------------------------------------------------------------
# GRAPH
# -------------------------------------------------------------------
graph = StateGraph(RAGState)

graph.add_node("enrich_query", enrich_query_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("validate", validate_node)
graph.add_node("answer", answer_node)
graph.add_node("web_search", web_search_node)
graph.add_node("web_answer", web_answer_node)

graph.add_edge(START, "enrich_query")
graph.add_edge("enrich_query", "retrieve")
graph.add_edge("retrieve", "validate")

graph.add_conditional_edges(
    "validate",
    is_relevant_condition,
    {
        True: "answer",
        False: "web_search"
    }
)

graph.add_edge("web_search", "web_answer")
graph.add_edge("answer", END)
graph.add_edge("web_answer", END)

adaptive_rag_graph = graph.compile()

# -------------------------------------------------------------------
# CLI LOOP
# -------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        user_query = input("\nEnter your question (or 'exit'): ")
        if user_query.lower() == "exit":
            break

        result = adaptive_rag_graph.invoke({
            "question": user_query
        })

        print("\nAnswer:\n", result["answer"])
