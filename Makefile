MAKEFLAGS += -s

define PAPER_ASCIIART
##########################################################################
##########################################################################
##########                       SYSTORI                       ###########
##########################################################################
##########################################################################
endef

build_base:
	docker build -f .devcontainer/app/base.Dockerfile --build-arg requirements_file=base.pip -t elmcrest/systori:base .

build_app:
	docker build -f .devcontainer/app/app.Dockerfile --build-arg requirements_file=app.pip -t elmcrest/systori:latest .

build_test:
	docker build -f .devcontainer/app/test.Dockerfile --build-arg requirements_file=test.pip -t elmcrest/systori:test .

build_dev:
	docker build -f .devcontainer/app/dev.Dockerfile --build-arg requirements_file=dev.pip -t elmcrest/systori:dev .

refresh_containers:
	make build_base
	make build_app
	make build_test
	make build_dev

push_containers:
    push elmcrest/systori:base
	push elmcrest/systori:app
	push elmcrest/systori:test
	push elmcrest/systori:dev

build_dart1x:
	docker-compose up -d dart1x
	docker exec systori_dart1x_1 bash -c "cd app && pub get && pub build"

first_run:
	docker volume create --name=systori_postgres_data
	make refresh_containers
	make build_dart1x
	
