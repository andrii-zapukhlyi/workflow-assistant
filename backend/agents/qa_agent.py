from langchain_core.messages import HumanMessage, AIMessage
from backend.rag_qa.llm_client import run_qa_chain
from backend.db.crud import get_session_by_id, load_chat_history, save_messages

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