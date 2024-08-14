from pydantic import BaseModel


class AnswerCallback(BaseModel):
    answer_id: int
    question_id: int
