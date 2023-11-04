all: clean deploy

# BUILD
build:
	docker-compose -f docker-compose.yaml build

# DEPLOY
deploy:
	docker-compose -f docker-compose.yaml up

# CLEAN
clean:
	docker-compose -f docker-compose.yaml down
