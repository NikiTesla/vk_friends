PROJECTNAME=$(shell basename "$(PWD)")

run:
	@ echo "  >  running manage.py runserver..."
	@ sudo docker start vk_pg
	@ sleep 0.1
	@ python3 manage.py makemigrations
	@ python3 manage.py migrate
	@ python3 manage.py runserver

test:
	@ echo "  >  running tests for project"
	@ sudo docker start vk_pg
	@ sleep 0.1
	@ echo "  >> testing friendship app"
	@ python3 manage.py test friendship
	@ echo "  >> testing users app"
	@ python3 manage.py test users


docker:
	@ sudo docker rmi -f friends_vk
	@ sudo docker build -t friends_vk .
	@ sudo docker compose up