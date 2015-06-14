cleardb:
	dropdb systori_local && createdb systori_local

clearmigrations:
	cd systori/apps && rm -rf accounting/migrations/ directory/migrations/ document/migrations/ project/migrations/ task/migrations/

makemigrations:
	./manage.py makemigrations accounting directory document equipment project task

migrate: cleardb clearmigrations makemigrations
	fab localdb_from_productiondb
	psql -f boardinghouse_pre_migrate.sql systori_local
	./manage.py migrate
	psql -f boardinghouse_post_migrate.sql systori_local
