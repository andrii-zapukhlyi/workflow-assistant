from typing import Any, Dict, List
import os
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.messages import BaseMessage
from rag.retriever import get_retriever
from langchain_groq import ChatGroq


def build_qa_chain(llm: ChatGroq, retriever: Any) -> Any:
    rephrase_system = (
        "Given a chat history and the latest user question, "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    rephrase_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", rephrase_system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    history_retriever = create_history_aware_retriever(llm, retriever, rephrase_prompt)

    qa_system = (
        "You are an expert assistant for Confluence documentation. "
        "Answer only based on the provided context. "
        "If the answer is not in the context, respond exactly: "
        "\"There is no information about the question in the provided documents for your department.\""
        "\n\n"
        "Context:\n{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    combine_docs = create_stuff_documents_chain(llm, qa_prompt)

    retrieval_chain = create_retrieval_chain(history_retriever, combine_docs)
    return retrieval_chain


def run_qa_chain(user_message: str, space_key: str, chat_history: List[BaseMessage]) -> tuple[str, List[str]]:
    llm = ChatGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile"
    )

    retriever = get_retriever(space_key, 2)
    qa_chain = build_qa_chain(llm, retriever)

    inputs: Dict[str, Any] = {
        "input": user_message,
        "chat_history": chat_history,
    }

    result = qa_chain.invoke(inputs)
    assistant_answer = result["answer"]
    docs = result.get("source_documents", [])
    source_links = [doc.metadata.get("source", "") for doc in docs]
    return assistant_answer, source_links