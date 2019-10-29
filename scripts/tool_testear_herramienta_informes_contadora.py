# pylint: disable=unused-import,wrong-import-position,invalid-name,wrong-import-order
# Este script sirve para testear la herramienta de informe de comprobantes para la contadora
# contra un ejemplo de informe real en excel de Mariana.
# Hace lo siguiente:
#   Parsea el xlsx, arma un diccionario de {numero de factura: linea del informe de ejemplo}.
#   Para cada comprobante en la DB que corresponda a una fila del informe de ejemplo:
#       Crea un informe con la herramienta
#       Compara campo por campo e imprime en consola los que tengan una diferencia
#
# Llamarlo con:
# $ python scripts/tool_testear_herramienta_informes_contadora.py path_a_informe_ejemplo.xlsx
#
# Los informes de ejemplo se encuentran en el mega, en una carpeta "informes_comproabntes_ejemplo"


# Correccion del path para importar desde el directorio padre
from __future__ import print_function
import os
import sys
import  inspect
from datetime import datetime
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import wsgi # Importar esto hace lo de las settings e inicia django
from django.core.exceptions import ObjectDoesNotExist
import xlrd

from comprobante.models import Comprobante, TipoComprobante
from comprobante.calculador_informe import calculador_informe_factory
from presentacion.models import Presentacion
from estudio.models import Estudio

def parsear_informe():
    """
    Busca el informe de ejemplo y lo parsea en un diccionario de numero: linea
    """
    # Give the location of the file
    if len(sys.argv) > 1:
        loc = sys.argv[1]
    else:
        loc = "informe_ejemplo.xlsx"

    # To open Workbook
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    # For row 0 and column 0
    sheet.cell_value(0, 0)
    return {
        row[2].value: {
            "estado": row[0].value,
            "tipo": row[1].value,
            "numero": row[2].value,
            "fecha": datetime(*xlrd.xldate_as_tuple(row[3].value, wb.datemode)),
            "obra_social": row[4].value,
            "monto": row[5].value,
            "iva": row[6].value,
            "total_facturado": row[7].value,
            "honorarios_medicos": row[9].value,
            "honorarios_anestesistas": row[10].value,
            "medicacion": row[11].value,
            "otros": row[12].value,
            "retencion_anestesistas": row[13].value,
        }
        for row in sheet.get_rows()
        if row[0].value != "" and "Liquidacion" not in row[1].value
    }


def buscar_comprobantes(informe_ejemplo):
    """
    Busca todos lso comprobantes correspondientes al informe de ejemplo.
    """
    if len(sys.argv) > 2:
        id_comprobante = sys.argv[2]
        return [Comprobante.objects.get(pk=id_comprobante)]
    filtros = [{
        # En realidad nos faltaria el numero de terminal peor no aparece en el informe de mariana. Filtramos lo mejor posible.
        "numero": inf["numero"],
        "tipo_comprobante": TipoComprobante.objects.get(pk=1) if "Factura" in inf["tipo"] \
        else TipoComprobante.objects.get(pk=3) if "Nota De Debito" in inf["tipo"] \
        else TipoComprobante.objects.get(pk=4),
        "sub_tipo": "A" if "A" in inf["tipo"] else "B",
        "fecha_emision": inf["fecha"],
        "responsable": "Cedir" if "CEDIR" in inf["tipo"] else "Brunetti"
    } for inf in informe_ejemplo.values()]
    return [Comprobante.objects.get(**f) for f in filtros]


def printear_estudios(comp, linea):
    presen = Presentacion.objects.get(comprobante__id=comp.id)
    estudios = Estudio.objects.filter(presentacion__id=presen.id)

    header_informe = ["hon_med", "ret_cedir", "uso_mats", "tot_med",
                      "mat_esp", "hon_anes", "ret_anes", "sala_recu", "ret_impos"]
    informe = [linea.honorarios_medicos, linea.retencion_cedir, linea.uso_de_materiales,
               linea.total_medicamentos, linea.total_material_especifico,
               linea.honorarios_anestesia, linea.retencion_anestesia,
               linea.sala_recuperacion, linea.retencion_impositiva]
    informe_format = "{:>12}" * len(header_informe)
    print(informe_format.format(*header_informe))
    print(informe_format.format(*informe) + "\n")

    header_estudio = ["practica", "act", "sol", "OS", "importe", "PcF", "dPac"]
    row_format = "{:>12}" * len(header_estudio)
    print(row_format.format(*header_estudio))
    for est in estudios:

        row = [est.practica.id, est.medico.id, est.medico_solicitante.id, est.obra_social.id,
               est.importe_estudio, est.es_pago_contra_factura, est.diferencia_paciente]
        print(row_format.format(*row))


def main():
    lineas_ejemplo = parsear_informe()
    comprobantes_del_informe = buscar_comprobantes(lineas_ejemplo)
    print(len(lineas_ejemplo))
    print(len(comprobantes_del_informe))
    assert(len(lineas_ejemplo) == len(
        comprobantes_del_informe) or len(sys.argv) > 2)

    for c in comprobantes_del_informe:
        # print("Comprobante {}".format(c.id))
        # printear_estudios(c)
        try:
            Presentacion.objects.get(comprobante__id=c.id)
        except ObjectDoesNotExist:
            continue

        nuestro = calculador_informe_factory(c)
        ejemplo = lineas_ejemplo[c.numero]
        print("\nComprobante {}".format(c.id))
        otros = nuestro.retencion_impositiva + nuestro.retencion_cedir + \
            nuestro.sala_recuperacion + \
            nuestro.total_material_especifico + \
            nuestro.uso_de_materiales + nuestro.honorarios_solicitantes
        suma = int(nuestro.honorarios_anestesia + nuestro.honorarios_medicos +
                   nuestro.total_medicamentos + nuestro.iva + nuestro.retencion_anestesia + otros)
        if int(nuestro.total_facturado) != suma:
            printear_estudios(c, nuestro)
            print("    Total Facturado - calculado: {0}, suma: {1}".format(
                nuestro.total_facturado, suma))
            if int(nuestro.honorarios_medicos) != int(ejemplo["honorarios_medicos"]):
                print("    Honorarios Medicos - calculado: {}, ejemplo: {}".format(
                    nuestro.honorarios_medicos, ejemplo["honorarios_medicos"]))
            if int(nuestro.honorarios_anestesia) != int(ejemplo["honorarios_anestesistas"]):
                print("    Honorarios Anestesistas - calculado: {}, ejemplo: {}".format(
                    nuestro.honorarios_anestesia, ejemplo["honorarios_anestesistas"]))
            if int(nuestro.total_medicamentos) != int(ejemplo["medicacion"]):
                print("    Total Medicamentos - calculado: {}, ejemplo: {}".format(
                    nuestro.total_medicamentos, ejemplo["medicacion"]))
            if int(otros) != int(ejemplo["otros"]):
                print(
                    "    Otros- calculado: {}, ejemplo: {}".format(otros, ejemplo["otros"]))
                print("        ret_imp: {}".format(
                    nuestro.retencion_impositiva))
                print("        ret_cedir: {}".format(nuestro.retencion_cedir))
                print("        sala_rec: {}".format(nuestro.sala_recuperacion))
                print("        mat_esp: {}".format(
                    nuestro.total_material_especifico))
                print("        uso_mat: {}".format(nuestro.uso_de_materiales))
                print("        hon_sol: {}".format(
                    nuestro.honorarios_solicitantes))
            # if int(nuestro.total_medicamentos) != int(ejemplo["medicacion"]):
            #     print("    Total Medicamentos - calculado: {}, ejemplo: {}".format(
            #         nuestro.total_medicamentos, ejemplo["medicacion"]))


if __name__ == "__main__":
    main()
