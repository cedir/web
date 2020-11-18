from typing import Dict, List
from reportlab.platypus.tables import TableStyle
from rest_framework.response import Response
from itertools import chain

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

from comprobante.models import ID_GRAVADO_INSCRIPTO_10_5, ID_GRAVADO_INSCRIPTO_21, ID_GRAVADO_EXENTO
from medico.models import PagoMedico
from medico.calculo_honorarios.calculador import CalculadorHonorariosPagoMedico
from medico.serializers import ListNuevoPagoMedicoSerializer

def generar_pdf_detalle_pago(response: Response, pago: PagoMedico) -> Response:

    estudios = [ListNuevoPagoMedicoSerializer(e, context={
                    'calculador': CalculadorHonorariosPagoMedico(e),
                    'medico': pago.medico
                }).data for e in  list(chain(pago.estudios_actuantes.all(), pago.estudios_solicitantes.all()))]
    datos_pago = get_datos_pago(pago)
    lineas_pago = get_lineas_pago(pago, estudios)
    totales = get_totales(estudios)

    return armar_pdf(response, datos_pago, lineas_pago, totales, str(pago.observacion))

def get_datos_pago(pago: PagoMedico) -> Dict:
    return {
        "doctorx": f"<b><u>Doctorx</u></b>:\t\t{pago.medico.apellido}, {pago.medico.nombre}",
        "fecha": f"<b><u>Fecha</u></b>:\t\t{pago.fecha.day}/{pago.fecha.day}/{pago.fecha.day}"
    }

def get_lineas_pago(pago: PagoMedico, estudios: ListNuevoPagoMedicoSerializer) -> List:
    return [{
        "fecha": f"{e['fecha']}",
        "paciente": f"{e['paciente']['apellido']}, {e['paciente']['nombre']}",
        "obra_social": e['obra_social']['nombre'],
        "practica": e['practica']['descripcion'],
        "actuante": f"{e['medico_actuante']['apellido']}, {e['medico_actuante']['nombre']}",
        "solicitante": f"{e['medico_solicitante']['apellido']}, {e['medico_solicitante']['nombre']}",
        "fecha_cobro": f"{e['fecha_cobro']}",
        "importe": e['importe_estudio'],
        "pago": e['pago'],
        "iva10.5": e['importe_iva'] if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_10_5 else 0,
        "iva21": e['importe_iva'] if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_21 else 0,
        "total": e['total'],
    } for e in estudios]

def get_totales(estudios: ListNuevoPagoMedicoSerializer) -> Dict:
    return {
        "honorarios_exento": sum([e['pago'] for e in estudios if e['gravado_id'] == ID_GRAVADO_EXENTO]),
        "honorarios_10_5": sum([e['pago'] for e in estudios if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_10_5]),
        "honorarios_21": sum([e['pago'] for e in estudios if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_21]),
        "monto_iva_10_5": sum([e['importe_iva'] for e in estudios if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_10_5]),
        "monto_iva_21": sum([e['importe_iva'] for e in estudios if e['gravado_id'] == ID_GRAVADO_INSCRIPTO_21]),
        "total": sum([e['pago'] + e['importe_iva'] for e in estudios ])
    }

def armar_pdf(response: Response, datos: Dict, lineas: List, totales: Dict, observacion: str) -> Response:
    # Create the PDF object, using the response object as its "file."
    pdf = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        topMargin=15*mm,
        bottomMargin=10*mm,
        rightMargin=17*mm,
        leftMargin=17*mm
    )

    styles: StyleSheet1 = getSampleStyleSheet()
    styles["Normal"].fontSize = 14

    elements = encabezado(datos, styles) \
        + tabla(lineas, styles) \
        + recuadro(totales, styles) \
        + elem_observacion(observacion, styles)

    pdf.build(elements)
    return response

def encabezado(datos: Dict, styles: StyleSheet1) -> List[Flowable]:
    return [
        Paragraph(f"Detalle del pago", styles["Title"]),
        Paragraph("<br/><br/>", styles["Normal"]),
        Paragraph(datos["doctorx"], styles["Normal"]),
        Paragraph("<br/>", styles["Normal"]),
        Paragraph(datos["fecha"], styles["Normal"]),
        Paragraph("<br/><br/>", styles["Normal"]),
    ]

def tabla(lineas: List, styles: StyleSheet1) -> List[Flowable]:
    table = Table([tuple([header for header in [
        "Fecha", "Paciente", "Obra\nSocial", "Practica", "Actuante", "Solicitante",
        "Fecha\nCobro", "Importe", "Pago", "IVA10.5", "IVA21", "Total"
        ]])] + [tuple([Paragraph(str(e[key]), style=styles["BodyText"]) for key in [
        "fecha", "paciente", "obra_social", "practica", "actuante", "solicitante",
        "fecha_cobro", "importe", "pago", "iva10.5", "iva21", "total",
        ]]) for e in lineas],
        colWidths=[3 * cm, 2.5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2.6 * cm, 2.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        # ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
    ]))

    table.setStyle(TableStyle(
        [
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('GRID',(0,1),(-1,-1),2,colors.black),
        ]
    ))
    return [table]

def recuadro(totales: Dict, styles: StyleSheet1) -> List[Flowable]:
    table = Table([
        [Paragraph("<b>Honorarios Exento</b>", styles["Normal"]), f"{totales['honorarios_exento']:.2f}"],
        [Paragraph("<b>Honorarios gravados al 10.5</b>", styles["Normal"]), f"{totales['honorarios_10_5']:.2f}"],
        [Paragraph("<b>Honorarios gravados al 21</b>", styles["Normal"]), f"{totales['honorarios_21']:.2f}"],
        [Paragraph("<b>Monto IVA 10.5</b>", styles["Normal"]), f"{totales['monto_iva_10_5']:.2f}"],
        [Paragraph("<b>Monto IVA 21</b>", styles["Normal"]), f"{totales['monto_iva_21']:.2f}"],
        [Paragraph("<b>Total</b>", styles["Normal"]), f"{totales['total']:.2f}"],
    ],hAlign="LEFT")
    table.setStyle(TableStyle([
        # ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
    ]))
    return [Paragraph("<br/><br/>", styles["Normal"]), table]

def elem_observacion(observacion: str, styles: StyleSheet1) -> List[Flowable]:
    return [
        Paragraph("<br/><br/>", styles["Normal"]),
        Paragraph(observacion, styles["Normal"]),
    ]