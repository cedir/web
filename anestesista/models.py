from __future__ import unicode_literals
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError
from comprobante.models import LineaDeComprobante
from paciente.models import Paciente
from obra_social.models import ObraSocial
from practica.models import Practica


class Anestesista(models.Model):
    id        = models.AutoField(primary_key=True, db_column="idMedicoAn")
    nombre    = models.CharField("Nombre",max_length=200, db_column="nombreMedicoAn")
    apellido  = models.CharField("Apellido",max_length=200, db_column="apellidoMedicoAn")
    matricula = models.CharField("Matricula",max_length=200, db_column="nroMatricula", null=True, blank=True)
    direccion = models.CharField("Direccion",max_length=200, db_column="direccionMedico", null=True, blank=True)
    localidad = models.CharField("Localidad",max_length=200, db_column="localidadMedico", null=True, blank=True)
    telefono  = models.CharField("Telefono",max_length=200, db_column="telMedico", null=True, blank=True)
    email     = models.EmailField("E-mail",max_length=200, db_column="mail", null=True, blank=True)
    porcentaje_anestesista = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))

    def __unicode__ (self):
        return u'%s, %s' % (self.apellido, self.nombre, )

    class Meta:
        managed = False
        db_table = 'tblMedicosAnestesistas'
        ordering = [u'apellido']


class PagoAnestesistaVM(object):
    pass



class LineaPagoAnestesistaVM(object):
    pass


class ComplejidadEstudio(models.Model):
    estudios = models.CharField(max_length=500)
    formula = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'tblComplejidadEstudios'

    @property
    def practicas(self):
        practicas_ids = self.estudios.split(',')
        practicas = Practica.objects.filter(id__in=practicas_ids)
        return map(lambda p: '{}'.format(p), practicas)

    def clean(self):
        """Para que el filtro de complefidadEstudio funcione, debe estar guardado en forma ascendente"""

        if ' ' in self.estudios:
            raise ValidationError("Los estudios (practicas IDs) deben estar separados por comas y sin espacios")

        practicas_ids = self.estudios.split(u',')
        init = 0
        for pid in practicas_ids:
            try:
                pid = int(pid)
            except ValueError:
                raise ValidationError("Algun estudio (practica ID) contiene un valor NO valido como numero.")

            if init > pid:
                raise ValidationError("Error: Las pracitcas (estudios) no estan ordenadas en forma ascendente: {} ".format(pid))
            init = pid
            try:
                practica = Practica.objects.get(pk=pid)
            except Practica.DoesNotExist:
                raise ValidationError("Error: Practica con ID {} no existe".format(pid))


class Complejidad(models.Model):
    importe = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblComplejidades'


#class PagoAnestesista(models.Model):
#    anestesista = models.ForeignKey(Anestesista)
#    anio = models.IntegerField()
#    mes = models.IntegerField()
#    creado = models.DateTimeField(auto_now_add=True)
#    modificado = models.DateTimeField(auto_now=True)

#class LineaPagoAnestesista(models.Model):
#    pago = models.ForeignKey(PagoAnestesista, related_name="lineas")
#    paciente = models.ForeignKey(Paciente)
#    obra_social = models.ForeignKey(ObraSocial)
#    estudios = models.ManyToManyField('estudio.Estudio')
#    es_paciente_diferenciado = models.BooleanField()
#    formula = models.CharField(max_length=200)
#    formula_valorizada = models.CharField(max_length=500)
#    importe = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
#    alicuota_iva = models.DecimalField(max_digits=16, decimal_places=2, default='0.00')
#    porcentaje_anestesista = models.DecimalField(max_digits=2, decimal_places=2, default='0.00')





