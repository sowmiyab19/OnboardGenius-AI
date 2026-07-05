import os
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.models import ChatHistory
from backend.schemas import ChatHistoryCreate

# Optional OpenAI integration
import openai

def get_chat_history(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatHistory]:
    return db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp.asc()).offset(skip).limit(limit).all()

def log_chat_message(db: Session, user_id: int, message: str, response: str) -> ChatHistory:
    db_chat = ChatHistory(
        user_id=user_id,
        message=message,
        response=response
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def generate_chatbot_response(message: str, context: Optional[dict] = None) -> str:
    """
    Generates response from OpenAI if configured, otherwise falls back to helper responses.
    Allows passing employee context (name, department, tasks status) for personalized answers.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Build a contextual system prompt
    system_content = "You are the OnboardGenius AI assistant, a friendly HR and employee onboarding bot. Help the employee with onboarding questions, checklist items, policy summaries, and standard HR questions."
    
    if context:
        name = context.get("name", "Team Member")
        dept = context.get("department", "Company")
        pos = context.get("position", "Member")
        tasks_info = context.get("tasks_info", "")
        system_content = (
            f"You are the OnboardGenius AI assistant, a friendly HR and employee onboarding bot. "
            f"You are conversing with {name}, a {pos} in the {dept} department. "
            f"Here is their current task status:\n{tasks_info}\n"
            f"Please address them by name and provide helpful advice regarding their onboarding."
        )

    if api_key and api_key != "your-openai-api-key-here":
        try:
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": message}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Fallback on OpenAI API call error
            return f"I had a small issue accessing my AI brain, but I'm here to help! Regarding your query: '{message}', could you please contact HR or check the onboarding portal documents?"

    # Static rule-based chatbot fallback
    name = context.get("name", "") if context else ""
    salutation = f"Hi {name}! " if name else "Hello! "
    
    msg = message.lower()
    if "hello" in msg or "hi" in msg:
        return f"{salutation}I am OnboardGenius AI. I am here to assist you with your onboarding checklist, documents, and any company policies. What can I do for you today?"
    elif "task" in msg or "todo" in msg:
        task_status = f" Currently, your tasks are: {context.get('tasks_info', '')}" if context and context.get("tasks_info") else ""
        return f"You can view your onboarding checklist on the Tasks page of the dashboard.{task_status} Please make sure to complete them before their due dates."
    elif "document" in msg or "form" in msg:
        return "Any required HR documents (like ID proofs or contracts) can be uploaded securely under the Documents section."
    elif "contact" in msg or "hr" in msg:
        return "You can reach out to the HR department via hr@onboardgenius.com or visit the administration room on the 3rd floor."
    elif "policy" in msg or "rule" in msg:
        return "Company policies are detailed in the Employee Handbook. You can find it under the Documents tab, or ask your manager for a copy."
    else:
        return f"Thank you for asking, {name if name else 'there'}! For specific details on onboarding or system issues, please reach out to your HR supervisor or check your profile dashboard."
