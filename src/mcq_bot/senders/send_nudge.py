from datetime import date

from mcq_bot.client import get_client
from mcq_bot.managers.user import UserManager
from mcq_bot.utils.message import get_attempted_today, get_daily_target
from telethon import Button


async def send_nudge(user_id: int):
    client = get_client()
    attempted = get_attempted_today(user_id)
    target = get_daily_target(user_id)
    days_to_exam = UserManager.get_user(user_id).exam_dt - date.today()

    # Don't nudge the user if they've hit their target.
    if attempted >= target:
        return

    if not attempted:
        nudge_message = f"{days_to_exam.days} days to your exam and you haven't done any questions today, time to do at least {target} questions today!"
    else:
        nudge_message = (
            f"You've done {attempted} questions today, {target - attempted} more to go!"
        )

    await client.send_message(
        user_id, nudge_message, buttons=Button.inline("I'm ready!", data=user_id)
    )
