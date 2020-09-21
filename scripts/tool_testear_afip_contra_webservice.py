#pylint: disable=unused-import,wrong-import-position,invalid-name
'''
Este script complementa los unit tests de la clase comprobante.Afip
Mientras que los unit tests funcionan aisladamente y solo testean nuestra logica,
Este script interactua con la API de  (entorno de tests) de la AFIP.

El script emite un comprobante de cada uno de los tipos validos que tenemos. (excepto liquidaciones, que son internas)

ATENCION: esto emite comprobantes contra la url y con los certificados configurados en settings.py
O sea qe si lo corres en produccion, facturas en falso :)

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
from datetime import date
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante
from comprobante.afip import Afip


def main():
    # Iniciamos el la conexion con la AFIP.
    afip = Afip()

    #########
    # Factura
    #########

    # En la realidad podemos usar nuestro conteneo de numeros de comprobantes sin problemas, (si no coinciden hay algun problema grave)
    # pero aca no y de todas formas es util tener a mano esta info.
    numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=1), "A")

    # Esto es para poder usar la proxima id que pide afip y es un motivo fuerte para NO CORRER ESTE SCRIPT EN PRODUCCION!!
    # (los numeros en homologacion y produccion no coincididen entonces en la DB dev tenemos colisiones de numero)
    # Comprobante.objects.filter(nro_terminal=91, tipo_comprobante=TipoComprobante.objects.get(pk=1), numero=numero).delete()

    # Creamos un Factura
    # Esto crea el objeto, pero no lo guarda en DB.
    factura = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Cedir",
        "sub_tipo": "A",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 91,
        "total_facturado": "2800.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=1),
    })
    # Creamos una linea de comprobante, parte necesaria de un comprobante para nuestro sistema.
    lineas_factura = [LineaDeComprobante(**{
        "comprobante": factura,
        "importe_neto": 2800.00,
        "sub_total": 2800.00,
        "iva": 0,
    })]

    # Emitimos el comprobante en la AFIP.
    afip.emitir_comprobante(factura, lineas_factura)

    # Revisamos que los datos esten bien.
    # Si la emicion funciono correctamente, los datos se setean directamente en el comprobante.
    print("FACTURA")
    print("-------")
    print((factura.cae))
    print((factura.vencimiento_cae))

    # Le pedimos el comprobante a la AFIP y verificamos que los datos coincidan.
    print((afip.consultar_comprobante(factura)))

    # Si la AFIP emitio bien, ahora se guardan.
    # Aca deberia haber codigo que hizo las verificaciones en realidad, pero esto es un PoC.
    # factura.save()
    # lineas_factura[0].save()

    #########
    # Nota de Debito
    #########
    numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=3), "A")
    nota_debito = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Cedir",
        "sub_tipo": "A",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 91,
        "total_facturado": "2800.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=3),
        "factura": factura  # Ponemos como comprobante asociado la factura que hicimos recien.
    })
    lineas_nota_debito = [LineaDeComprobante(**{
        "comprobante": nota_debito,
        "importe_neto": 2800.00,
        "sub_total": 2800.00,
        "iva": 0,
    })]
    afip.emitir_comprobante(nota_debito, lineas_nota_debito)
    print("NOTA DE DEBITO")
    print("--------------")
    print((nota_debito.cae))
    print((nota_debito.vencimiento_cae))
    print((afip.consultar_comprobante(nota_debito)))
    print("")

    #########
    # Nota de Credito
    #########
    numero = afip.consultar_proximo_numero("Cedir", 91, TipoComprobante.objects.get(pk=4), "A")
    nota_credito = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Cedir",
        "sub_tipo": "A",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 91,
        "total_facturado": "2800.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=4),
        "factura": nota_debito  # Ponemos como comprobante asociado la factura que hicimos recien.
    })
    lineas_nota_credito = [LineaDeComprobante(**{
        "comprobante": nota_credito,
        "importe_neto": 2800.00,
        "sub_total": 2800.00,
        "iva": 0,
    })]
    print("NOTA DE CREDITO")
    print("---------------")
    afip.emitir_comprobante(nota_credito, lineas_nota_credito)
    print((nota_credito.cae))
    print((nota_credito.vencimiento_cae))
    print((afip.consultar_comprobante(nota_credito)))
    print("")

    #######################################
    # Factura de Credito Electronica MiPyME
    #######################################

    numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=5), "B")
    factura_electronica = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Brunetti",
        "sub_tipo": "B",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 3,
        "total_facturado": "100000.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=5),
    })
    lineas_factura_electronica = [LineaDeComprobante(**{
        "comprobante": factura_electronica,
        "importe_neto": 100000.00,
        "sub_total": 100000.00,
        "iva": 0,
    })]
    print("FACTURA MIPYME")
    print("--------------")
    afip.emitir_comprobante(factura_electronica, lineas_factura_electronica)
    print((factura_electronica.cae))
    print((factura_electronica.vencimiento_cae))
    print((afip.consultar_comprobante(factura_electronica)))
    print("")

    #######################################
    # Nota de Debito Electronica MiPyME
    #######################################

    numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=6), "B")
    nota_de_debito_electronica = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Brunetti",
        "sub_tipo": "B",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 3,
        "total_facturado": "100000.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=6),
        "factura": factura_electronica
    })
    lineas_nota_de_debito_electronica = [LineaDeComprobante(**{
        "comprobante": nota_de_debito_electronica,
        "importe_neto": 100000.00,
        "sub_total": 100000.00,
        "iva": 0,
    })]
    print("N DEBITO MIPYME")
    print("--------------")
    afip.emitir_comprobante(nota_de_debito_electronica, lineas_nota_de_debito_electronica)
    print((nota_de_debito_electronica.cae))
    print((nota_de_debito_electronica.vencimiento_cae))
    print((afip.consultar_comprobante(nota_de_debito_electronica)))
    print("")

    #######################################
    # Nota de Credito Electronica MiPyME
    #######################################

    numero = afip.consultar_proximo_numero("Brunetti", 3, TipoComprobante.objects.get(pk=7), "B")
    nota_de_credito_electronica = Comprobante(**{
        "nombre_cliente": "Obra Social de los Trabajadores de la Planta Nuclear de Springfield",
        "domicilio_cliente": " - Springfield - (CP:2000)",
        "nro_cuit": "30604958640",
        "gravado_paciente": "",
        "condicion_fiscal": "EXENTO",
        "gravado": Gravado.objects.get(pk=1),
        "responsable": "Brunetti",
        "sub_tipo": "B",
        "estado": "PENDIENTE",
        "numero": numero,
        "nro_terminal": 3,
        "total_facturado": "100000.00",
        "total_cobrado": "0.00",
        "fecha_emision": date.today(),
        "fecha_recepcion": date.today(),
        "tipo_comprobante": TipoComprobante.objects.get(pk=7),
        "factura": factura_electronica
    })
    lineas_nota_de_credito_electronica = [LineaDeComprobante(**{
        "comprobante": nota_de_credito_electronica,
        "importe_neto": 100000.00,
        "sub_total": 100000.00,
        "iva": 0,
    })]
    print("N CREDITO MIPYME")
    print("--------------")
    afip.emitir_comprobante(nota_de_credito_electronica, lineas_nota_de_credito_electronica)
    print((nota_de_credito_electronica.cae))
    print((nota_de_credito_electronica.vencimiento_cae))
    print((afip.consultar_comprobante(nota_de_credito_electronica)))
    print("")

if __name__ == "__main__":
    main()