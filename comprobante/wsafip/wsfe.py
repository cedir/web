
import hashlib, datetime, email, os, sys, time, traceback, warnings
from pysimplesoap.client import SimpleXMLElement
from M2Crypto import BIO, Rand, SMIME, SSL


# TODO
#pysimplesoap==1.08.8
#m2crypto>=0.18





# Constantes (si se usa el script de linea de comandos)
WSDL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"  # El WSDL correspondiente al WSAA 
CERT = "reingart.crt"        # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = "reingart.key"  # La clave privada del certificado CERT
PASSPHRASE = "xxxxxxx"  # La contrasena para firmar (si hay)
SERVICE = "wsfe"        # El nombre del web service al que se le pide el TA

# WSAAURL: la URL para acceder al WSAA, verificar http/https y wsaa/wsaahomo
#WSAAURL = "https://wsaa.afip.gov.ar/ws/services/LoginCms" # PRODUCCION!!!
WSAAURL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms" # homologacion (pruebas)
SOAP_ACTION = 'http://ar.gov.afip.dif.facturaelectronica/' # Revisar WSDL
SOAP_NS = "http://wsaa.view.sua.dvadac.desein.afip.gov"     # Revisar WSDL 

# Verificacion del web server remoto, necesario para verificar canal seguro
CACERT = "conf/afip_ca_info.crt" # WSAA CA Cert (Autoridades de Confiaza)

HOMO = False
TYPELIB = False
DEFAULT_TTL = 60*60*5       # five hours
DEBUG = False

class WSFEv1(object):





if __name__=="__main__":

    cache = None
    wsdl = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
    proxy = ""
    wrapper = ""    # "pycurl" para usar proxy avanzado / propietarios
    cacert = None   # "afip_ca_info.crt" para verificar canal seguro

    wsfev1 = WSFEv1()
    wsfev1.Conectar(cache, wsdl, proxy, wrapper, cacert)

    print "first approach!"
    
