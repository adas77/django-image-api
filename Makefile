py = python3
backend = backend
port = 8000
super_user_name = admin
super_user_email = admin@example.com
super_user_password = fF1aqm18

manage = ${backend}/manage.py
fixture_accounts = ${backend}/api/fixtures/default_accounts.json
fixture_tier = ${backend}/api/fixtures/default_tiers.json

run = $(py) $(manage)
migrate_make = $(py) makemigrations

f:
	$(run) loaddata $(fixture_tier) $(fixture_accounts)

r:
	$(run) runserver 0.0.0.0:$(port)

u:
	DJANGO_SUPERUSER_USERNAME=${super_user_name} \
	DJANGO_SUPERUSER_PASSWORD=${super_user_password} \
	DJANGO_SUPERUSER_EMAIL=${super_user_email} \
	${run} createsuperuser --noinput
m-make:
	$(run) makemigrations

m-run:
	$(run) migrate

m: m-make m-run