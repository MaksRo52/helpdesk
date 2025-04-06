#pip install poetry
#poetry install
#source .venv/bin/activate
#poetry update
#python3 manage.py makemigrations
#python3 manage.py migrate
#python3 manage.py collectstatic --no-input
#exit
docker compose down
docker system prune -f
docker volume rm helpdesk_static
docker compose up --build -d
#docker compose exec app poetry run python manage.py makemigrations
#docker compose exec app poetry run python manage.py migrate
