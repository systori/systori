import json
import os
import sys
from fabric.api import cd, env, get, lcd, local, prefix, run, sudo
from fabric.context_managers import shell_env

env.hosts = ["elmcrest@metal.systorigin.de"]

PROD_MEDIA_PATH = "/var/lib/systori/production"
PROD_MEDIA_FILE = "systori.media.tgz"


def test():
    "django continuous integration test"
    with shell_env(DJANGO_SETTINGS_MODULE="systori.settings.test"):
        local("coverage run -p manage.py test --verbosity 3 systori.apps systori.lib")
        local("coverage combine")
        local("coverage html -d reports")


def run_tests(parallel=2):
    local("python manage.py collectstatic --noinput")
    local(
        f"DJANGO_SETTINGS_MODULE='systori.settings.test' python manage.py test --parallel={parallel} systori.apps systori.lib"
    )
    local(f"python manage.py test --parallel={parallel} systori.apps systori.lib")


def makemessages():
    "django makemessages"
    local("./manage.py makemessages -l de -e html,py")


def getmedia():
    "download production media files"
    with cd(PROD_MEDIA_PATH):
        run("tar -cz media -f /tmp/" + PROD_MEDIA_FILE)
    get("/tmp/" + PROD_MEDIA_FILE, PROD_MEDIA_FILE)
    local("tar xfz " + PROD_MEDIA_FILE)
    local("rm " + PROD_MEDIA_FILE)
    run("rm /tmp/" + PROD_MEDIA_FILE)


def fetchdb(envname="production"):
    ":envname=production -- fetch remote database, see getdb"
    container = "systori_postgres11_1"
    dbname = "systori_" + envname
    dump_file = "systori." + envname + ".dump"
    dump_folder = "/var/lib/postgresql/dumps"
    dump_path = os.path.join(dump_folder, dump_file)
    mapped_folder = "/var/lib/postgresql11/dumps"
    mapped_path = os.path.join(mapped_folder, dump_file)
    # -Fc : custom postgresql compressed format
    run(
        "docker exec {container} pg_dump -U postgres -Fc -x -f {dump_path} {dbname}".format(
            **locals()
        )
    )
    print("before get()")
    get(mapped_path, dump_file)
    sudo("rm {}".format(mapped_path))


def getdb(envname="production"):
    ":envname=production -- fetch and load remote database"
    fetchdb(envname)
    local("dropdb systori_local --if-exists")
    local("createdb systori_local")
    local("pg_restore -d systori_local -O systori." + envname + ".dump")
    local('psql -c "ANALYZE" systori_local')
    local("rm systori." + envname + ".dump")


def dockergetdb(
    container="postgres11", envname="production", targetname="systori_local"
):
    ":container=app,envname=production -- fetch and load remote database"
    dump_file = "systori." + envname + ".dump"
    settings = {"NAME": targetname, "USER": "postgres", "HOST": "localhost"}
    fetchdb(envname)
    local("docker cp {0} systori_db_1:/{0}".format(dump_file))
    local(
        "docker exec systori_db_1 dropdb -h {HOST} -U {USER} {NAME} --if-exists".format(
            container, **settings
        )
    )
    local(
        "docker exec systori_db_1 createdb -h {HOST} -U {USER} {NAME}".format(
            container, **settings
        )
    )
    local(
        "docker exec systori_db_1 pg_restore -d {NAME} -O {1} -h {HOST} -U {USER}".format(
            container, dump_file, **settings
        )
    )
    local("rm " + dump_file)


def vscodegetdb(envname="production"):
    fetchdb(envname)
    local("dropdb -h db -U postgres systori_local --if-exists")
    local("createdb -h db -U postgres systori_local")
    local("pg_restore -d systori_local -O systori.production.dump -h db -U postgres")
    local("rm systori.production.dump")


def mail():
    "start mail debugging server"
    local("python -m smtpd -n -c DebuggingServer localhost:1025")


def dockercontextsize():
    "shows size of 'context' uploaded to docker when building docker image"
    local("du -X .dockerignore -h -d 2 | sort -h")


def refresh_sandbox_db():
    db_container = "systori_postgres11_1"
    db_source = "systori_production"
    db_target = "systori_sandbox"
    dump_file = f"{db_source}.dump"

    user = "postgres"
    # just cloning production db doesn't work without disconnecting all users
    run(f"docker exec {db_container} dropdb -U {user} {db_target} --if-exists")
    run(f"docker exec {db_container} createdb -U {user} -O {user} {db_target}")
    # -Fc compressed binary format to be used with pg_restore
    run(
        f"docker exec {db_container} pg_dump -U {user} -Fc -x -f {dump_file} {db_source}"
    )
    run(
        f"docker exec {db_container} pg_restore -U {user} -d {db_target} -O {dump_file}"
    )
    run(f"docker exec {db_container} rm {dump_file}")


def deploy_sandbox(build="yes", db="yes"):
    ":build=true and deploy sandbox image"
    local("source .environment")
    if "yes" in build:
        local("docker-compose build app_sandbox")
        local("docker push elmcrest/systori:sandbox")
    # switch to metal
    with cd("infrastructure"):
        run("docker-compose stop sandbox")
        if "yes" in db:
            refresh_sandbox_db()
        if "yes" in build:
            run("docker-compose pull sandbox")
        run("docker-compose up -d sandbox")


def deploy_production():
    with cd("infrastructure"):
        run("docker tag elmcrest/systori:sandbox elmcrest/systori:production")
        run("docker-compose stop production")
        run("docker-compose up -d production")
