from mcq_bot.db.db_types import AnswerType, NoCorrectAnswerException


def validate_only_one_correct_answer(answers: list[AnswerType]):
    """Checks that in a list of AnswerTypes, there is only 1 answer marked as correct, or raises an exception."""
    correct_answers = len([a for a in answers if a["is_correct"]])
    if correct_answers != 1:
        raise NoCorrectAnswerException(
            f"Expected 1 correct answer but got {correct_answers}"
        )
