# MCQ Bot

Telegram bot which sends MCQ questions and validates their answers to users.

Supports sending daily reminders to the user.

## Setup

You will need to enter the bot token manually by exec-ing into the compose container:

```
docker compose run -it mcq-bot bash
cd /app
python -m mcq_bot.main
```

Then, load the questions into the production database:

```
python -m mcq_bot.scripts.add_questions questions_dir data/prod.db
```
