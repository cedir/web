from django.db import models
from medico.models import Medico


class Usuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="idUsuario")
    nombreUsuario = models.CharField("Nombre Usuario",max_length=200, null=False,blank=False)
    password = models.CharField("Password",max_length=200, null=False,blank=False)
    #idAtorizacion = models.IntegerField()
    medico = models.ForeignKey(Medico, db_column="idMedico")

    class Meta:
        db_table = 'webData\".\"tblUsuarios'


class GrupoUsuarios(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'webData\".\"gruposUsuarios'


# class Linea(models.Model): #Esto que hace aca...
#     id = models.AutoField(primary_key=True)
#     idCaja = models.IntegerField()
#     descripcion = models.CharField()
#     monto = models.DecimalField()
#
#     def __unicode__ (self):
#         return self.descripcion
#
#     class Meta:
#         db_table = 'cedirData\".\"tblCajaMovimientos'


class AuditLog(models.Model):
    userActionId = models.IntegerField()
    objectTypeId = models.IntegerField()
    objectId = models.IntegerField()
    dateTime = models.CharField(max_length=200, null=False, blank=False)
    observacion = models.CharField(max_length=300)
    user = models.ForeignKey(Usuario, db_column="userId")

    class Meta:
        db_table = u'cedirData\".\"AuditUserActionsLog'