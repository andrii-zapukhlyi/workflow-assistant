from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY
from langchain_core.output_parsers import PydanticOutputParser

class SkillExtraction(BaseModel):
    skills: List[str]

def skill_extractor_tool(query: str) -> List[str]:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    )

    prompt = (
        "Extract ONLY technical skills or relevant expertise from the user query. "
        "Return valid JSON **using double quotes** exactly like this: {\"skills\": [\"skill1\", \"skill2\"]}. "
        "Do NOT include any explanations, markdown, or formatting. "
        "Expand abbreviations (e.g. 'k8s' → 'kubernetes'). "
        "If no skills exist, return {\"skills\": []}.\n\n"
        f"User query: {query}"
    )

    parser = PydanticOutputParser(pydantic_object=SkillExtraction)
    response = llm.invoke([
        {"role": "system", "content": prompt},
    ])

    parsed = parser.parse(response.content)
    return [skill.lower() for skill in parsed.skills]