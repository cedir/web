# CEDIR WEB

## AFIP

Para la pylib de la afip, pip clonará el repo correspondiente desde git. Solo instalamos las dependencias necesarias para los modulos que vamos a usar, para no inflar las dependencias.
Para poder usarla, es necesario agregar al directorio de trabajo un certificado y su clave privada. En entornos de desarrollo será un certificado emitido para la api de homologacion y en produccion será uno de la api de produccion de producción.

Links importantes:

https://www.pyafipws.com.ar/

https://github.com/reingart/pyafipws.git

https://groups.google.com/forum/#!forum/pyafipws

## Steps to start with the project

- Install virtualenv: `pip install virtualenv`
- Create virtual environment: `virtualenv cedir -p python3.7`
- Activate virtual environment inside the directory created by virtualenv: `source bin/activate`
- Clone git repository: `git clone https://github.com/cedir/web`
- Install required dependencies `sudo apt install swig libssl-dev python3.7-dev`
- Install libraries inside web directory: `pip install -r requeriments.txt`
- Install postgres and pgadmin4 with your operative system's package manager
- Start pgadmin4 and create the admin user
- In pgadmin4, go to file -> preferences -> Binary paths -> PostgreSQL Binary Path, and paste the directory where psql is installed (usually /usr/bin)

   If you don't know where postgres is installed, execute sudo find / -name "psql"

- Create the database inside the postgres terminal:

      sudo su postgres -l

      initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data/'

      exit

- Start postgres service:

   sudo systemctl enable --now postgresql.service

   sudo systemctl start postgresql.service

- Restore database: `psql -h localhost -F p -d nombre_base_de_datos < ./db.out`
- Create file settings.py, containing the database credentials and the directory where the logs will be saved, in the directory where manage.py is. You can use settings.py.bak as a template: `cp settings.py.bak settings.py`.
- Execute tests: `python manage.py tests` (see Troubleshooting)
- Install nodejs with your operative system's package manager
- Install dependencies: `npm install`
- Run server: `python manage.py runserver`

### Troubleshooting

- Permision denied: '.../debug.log':

      Give permision to write on the logs directory.

- OperationalError: Problem installing fixtures: no such table: name_table__old:

      In the directory where the virtual environment is, go to 

         lib/python2.7/site-packages/django/db/backends/sqlite3

      open the file "schema.py"

      in the function __enter__, below the line:

         c.execute('PRAGMA foreign_keys = 0'),

      paste the next line:

         c.execute('PRAGMA legacy_alter_table = ON')

- Error while running `pip install -r requirements.txt`

   Make sure you Install the required libs: `sudo apt-get install swig libssl-dev python3-dev`

## Testing

Con el virtualenv activado, podes:

- Correr los Unit Tests con  `python manage.py test`
- Correr los Integration Tests con Postman: abrri el servidor de testing con `python manage.py runserver` y abrí el botón "Runner" de Postman. Setea el enviroment a `Local` y tickea el box de `Save responses`. Seleccciona la coleccion y apretá "Run CEDIR Collection".
  - Los tests corren en un orden especifico. Para agregar tests a una request nueva, anda a la última y agregale una linea de `postman.setNextRequest('nombre de tu request')`. En tu request, anda ala pestaña "test" y agregalo ahí. Los tests se escriben en javascript y usan una API de Postman. Basate en los otros. La ultima tiene que quedar con `postman.setNextRequest(null)` para que no entre en un loop.
  - Los tests van guardando estado. El POST de /presentacion por ejemplo guarda la id para usarla despues en el PATCH de cerrar

## CI

El repo usa Travis para correr varias pruebas en el codigo cada vez que pusheamos:

- Corre pylint en modo solo errores.
- Corre los unit tests.
- Corre los integration tests con Newman (la version CLI de Postman) segun lo que esté especificado en los dumps de la colección en la carpeta `integration_tests`. Para exportar, en Postman dale click derecho a la colección -> export -> 2.1 -> reemplazas el `cedir_web.postman_collection.json`. Si tuviste que agregar algo al enviroment, fijate de ponerlo tambien en el enviroment `staging` y exportá `local` con ⚙️ -> Local -> ⬇️ -> reemplaza el `local.postman_environment.json`.
- El informe mensual de comprobantes tarda muchisimo en correr, asi que tratá de dejarlo último para acelerar el testing manual.
