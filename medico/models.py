#-*- coding: utf-8 -*-
from django.db import models
from django.db import connection

from sala.models import Sala

RESPONSABILIDADES_FISCALES = (('INSCRIPTO', 'INSCRIPTO'),
                              ('MONOTRIBUTO', 'MONOTRIBUTO'))

class Medico(models.Model):
    id = models.AutoField(primary_key=True, db_column="idMedicoAct")
    nombre = models.CharField("Nombre", max_length=200, \
                              db_column="nombreMedicoAct")
    apellido = models.CharField("Apellido", max_length=200, \
                                db_column="apellidoMedicoAct")
    domicilio = models.CharField("Domicilio", max_length=200, \
                                 db_column="direccionMedico", blank=True)
    localidad = models.CharField("Localidad", db_column="localidadMedico", \
                                 max_length=200, blank=True)
    telefono = models.CharField("Teléfono", max_length=200, \
                                db_column="telMedico", blank=True)
    matricula = models.CharField("Matrícula", max_length=200, \
                                 db_column="nroMatricula", blank=True)
    mail = models.CharField("Mail", max_length=200, \
                            db_column="mail", blank=True)
    clave_fiscal = models.CharField("Clave Fiscal", max_length=200, \
                                    db_column="claveFiscal", blank=True, default="")
    responsabilidad_fiscal = models.CharField('Responsabilidad Fiscal', \
                                              db_column='responsabilidadFiscal',
                                              max_length=200, choices=RESPONSABILIDADES_FISCALES, \
                                              default='MONOTRIBUTO')

    facturar_amr_en_nombre_de_medico = models.ForeignKey('self', models.SET_NULL, related_name='facturar_amr_medico', blank=True, null=True)
    facturar_osde_en_nombre_de_medico = models.ForeignKey('self', models.SET_NULL, related_name='facturar_osde_medico', blank=True, null=True)

    def __str__(self):
        return '%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        db_table = 'tblMedicosAct'
        ordering = ['apellido']

    #TODO: resolver duplicación de tablas de médicos y luego borrar este método.
    def save(self, *args, **kwargs):
        '''
        La tabla de medicos esta duplicada, en tblMedicoAct y tblMedicoSol.
        Por eso, cuando guardamos algo, tenemos que duplicar el cambio en la segunda.
        El SQL crudo se llama antes de la superclase para poder diferenciar según si
        hay o no self.id .

        Esto es vulnerable a SQL Injection y no tienen arreglo mas que arreglar lo de arriba.

        La magia negra de comillas es porque en PostgreSQL las columnas van entre comillas dobles y
        las strings entre simples.

        Fede@Septiembre 2018.
        '''
        valores = (self.nombre, \
                   self.apellido, \
                   self.matricula, \
                   self.domicilio, \
                   self.localidad, \
                   self.telefono, \
                   self.mail, \
                   self.clave_fiscal, \
                   self.responsabilidad_fiscal)
        # Si la instancia tiene id, es un update. Sino, es un insert.
        if self.id is None:
            columnas = ("nextval('tblmedicossol_idmedicosol_seq'), " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s', " \
                        + "'%s'")
            fila = columnas % valores
            query = 'INSERT INTO public."tblMedicosSol" VALUES (%s);' % fila
        else:
            columnas = ('"nombreMedicoSol"=\'%s\', ' \
                        + '"apellidoMedicoSol"=\'%s\', ' \
                        + '"nroMatricula"=\'%s\', ' \
                        + '"direccionMedico"=\'%s\', ' \
                        + '"localidadMedico"=\'%s\', ' \
                        + '"telMedico"=\'%s\', ' \
                        + '"mail"=\'%s\', ' \
                        + '"claveFiscal"=\'%s\', ' \
                        + '"responsabilidadFiscal"=\'%s\'')
            fila = columnas % valores
            query = ('UPDATE public."tblMedicosSol" SET %s ' \
                     + 'WHERE "tblMedicosSol"."idMedicoSol"=%i;') \
                     % (fila, self.id)
        with connection.cursor() as cursor:
            cursor.execute(query)
        super(Medico, self).save(*args, **kwargs)


class Disponibilidad(models.Model):
    dia = models.CharField(max_length=20)
    horaInicio = models.CharField(db_column="hora_inicio", max_length=20)
    horaFin = models.CharField(db_column="hora_fin", max_length=20)
    fecha = models.CharField(max_length=100)
    medico = models.ForeignKey(Medico)
    sala = models.ForeignKey(Sala)

    def getDuracionEnMinutos(self):
        return (self.horaFin.hour * 60 + self.horaFin.minute) - (self.horaInicio.hour * 60 + self.horaInicio.minute)

    class Meta:
        db_table = 'turnos_disponibilidad_medicos'


class PagoMedico(models.Model):
    id = models.AutoField(primary_key=True, db_column='nroPago')
    fecha = models.DateField(db_column='fechaPago')
    medico = models.ForeignKey(Medico, db_column='idMedico')
    observacion = models.TextField(db_column='observacionPago')

    class Meta:
        db_table = 'tblPagosMedicos'
