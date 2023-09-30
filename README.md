# Telegram bot for survey

---

## Installation

Clone the repo
```bash
git clone https://github.com/evil-kekc/ggl_bot.git
cd ggl_bot
```

## Configuration
1. Replace credentials with yours in [.env](.env)
    ```text
    DATABASE_NAME=example
    POSTGRES_USER_NAME=postgres
    POSTGRES_USER_PASSWORD=postgres
    POSTGRES_HOST=127.0.0.1
    POSTGRES_PORT=5432
    
    BOT_TOKEN=0123456789:ABCDEFGHIGKLMNOPQRST
    
    HOST_URL=https://example.com
    APP_HOST=0.0.0.0
    APP_PORT=5000
    
    ADMIN_ID=123456789
    ```

2. Replace sqlalchemy.url in [alembic.ini](alembic.ini)
    ```bash
    sqlalchemy.url = postgresql://username:password@host/db_name
    ```

## Usage
Launch the application in one of the following ways:
- Polling
    ```bash
    # Using polling
    docker-compose -f docker-compose.polling.yml up
    ```
- Webhook (to launch a webhook you need to obtain SSL certificates, you can see how to do this [here](SSL.md))
    ```bash
    # Using webhook
    docker-compose -f docker-compose.webhook.yml up
    ```