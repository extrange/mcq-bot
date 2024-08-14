from pydantic import BaseModel


class AnswerCallback(BaseModel):
    user_id: int
    answer_id: int
    question_id: int


NEXT_QUESTION = "next_question"


def is_answer_callback(data: str):
    try:
        AnswerCallback.model_validate_json(data)
    except Exception:
        return False
    return True
