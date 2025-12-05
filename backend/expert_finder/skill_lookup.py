from typing import List, Dict
from backend.db.crud import get_employees_by_skills
from sqlalchemy.orm import Session

def skill_lookup_tool(db: Session, skills: List[str]) -> Dict:
    if not skills:
        return {"employees": []}

    employees = get_employees_by_skills(db, skills)

    if not employees:
        return {"employees": []}

    result = []
    for emp in employees:
        if emp.position_obj:
            result.append({
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department,
                "position_level": emp.position_obj.position_level,
                "position": emp.position_obj.position,
                "skills": emp.position_obj.skills,
            })

    return {"employees": result}