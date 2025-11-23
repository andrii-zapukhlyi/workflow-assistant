from typing import List, Tuple
from langchain_core.messages import HumanMessage, AIMessage
from rag.llm_client import run_qa_chain
from db.crud import get_latest_session, create_session, load_chat_history, save_messages
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os

def generate_session_name(first_message: str) -> str:
    llm = ChatGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Generate a short title (max 5 words) summarizing the user's message. "
         "Do NOT add new information. Keep it concise, neutral, and lowercase."),
        ("user", first_message)
    ])

    response = llm.invoke(prompt.format_messages())
    title = response.content.strip()

    if not title:
        title = first_message[:8] + "..."

    title.capitalize()
    return title


def handle_user_query(user_id: int, user_message: str, space_key: str, db) -> Tuple[str, List[str]]:
    session = get_latest_session(user_id, db)

    if not session:
        session_name = generate_session_name(user_message)
        session = create_session(user_id, session_name, db)

    chat_history = load_chat_history(session)
    assistant_answer, links = run_qa_chain(user_message, space_key, chat_history)

    new_messages = [
        HumanMessage(content=user_message),
        AIMessage(content=assistant_answer),
    ]
    save_messages(session, new_messages, db)

    return assistant_answer, links