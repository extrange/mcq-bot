import asyncio
import logging
from asyncio import AbstractEventLoop

import schedule

from mcq_bot.managers.user import UserManager
from mcq_bot.senders.send_nudge import send_nudge

logger = logging.getLogger(__file__)


async def _job():
    scheduled_users = UserManager.get_scheduled_users()
    for user in scheduled_users:
        try:
            await send_nudge(user.id)
            logger.info("Nudge sent to %s", user.id)
        except Exception as e:
            logger.error(
                "Failed to send scheduled question for user %s: %s", user.id, e
            )


async def start_schedule(loop: AbstractEventLoop, job: schedule.Job):
    job.do(lambda: loop.create_task(_job()))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
