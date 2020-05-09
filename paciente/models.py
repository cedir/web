from django.db import models
from datetime import date


class Paciente(models.Model):
    MASCULINO = 'Masculino'
    FEMENINO = 'Femenino'
    SEXOS = (
        (MASCULINO, MASCULINO),
        (FEMENINO, FEMENINO)
    )

    id = models.AutoField(primary_key=True)
    dni = models.IntegerField(unique=True)
    nombre = models.CharField(u"Nombre", max_length=200, db_column=u"nombres")
    apellido = models.CharField(u"Apellido", max_length=200)
    edad = models.IntegerField(blank=True, null=True)
    fechaNacimiento = models.DateField(blank=True, null=True)
    domicilio = models.CharField(u"Domicilio", max_length=200, db_column=u"direccion", blank=True)
    telefono = models.CharField(u"Telefono", max_length=200, db_column=u"tel", blank=True)
    sexo = models.CharField(max_length=50, choices=SEXOS, blank=True)
    nroAfiliado = models.CharField(u"Nro Afiliado", max_length=200, blank=True)
    email = models.CharField(u'Email', max_length=200, db_column=u"e_mail", blank=True, null=True)

    @property
    def _edad(self):
        return self.get_edad()

    def get_edad(self):
        if not self.fechaNacimiento:
            return None

        today = date.today()
        return today.year - self.fechaNacimiento.year - ((today.month, today.day) < (self.fechaNacimiento.month, self.fechaNacimiento.day))

    class Meta:
        db_table = u'tblPacientes'

    def __unicode__(self):
        return u'%s, %s' % (self.apellido, self.nombre)

