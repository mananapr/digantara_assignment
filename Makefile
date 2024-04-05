help:
	@echo "build  Builds the docker image"
	@echo "up     Runs the containers as specified in docker-compose.yml"
	@echo "down   Stops the containers"

build:
	docker build -t digantara .

up:
	docker-compose up

down:
	docker-compose down
