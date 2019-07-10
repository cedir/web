# Parsear el xlsx, armar una lista de diccionarios.
# Para cada fila:
#   buscar el comprobante
#   generar la linea de informe
#   comparar para cada atributo y hacer saltar diferencias

import xlrd
import wsgi

from comprobante.models import Comprobante
from comprobante.calculador_informe import calculador_informe_factory


def parsear_informe():
    """
    Busca el informe de ejemplo y lo parsea en un diccionario de numero: linea
    """
    # Give the location of the file
    loc = ("informe_ejemplo.xlsx")

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
            "fecha": row[3].value,
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
        if row[0].value != ""
    }


def buscar_comprobantes(informe_ejemplo):
    """
    Busca todos lso comprobantes correspondientes al informe de ejemplo.
    """
    numeros = [inf["numero"] for inf in informe_ejemplo.values()]
    return Comprobante.objects.filter(numero__in=numeros, fecha_emision__month__in=[1], fecha_emision__year__in=[2019])


def main():
    lineas_ejemplo = parsear_informe()
    comprobantes_del_informe = buscar_comprobantes(lineas_ejemplo)
    assert(len(lineas_ejemplo) == len(comprobantes_del_informe))
    for c in comprobantes_del_informe:
        nuestro = calculador_informe_factory(c)
        # esto en particular lo podemos hacer porque no se chocan las numeros en este mes
        # pero podria no ser el caso
        ejemplo = lineas_ejemplo[c.numero]
        print("Comprobante {}".format(c.id))
        if int(nuestro.total_facturado) != int(ejemplo["total_facturado"]):
            print("    Total Facturado - calculado: {0}, ejemplo: {1}".format(
                nuestro.total_facturado, ejemplo["total_facturado"]))
        if int(nuestro.iva) != int(ejemplo["iva"]):
            print(
                "    IVA - calculado: {}, ejemplo: {}" .format(nuestro.iva, ejemplo["iva"]))
        if int(nuestro.honorarios_medicos) != int(ejemplo["honorarios_medicos"]):
            print("    Honorarios Medicos - calculado: {}, ejemplo: {}".format(
                nuestro.honorarios_medicos, ejemplo["honorarios_medicos"]))
        if int(nuestro.honorarios_anestesia) != int(ejemplo["honorarios_anestesistas"]):
            print("    Honorarios Anestesistas - calculado: {}, ejemplo: {}".format(
                nuestro.honorarios_anestesia, ejemplo["honorarios_anestesistas"]))
        if int(nuestro.total_medicamentos) != int(ejemplo["medicacion"]):
            print("    Total Medicamentos - calculado: {}, ejemplo: {}".format(
                nuestro.total_medicamentos, ejemplo["medicacion"]))
        otros = nuestro.retencion_impositiva + nuestro.retencion_cedir + \
            nuestro.sala_recuperacion + nuestro.total_material_especifico
        if int(otros) != int(ejemplo["otros"]):
            print(
                "    Otros- calculado: {}, ejemplo: {}".format(otros, ejemplo["otros"]))


if __name__ == "__main__":
    main()
