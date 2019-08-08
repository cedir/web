#pylint: disable=unused-import,wrong-import-position,invalid-name
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
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante
from comprobante.afip import Afip

def numero_comp_valido():
    #
    return 99999999

def main():
    # Se necesitan dos instancias porque cedir y brunetti facturan por separado.
    afip = Afip()


    # En la realidad podemos usar nuestro conteneo de numeros de comprobantes sin problemas,
    # pero aca no y de todas formas es util tener a mano esta info.
    numero = afip.consultar_proximo_numero("Cedir", 1, TipoComprobante.objects.get(pk=1), "B")
    
    # Esto es para poder usar la proxima id que pide afip y es un motivo fuerte para NO CORRER ESTE SCRIPT EN PRODUCCION!!
    try:
        Comprobante.objects.filter(nro_terminal=1, tipo_comprobante=TipoComprobante.objects.get(pk=1), numero=numero).delete()
    except Comprobante.DoesNotExist:
        pass
    
    # Creamos un comprobante
    comprobante = Comprobante.objects.create(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "11",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Cedir",
        "sub_tipo": "B",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 1,
        "total_facturado": "2800.00",
        "total_cobrado": "0.00",
        "fecha_emision": "2012-07-07",
        "fecha_recepcion": "2012-07-07",
        "tipo_comprobante": TipoComprobante.objects.get(pk=1),
    })
    linea = LineaDeComprobante.objects.create(**{
        "comprobante": comprobante,
        "importe_neto": "2800.00",
        "sub_total": "2800.00",
        "iva": "0",
    })

    # Emitimos el comprobante en la AFIP.
    afip.emitir_comprobante(comprobante)

    # Revisamos que los datos esten bien.
    print(comprobante.cae)
    print(comprobante.vencimiento_cae)

    # Le pedimos el comprobante a la AFIP y verificamos que los datos coincidan.
    print(afip.consultar_comprobante(comprobante))

if __name__ == "__main__":
    main()