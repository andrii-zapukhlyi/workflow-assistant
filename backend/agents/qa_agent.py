from langchain_core.messages import HumanMessage, AIMessage
from backend.rag.llm_client import run_qa_chain
from backend.db.crud import get_session_by_id, load_chat_history, save_messages
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.config.settings import GROQ_API_KEY

def generate_session_name(first_message: str) -> str:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
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

    return title.capitalize()


def handle_user_query(session_id: int, user_message: str, space_key: str, db) -> tuple[str, list[str]]:
    session = get_session_by_id(db, session_id)
    chat_history = load_chat_history(session)
    assistant_answer, links = run_qa_chain(
        user_message,
        space_key,
        chat_history
    )
    save_messages(
        db,
        session,
        [
            HumanMessage(content=user_message),
            AIMessage(content=assistant_answer),
        ]
    )
    return assistant_answer, links