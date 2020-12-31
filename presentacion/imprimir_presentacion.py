from itertools import chain
from decimal import Decimal

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph, KeepTogether
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

from medicamento.models import TIPOS_MEDICAMENTOS

styles = getSampleStyleSheet()
styles["Normal"].fontSize = 10
styles["Heading1"].fontSize = 10
HLINE = KeepTogether(Paragraph('_'*89, styles["Normal"]))
ENTER = KeepTogether(Paragraph("<br/><br/>", styles["Normal"]))
TOPMARGIN = 60*mm
BOTTOMMARGIN = 10*mm
RIGHTMARGIN = 15*mm
LEFTMARGIN = 15*mm
COL1 = 80*mm
COL2 = 30*mm
COL3 = 70*mm

def generar_pdf_presentacion(response, presentacion):

    pdf = SimpleDocTemplate(
        response,
        pagesize = (A4),
        topMargin = TOPMARGIN,
        bottomMargin = BOTTOMMARGIN,
        rightMargin = RIGHTMARGIN,
        leftMargin = LEFTMARGIN,
    )
    presentacion = get_pacientes(presentacion)
    elements = pdf_encabezado(presentacion['obra_social'], presentacion['fecha'], presentacion['periodo']) + [HLINE]
    estudios, total_presentacion = pdf_estudios(presentacion['estudios'])
    for estudio in estudios:
        elements += estudio
    elements += [KeepTogether(Paragraph(f"Total: ${total_presentacion}", styles['Heading2']))]
    pdf.build(elements)
    return response

def pdf_encabezado(obra_social, fecha, periodo):
    return [
        KeepTogether(Paragraph(f"Obra Social: {obra_social['nombre']}", styles["Title"])),
        ENTER,
        KeepTogether(Paragraph(f"Detalle de Facturacion correspondiente al mes de {periodo}", styles["Normal"])),
        KeepTogether(Paragraph(f"Fecha: {fecha}", styles["Normal"])),
    ]

def estudios_por_paciente(nombre, estudios):
    estudios_del_paciente = []
    for estudio in estudios:
        if estudio['paciente']['apellido'] + ', ' + estudio['paciente']['nombre'] == nombre:
            estudios_del_paciente += [estudio]
    return estudios_del_paciente

def get_pacientes(presentacion):
    estudios = presentacion['estudios']
    pacientes = set([estudio['paciente']['apellido'] + ', ' + estudio['paciente']['nombre'] for estudio in estudios ])
    presentacion['pacientes'] = [
        {
            'nombre' : nombre,
            'estudios': estudios_por_paciente(nombre, estudios)
        }
    for nombre in pacientes]
    return presentacion

def filas_pension(importe_pension):
    
    if not (Decimal(importe_pension) == Decimal(0)):
        return [['Pension', '', f"${importe_pension}"]]
    return []

def filas_anestesia(importe_anestecia):
    if not (importe_anestecia == '0.00'):
        return [['Anestesia', '', f"${importe_anestecia}"]]
    return []

def filas_medicamentos(medicamentos, tipo_medicamento):
    importe_total = Decimal(0)
    filas = []
    if medicamentos:
        filas = [[f'{tipo_medicamento}:', '', '']]
        for elemento in medicamentos:
            filas += [[' * ' + elemento['descripcion'], '$' + elemento['importe'], '']]
            importe_total += Decimal(elemento['importe'])
        extra = ' * Valorizada de acuerdo al Vademecum Kairo' if tipo_medicamento == 'Medicacion' else ''
        filas += [[f'Total {tipo_medicamento}', '', f"{importe_total} {extra}"]]
    return filas, importe_total

def pdf_tabla_estudio(estudio):
    material_especifico = []
    medicacion = []
    for medicamento in estudio['medicacion']:
        if medicamento['tipo'] == TIPOS_MEDICAMENTOS[0][0]:
            material_especifico += [medicamento]
        else:
            medicacion += [medicamento]
    total_estudio = Decimal(estudio['importe_estudio']) + Decimal(estudio['pension'])
    fila_medicacion, costo_medicacion = filas_medicamentos(medicacion, 'Medicacion')
    fila_material, costo_material = filas_medicamentos(material_especifico, 'Material Especifico')
    total_estudio = total_estudio + costo_material + costo_medicacion

    tabla = [['Practica', '', f"${estudio['importe_estudio']}"]] \
         + filas_pension(estudio['pension']) \
         + filas_anestesia(estudio['arancel_anestesia']) \
         + fila_medicacion \
         + fila_material \
         + [['Total del estudio', '', f'${total_estudio}']]

    style = [('INNERGRID', (0, x), (2, x), 0.25, colors.black) for x in range(len(tabla)-1)] #crea lineas en la tabla
    table = Table(tabla, style = style, colWidths=[COL1, COL2, COL3])
    return table, total_estudio

def pdf_estudio(estudio):
    nombre_paciente = estudio['paciente']['apellido'] + ', ' + estudio['paciente']['nombre']
    info_extra = estudio['paciente'].get('informacion_extra', '') or ''
    tabla, total_estudio = pdf_tabla_estudio(estudio)
    return [KeepTogether(Paragraph(f"Fecha: {estudio['fecha']}", styles["Normal"])),
        KeepTogether(Paragraph(f"Paciente: {nombre_paciente} - Nro de afiliado: {estudio['paciente']['nroAfiliado']} {info_extra}", styles["Normal"])),
        KeepTogether(Paragraph(f"Nro de orden: {estudio['nro_de_orden']}", styles["Normal"])),
        KeepTogether(Paragraph(f"Practica: {estudio['practica']['descripcion']}", styles["Normal"])),
        ENTER,
        tabla,
        ENTER,] , total_estudio

def pdf_estudios(estudios):
    informacion = [[]]
    total_presentacion = Decimal(0)
    for estudio in estudios:
        informacion_estudio, total_estudio = pdf_estudio(estudio)
        total_presentacion += total_estudio
        informacion += [informacion_estudio, [HLINE]]
    return informacion, total_presentacion