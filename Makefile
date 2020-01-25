MAKEFLAGS += -s

define PAPER_ASCIIART
##########################################################################
##########################################################################
##########                       SYSTORI                       ###########
##########################################################################
##########################################################################
endef

build_base:
	docker build -f .devcontainer/app/base.Dockerfile --build-arg requirements_file=base.pip -t docker.pkg.github.com/systori/systori/base:latest .

push_base:
	docker push docker.pkg.github.com/systori/systori/base:latest

build_app:
	docker build -f .devcontainer/app/app.Dockerfile --build-arg requirements_file=app.pip -t docker.pkg.github.com/systori/systori/app:latest .

push_app:
	docker push docker.pkg.github.com/systori/systori/app:latest

build_dev_base:
	docker build -f .devcontainer/app/test.Dockerfile --build-arg requirements_file=test.pip -t docker.pkg.github.com/systori/systori/dev_base:latest .

push_dev_base:
	docker push docker.pkg.github.com/systori/systori/dev_base:latest

build_dev:
	docker build -f .devcontainer/app/dev.Dockerfile --build-arg requirements_file=dev.pip -t docker.pkg.github.com/systori/systori/dev:latest .

push_dev:
	docker push docker.pkg.github.com/systori/systori/dev:latest

refresh_containers:
	make build_base
	make build_app
	make build_dev_base
	make build_dev

push_containers:
	make push_base
	make push_app
	make push_dev_base
	make push_dev

refresh_and_push_containers:
	make refresh_containers
	make push_containers

build_dart1x:
	docker-compose up -d dart1x
	docker exec systori_dart1x_1 bash -c "cd app && pub get && pub build"

first_run:
	docker volume create --name=systori_postgres_data
	make refresh_containers
	make build_dart1x
	
