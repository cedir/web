from typing import Dict, List
from reportlab.platypus.tables import TableStyle
from rest_framework.response import Response
from itertools import chain
from decimal import *

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

from medicamento.models import TIPOS_MEDICAMENTOS

styles = getSampleStyleSheet()
styles["Normal"].fontSize = 10
styles["Heading1"].fontSize = 10
separacion = Paragraph('_'*89, styles["Normal"])
enter = Paragraph("<br/><br/>", styles["Normal"])

def generar_pdf_presentacion(response, presentacion):

    pdf = SimpleDocTemplate(
        response,
        pagesize=(A4),
        topMargin=60*mm,
        bottomMargin=10*mm,
        rightMargin=15*mm,
        leftMargin=15*mm
    )
    elements = pdf_encabezado(presentacion['obra_social'], presentacion['fecha']) + [separacion, enter]
    estudios, total_presentacion = pdf_estudios(presentacion['estudios'])
    for estudio in estudios:
        elements += estudio
    elements += [Paragraph(f"Total: ${total_presentacion}", styles['Heading2'])]
    pdf.build(elements)
    return response

def pdf_encabezado(obra_social, fecha):
    return [
        Paragraph(f"Obra Social: {obra_social['nombre']}", styles["Title"]),
        Paragraph("<br/><br/>", styles["Normal"]),
        Paragraph("Detalle de Facturacion correspondiente al mes de", styles["Normal"]),
        Paragraph(f"Fecha: {fecha}", styles["Normal"]),
        Paragraph("<br/><br/>", styles["Normal"]),
    ]

def filas_pension(importe_pension):
    
    if not (importe_pension == '0.00'):
        return [['Pension', '', f"${importe_pension}"]]
    return []

def filas_anestesia(importe_anestecia):
    if not (importe_anestecia == '0.00'):
        return [['Anestesia', '', f"${importe_anestecia}"]]
    return []

def filas_elementos(lista, titulo):
    importe_total = Decimal(0)
    if len(lista) > 0:
        filas = [[f'{titulo}:', '', '']]
        for elemento in lista:
            filas += [[' * ' + elemento['descripcion'], '$' + elemento['importe'], '']]
            importe_total += Decimal(elemento['importe'])
        extra = ''
        if titulo == 'Medicacion':
            extra = ' * Valorizada de acuerdo al Vademecum Kairo'
        filas += [[f'Total {titulo}', '', f'${importe_total}' + extra]]
        return filas, importe_total
    return [], importe_total

def pdf_tabla_estudio(estudio):
    material_especifico = []
    medicacion = []

    for medicamento in estudio['medicacion']:
        if medicamento['tipo'] == TIPOS_MEDICAMENTOS[0][0]:
            material_especifico.append(medicamento)
        if medicamento['tipo'] == TIPOS_MEDICAMENTOS[1][0]:
            medicacion.append(medicamento)
    total_estudio = Decimal(estudio['importe_estudio']) + Decimal(estudio['pension'])
    fila_medicacion, costo_medicacion = filas_elementos(medicacion, 'Medicacion')
    fila_material, costo_material = filas_elementos(material_especifico, 'Material Especifico')
    total_estudio = total_estudio + costo_material + costo_medicacion

    tabla = [['Practica', '', f"${estudio['importe_estudio']}"]] \
         + filas_pension(estudio['pension']) \
         + filas_anestesia(estudio['arancel_anestesia']) \
         + fila_medicacion \
         + fila_material \
         + [['Total del estudio', '', f'${total_estudio}']]
    style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black)]
    table = Table(tabla, style = style)
    return table, total_estudio

def pdf_estudio(estudio):
    nombre_paciente = estudio['paciente']['apellido'] + ', ' + estudio['paciente']['nombre']
    info_extra = estudio.get('informacion_extra', '')
    tabla, total_estudio = pdf_tabla_estudio(estudio)
    return [Paragraph(f"Fecha: {estudio['fecha']}", styles["Normal"]),
        Paragraph(f"Paciente: {nombre_paciente} - Nro de afiliado: {estudio['paciente']['nroAfiliado']} {info_extra}", styles["Normal"]),
        Paragraph(f"Nro de orden: {estudio['nro_de_orden']}", styles["Normal"]),
        Paragraph(f"Practica: {estudio['practica']['descripcion']}", styles["Normal"]),
        enter,
        tabla,
        enter,] , total_estudio

def pdf_estudios(estudios):
    informacion = [[]]
    total_presentacion = Decimal(0)
    for estudio in estudios:
        informacion_estudio, total_estudio = pdf_estudio(estudio)
        total_presentacion += total_estudio
        informacion += [informacion_estudio, [separacion]]
    return informacion, total_presentacion