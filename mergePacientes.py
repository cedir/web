#!/usr/bin/env python

from django.core.management import setup_environ
import settings
setup_environ(settings)

from managers.model.personas import *
from managers.model.turno import *
from datetime import date


def calculate_age(born):
    today = date.today()
    try: 
        birthday = born.replace(year=today.year)
    except ValueError: # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year

def calculate_borndate(age):
 if age >= 100 or age < 1:
  return None
 born = date.today()
 year = born.year - age 
 birthday = born.replace(year=year)
 return birthday

rowCount = 0
arrPaciente = Paciente.objects.all()[:20]
for paciente in arrPaciente:
 b = calculate_borndate(int(paciente.edad))
 print "pac: " + str(paciente.id) + " edad: " + str(paciente.edad)
 if (b is not None): 
  print "Fecha: " + str(b)
  paciente.fechaNacimiento = b
  paciente.save()
 else:
  print "skipping.."
 rowCount +=1

print "fin Cant de pacientes: " + str(rowCount)
