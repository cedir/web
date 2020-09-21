from django.db import models


class Sala(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    observaciones = models.CharField(max_length=200)

    class Meta:
        db_table = 'turnos_salas'

    def __str__(self):
        return str(self.nombre)
