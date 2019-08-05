'''
Este script complementa los unit tests de la clase comprobante.Afip
Mientras que los unit tests funcionan aisladamente y solo testean nuestra logica,
Este script interactua con la API de  (entorno de tests) de la AFIP.
ATENCION: esto emite comprobantes contra la url y con los certificados configurados en settings.py
O sea qe si lo corres en produccion, facturas en falso :)
De todas formas, todos los montos estan en centavos.

Para correrlo contra el entorno de test, se necesitan las urls correctas y certificados de homologacion.
Tener en cuenta que el servicio de homologacion se cae bastante.
'''


# Correccion del path para importar desde el directorio padre
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import wsgi # Importar esto hace lo de las settings e inicia django

from comprobante.models import Comprobante
from comprobante.afip import Afip
from settings import CEDIR_CERT_PATH, CEDIR_PV_PATH, CEDIR_CUIT, BRUNETTI_CERT_PATH, BRUNETTI_PV_PATH, BRUNETTI_CUIT

def init():
    afip_cedir = Afip(CEDIR_PV_PATH, CEDIR_CERT_PATH, CEDIR_CUIT)
    afip_brunetti = Afip(BRUNETTI_PV_PATH, BRUNETTI_CERT_PATH, BRUNETTI_CUIT)

    # Emitir un comprobante

    # Pedir el comprobante por numero y ver que da bien
