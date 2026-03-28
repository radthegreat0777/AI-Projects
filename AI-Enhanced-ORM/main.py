from fastapi import FastAPI

from db_agent import query_db_with_natural_language
from user_routes import router as user_router
from invoice_route import router as invoice_router
from agent_routes import  router as agent_router
from uuid import uuid4
import gradio as gr
app = FastAPI(title="ORM Implementation")

app.include_router(user_router)
app.include_router(invoice_router)
app.include_router(agent_router)


def db_agent_gradio_ui():
    with gr.Blocks() as db_ui:
        gr.Markdown("Database Agent")
        gr.Markdown("Query Your database with natural language")
        thread_id = gr.State(str(uuid4()))
        chatbot = gr.Chatbot(label="Conversation")
        msg = gr.Textbox(label="Enter Message")
        def respond(message: str, history: list, current_thread_id: str):
            result = query_db_with_natural_language(message, thread_id=current_thread_id)

            history = history + [
                {"role" : "user", "content" : message},
                {"role" : "assistant", "content" : result}
            ]

            return history, "", current_thread_id
        msg.submit(
            respond,
            inputs=[msg,chatbot, thread_id],
            outputs=[chatbot, msg, thread_id]
        )
    return db_ui

app = gr.mount_gradio_app(app, db_agent_gradio_ui(), "/agent/ui")
