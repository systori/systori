MAKEFLAGS += -s

define PAPER_ASCIIART
##########################################################################
##########################################################################
##########                       SYSTORI                       ###########
##########################################################################
##########################################################################
endef

build_base:
	docker build -f .devcontainer/app/base.Dockerfile --build-arg requirements_file=base.pip -t hub.docker.com/elmcrest/systori:base .

build_app:
	docker build -f .devcontainer/app/app.Dockerfile --build-arg requirements_file=app.pip -t hub.docker.com/elmcrest/systori:latest .

build_test:
	docker build -f .devcontainer/app/test.Dockerfile --build-arg requirements_file=test.pip -t hub.docker.com/elmcrest/systori:test .

build_dev:
	docker build -f .devcontainer/app/dev.Dockerfile --build-arg requirements_file=dev.pip -t hub.docker.com/elmcrest/systori:dev .

refresh_all:
	make build_base
	make build_app
	make build_test
	make build_dev

first_run:
	docker volume create --name=systori_postgres_data
	make refresh_all
	
