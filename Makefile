# Data dump files.
DUMP_FILE=export/database/db.json

# Backup file.
BACKUP_DUMP_FILE=export/database/db.backup.`date +'%Y-%m-%d-%H%M'`.json

# Default settings module.
DJANGO_SETTINGS_MODULE := biostar.recipes.settings

# Default app.
DJANGO_APP := biostar.recipes

# Database name
DATABASE_NAME := database.db

# Search index name
INDEX_NAME := index

# Search index directory
INDEX_DIR := search

# Recipes database to copy
COPY_DATABASE := recipes.db

all: recipes serve

accounts:
	$(eval DJANGO_SETTINGS_MODULE := biostar.accounts.settings)
	$(eval DJANGO_APP := biostar.accounts)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}


emailer:
	$(eval DJANGO_SETTINGS_MODULE := biostar.emailer.settings)
	$(eval DJANGO_APP := biostar.emailer)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}

pg:
	$(eval DJANGO_SETTINGS_MODULE := conf.examples.pg.forum_settings)
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}


recipes:
	$(eval DJANGO_SETTINGS_MODULE := biostar.recipes.settings)
	$(eval DJANGO_APP := biostar.recipes)
	$(eval UWSGI_INI := conf/uwsgi/engine_uwsgi.ini)
	$(eval ANSIBLE_HOST := hosts/www.bioinformatics.recipes)
	$(eval ANSIBLE_ROOT := conf/ansible)
	$(eval SUPERVISOR_NAME := recipes)
	$(eval ENGINE_DIR := /export/www/biostar-central)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	@echo DATABASE_NAME=${DATABASE_NAME}


chat:
	$(eval DJANGO_SETTINGS_MODULE := biostar.chat.settings)
	$(eval DJANGO_APP := biostar.chat)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	@echo DATABASE_NAME=${DATABASE_NAME}


bioconductor:
	$(eval DJANGO_SETTINGS_MODULE := themes.bioconductor.settings)
	$(eval DJANGO_APP := biostar.forum)
	$(eval UWSGI_INI := themes/bioconductor/conf/uwsgi.ini)
	$(eval ANSIBLE_HOST := supportupgrade.bioconductor.org)
	$(eval ANSIBLE_ROOT := themes/bioconductor/conf/ansible)
	$(eval SUPERVISOR_NAME := forum)
	$(eval ENGINE_DIR := /export/www/biostar-central)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	@echo DATABASE_NAME=${DATABASE_NAME}


forum:
	$(eval DJANGO_SETTINGS_MODULE := biostar.forum.settings)
	$(eval DJANGO_APP := biostar.forum)
	$(eval UWSGI_INI := conf/uwsgi/forum_uwsgi.ini)
	$(eval ANSIBLE_HOST := hosts/test.biostars.org)
	$(eval ANSIBLE_ROOT := conf/ansible)
	$(eval SUPERVISOR_NAME := engine)
	$(eval ENGINE_DIR := /export/www/biostar-engine)

	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	@echo DATABASE_NAME=${DATABASE_NAME}

serve:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py runserver --settings ${DJANGO_SETTINGS_MODULE}

init:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py collectstatic --noinput -v 0  --settings ${DJANGO_SETTINGS_MODULE}
	python manage.py migrate -v 0  --settings ${DJANGO_SETTINGS_MODULE}

load:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py loaddata --ignorenonexistent --settings ${DJANGO_SETTINGS_MODULE} $(DUMP_FILE)

delete:
	# Delete the database, logs and CACHE files.
	# Keep media and spooler.
	rm -rf export/logs/*.log
	rm -f export/db/${DATABASE_NAME}
	rm -rf export/static/CACHE
	rm -rf *.egg
	rm -rf *.egg-info

# Resets the site without removing jobs.
reset: delete init
    # Initializes the test project.

copy: reset
	@echo COPY_DATABASE=${COPY_DATABASE}
	python manage.py copy --db ${COPY_DATABASE} --settings ${DJANGO_SETTINGS_MODULE}

test:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	#python manage.py test ${DJANGO_APP} --settings ${DJANGO_SETTINGS_MODULE} -v 2 --failfast
	coverage run manage.py test ${DJANGO_APP} --settings ${DJANGO_SETTINGS_MODULE} -v 2 --failfast
	coverage html --skip-covered

test_all:
	#python manage.py test --settings biostar.test.test_settings -v 2 --failfast
	coverage run manage.py test --settings biostar.test.test_settings -v 2 --failfast
	coverage html --skip-covered

test_pg:
	#python manage.py test --settings biostar.test.pg_test_settings -v 2 --failfast
	coverage run manage.py test --settings biostar.test.pg_test_settings -v 2 --failfast
	coverage html --skip-covered

index:
	@echo INDEX_NAME=${INDEX_NAME}
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py index --settings ${DJANGO_SETTINGS_MODULE} --index 130000 --report

reindex:
	@echo INDEX_NAME=${INDEX_NAME}
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py index --remove --reset --index 130000 --settings ${DJANGO_SETTINGS_MODULE}

recipes_demo: recipes reset init load_recipes serve

forum_demo: forum reset init load_forum serve

load_recipes:
	python manage.py project --pid test --name "Test Project" --public
	python manage.py recipe --pid test --rid hello --json biostar/recipes/recipes/hello-world.hjson

load_forum:
	python manage.py populate --n_users 10 --n_posts 10 --settings ${DJANGO_SETTINGS_MODULE}

hard_reset: delete
	# Delete media and spooler.
	rm -rf export/spooler/*spool*
	rm -rf export/media/*

dump:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo DJANGO_APP=${DJANGO_APP}
	python manage.py dumpdata --settings ${DJANGO_APP} --settings ${DJANGO_SETTINGS_MODULE} --exclude auth.permission --exclude contenttypes  > $(DUMP_FILE)
	@cp -f $(DUMP_FILE) $(BACKUP_DUMP_FILE)
	@ls -1 export/database/*.json

uwsgi:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	@echo UWSGI_INI=${UWSGI_INI}
	uwsgi --ini ${UWSGI_INI}

pg_drop:
	dropdb --if-exists ${DATABASE_NAME}
	createdb ${DATABASE_NAME}

transfer:
	python manage.py migrate --settings conf.examples.pg.forum_settings
	python manage.py transfer -n 300 --settings biostar.transfer.settings

next:
	@echo DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
	python manage.py job --next --settings ${DJANGO_SETTINGS_MODULE}

config:
	(cd ${ANSIBLE_ROOT} && ansible-playbook -i ${ANSIBLE_HOST} config.yml --extra-vars -v)

install:
	(cd ${ANSIBLE_ROOT} && ansible-playbook -i ${ANSIBLE_HOST} install.yml --ask-become-pass --extra-vars -v)

deploy:
	(cd ${ANSIBLE_ROOT} && ansible-playbook -i ${ANSIBLE_HOST} server-deploy.yml --ask-become-pass --extra-vars "supervisor_program=${SUPERVISOR_NAME} restart=True engine_dir=${ENGINE_DIR}"  -v)
