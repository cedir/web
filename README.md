# CEDIR WEB

### AFIP

Para la pylib de la afip, pip clonará el repo correspondiente desde git. Solo instalamos las dependencias necesarias para los modulos que vamos a usar, para no inflar las dependencias.
Para poder usarla, es necesario agregar al directorio de trabajo un certificado y su clave privada. En entornos de desarrollo será un certificado emitido para la api de homologacion y en produccion será uno de la api de produccion de producción.

Links importantes:

https://www.pyafipws.com.ar/

https://github.com/reingart/pyafipws.git

https://groups.google.com/forum/#!forum/pyafipws

## Steps to start with the project

1 - Install virtualenv: pip install virtualenv
2 - Create virtual environment: virtualenv cedir
3 - Activate virtual environment inside the directory created by virtualenv: source bin/activate
4 - Clone git repository: git clone https://github.com/cedir/web
5 - Install libraries inside web directory: pip install -r requeriments.txt
7 - Install postgres and pgadmin4 with your operative system's package manager
8 - Start pgadmin4 and create the admin user
9 - In pgadmin4, go to file -> preferences -> Binary paths -> PostgreSQL Binary Path, and paste the directory where psql is installed (usually /usr/bin)
   If you don't know where postgres is installed, execute sudo find / -name "psql"
10 - Create the database inside the postgres terminal:
         sudo su postgres -l
         initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data/'
         exit
11 - Start postgres service:
     sudo systemctl enable --now postgresql.service
     sudo systemctl start postgresql.service
12 - Restore database: psql -h localhost -F p -d nombre_base_de_datos < ./db.out
13 - Create file settings.py, containing the database credentials and the directory where the logs will be saved, in the directory where manage.py is.
14 - Execute tests: python manage.py tests (see Troubleshooting)
15 - Install nodejs with your operative system's package manager
16 - Install dependencies: npm install
17 - Run server: python manage.py runserver

### Troubleshooting:

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

