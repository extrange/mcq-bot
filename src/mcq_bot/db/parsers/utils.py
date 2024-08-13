from mcq_bot.db.types import AnswerType, NoCorrectAnswerException


def validate_only_one_correct_answer(answers: list[AnswerType]):
    correct_answers = len([a for a in answers if a["is_correct"]])
    if correct_answers != 1:
        raise NoCorrectAnswerException(
            f"Expected 1 correct answer but got {correct_answers}"
        )
