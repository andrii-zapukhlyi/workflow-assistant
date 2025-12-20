from langchain_groq import ChatGroq
from sqlalchemy.orm import Session

from config.settings import GROQ_API_KEY
from expert_finder.skill_extractor import skill_extractor_tool
from expert_finder.skill_lookup import skill_lookup_tool


def ask_expert_agent(db: Session, query: str, user_department: str) -> str:
    extracted_skills = skill_extractor_tool(query)
    lookup_result = skill_lookup_tool(db, extracted_skills)
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
    prompt = (
        "You are an expert finding agent. A user is asking for help with the following skills: "
        f"{', '.join(extracted_skills)}.\n\n"
        "The following is the result of looking up experts with those skills:\n"
        f"{lookup_result}\n\n"
        "Start searching from the same department as the user, AND feel free to look in other departments if no suitable expert is found. Better to suggest an expert from another department than no expert at all.\n\n"
        f"User department: {user_department}\n\n"
        "If no suitable expert is found, respond with: 'No suitable expert found.'"
        "Just provide one sentence in the format: 'You can contact {Full Name} (Position level position name in lower case) at **{Email}** for assistance with {skills}.'"
    )
    response = llm.invoke(
        [
            {"role": "system", "content": prompt},
        ]
    )
    return response.content
