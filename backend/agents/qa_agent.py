from langchain_core.messages import HumanMessage, AIMessage
from rag_qa.llm_client import run_qa_chain
from db.crud import get_session_by_id, load_chat_history, save_messages

def handle_user_query(session_id: int, user_message: str, space_key: str, db) -> tuple[str, list[str], list[str]]:
    session = get_session_by_id(db, session_id)
    chat_history = load_chat_history(session)
    assistant_answer, source_links, source_titles = run_qa_chain(
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
        ],
        source_links=source_links,
        source_titles=source_titles
    )
    return assistant_answer, source_links, source_titles