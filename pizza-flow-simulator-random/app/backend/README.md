# Migrations
Create new migration

- Add to dbmigrations/env.py the import of the model in L10

```
docker exec -it cc-server bash
alembic revision --autogenerate -m "create RFA" # Set the message
alembic upgrade heads # Run the migrations
```