#!/usr/bin/python
# -*- coding: utf8 -*-
#pylint: disable=unused-import,wrong-import-position,invalid-name
import psycopg2

try:
    connection = psycopg2.connect(user="***",
                                  password="***",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="cedir_web_data")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print (connection.get_dsn_parameters(), "\n")

    alter_query = """ALTER TABLE "AlmacenPreciosEstOS" ADD COLUMN "id" bigint;"""
    cursor.execute(alter_query)
    select_query = "SELECT * FROM \"AlmacenPreciosEstOS\""
    update_query = """UPDATE "AlmacenPreciosEstOS" SET id = %s WHERE "idEstudio" = %s AND "idObraSocial" = %s"""
    cursor.execute(select_query)
    arancel_records = cursor.fetchall()
    id_counter = 0
    for row in arancel_records:
        id_estudio = row[0]
        id_obra_social = row[1]
        cursor.execute(update_query, (id_counter, id_estudio, id_obra_social))
        id_counter += 1
        connection.commit()
        print(cursor.rowcount, "Record Updated successfully")

except psycopg2.Error as error:
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print "PostgreSQL connection is closed"
