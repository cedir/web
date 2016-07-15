from django.db import models
from datetime import date


class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    dni = models.IntegerField()
    nombre = models.CharField(u"Nombre", max_length=200, db_column=u"nombres")
    apellido = models.CharField(u"Apellido", max_length=200)
    edad = models.IntegerField()
    fechaNacimiento = models.DateField()
    domicilio = models.CharField(u"Domicilio", max_length=200, db_column=u"direccion")
    telefono = models.CharField(u"Telefono", max_length=200, db_column=u"tel")
    sexo = models.CharField(max_length=50)
    nroAfiliado = models.CharField(u"Nro", max_length=200)
    email = models.CharField(u'Email', max_length=200, db_column=u"e_mail")

    def get_edad(self):
        if not self.fechaNacimiento:
            return None

        today = date.today()
        return today.year - self.fechaNacimiento.year - ((today.month, today.day) < (self.fechaNacimiento.month, self.fechaNacimiento.day))

    class Meta:
        db_table = u'tblPacientes'

    def __unicode__(self):
        return u'%s, %s' % (self.nombre, self.apellido)

