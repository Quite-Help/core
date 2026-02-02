# core
to run application install docker and docker-compose first then follow the commands bellow to run application
```
cp .env.example .env
docker compose up --build
```

if you made changes to schema, run the database service alone which binds to host machine's ports. Adjust SYNC_DATABASE_URL to use localhost address then generate migration files then switch SYNC_DATABASE_URL back to use db (docker-compose creates the db dns mapping which can be used by core-api service)
```
docker compose up db
# change SYNC_DATABASE_URL to postgresql+psycopg2://counseling:counseling@localhost:5432/counseling
alembic revision --autogenerate -m "<describe-your-schema-change>"
docker compose down
# change SYNC_DATABASE_URL back to postgresql+psycopg2://counseling:counseling@db:5432/counseling
docker compose up --build
```

to access the swagger page go to localhost:8000/docs. For api endpoints requireing auth, first visit /account/tmp/bootstrap to create the default user with username=admin and password=admin. Then go to /account/token to get an access_token with the previous credentails. provide the access_token value by clicking the lock icon corresponding to the API endpoint and pasteing in the access_token in the bearer token field