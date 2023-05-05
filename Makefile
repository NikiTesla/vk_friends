PROJECTNAME=$(shell basename "$(PWD)")

run:
	@ echo "  >  running manage.py runserver..."
	@ sudo docker start vk_pg
	@ sleep 1
	@ python3 manage.py makemigrations
	@ python3 manage.py migrate
	@ python3 manage.py runserver

docker:
	@ sudo docker build -t friends .
	@ sudo docker compose up