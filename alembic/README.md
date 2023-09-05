- Create migrations
    ```bash
    alembic revision -m "initial migration"
    ```

- Applying migrations
    ```bash
    alembic upgrade head
    ```

- Rolling back migrations
  ```bash
  alembic downgrade -1
  ```