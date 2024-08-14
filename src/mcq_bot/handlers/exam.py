import logging
from datetime import date

from dateutil import parser
from mcq_bot.managers.user import UserManager
from mcq_bot.utils.message import extract_command_content, get_user_id
from sqlalchemy.exc import SQLAlchemyError
from telethon.custom import Message
from telethon.events import StopPropagation

logger = logging.getLogger(__file__)


async def handle_exam_date(message: Message):
    text = message.text
    user_id = get_user_id(message)
    if text is None:
        raise StopPropagation

    extracted_date = extract_command_content(text)

    if not extracted_date:
        user = UserManager.get_user(user_id)

        await message.reply(
            f"""
        {f"Your current exam date is {user.exam_dt.isoformat()}." if user else ""}

        You can set or update your exam date with `/exam your-exam-date`.

        For example: `/exam 22-10-2024`
        """
        )
        raise StopPropagation

    try:
        parsed_datetime = parser.parse(extracted_date, dayfirst=True, fuzzy=True)
        parsed_date = parsed_datetime.date()
        UserManager.add_user(user_id, parsed_date)

    except parser.ParserError as e:
        await message.reply(
            "Sorry, I couldn't understand that date. Try something like 1 Jan 2024 instead."
        )
        logger.error(e)
        raise StopPropagation

    except SQLAlchemyError as e:
        logger.info("Error adding user: %s", e)
        await message.reply("Oops, we encountered an error, please try again")
        raise StopPropagation

    days_from_now = parsed_date - date.today()

    await message.reply(
        f"I've set your exam date as {parsed_date.isoformat()}, which is {days_from_now.days} days from today. If that's not correct, just send me another date with `/exam`."
    )
