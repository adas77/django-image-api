# Envs

In `.env`

# Run

## Docker

```bash
make d
```

or

```bash
docker compose -p "django-image-api-az4ek7fb2gs" -f docker/docker-compose.dev.yml --env-file .env up --build
```

## Local

### Env install

```bash
pip install -r backend/requirements.txt
```

### Run

```bash
python3 backend/manage.py migrate
make f
make r
```

or

```bash
python3 backend/manage.py migrate
python3 backend/manage.py loaddata backend/api/fixtures/default_tiers.json backend/api/fixtures/default_users.json backend/api/fixtures/admin.json
python3 backend/manage.py runserver 127.0.0.1:8000
```

# Test

## Docker (Container needs to be running)

```bash
make d-test
```

or

```bash
docker exec django-image-api-python-jEGpBquIloU python3 backend/manage.py test api --parallel
```

## Local

```bash
make t
```

or

```bash
python3 backend/manage.py test api --parallel
```
