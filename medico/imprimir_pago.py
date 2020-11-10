from typing import Dict, List
from rest_framework.response import Response

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Table, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black,white, Color

from comprobante.models import ID_GRAVADO_INSCRIPTO_10_5, ID_GRAVADO_INSCRIPTO_21, ID_GRAVADO_EXENTO
from medico.models import PagoMedico
from medico.calculo_honorarios.calculador import CalculadorHonorariosPagoMedico
from medico.serializers import ListNuevoPagoMedicoSerializer

styles = getSampleStyleSheet()

font_std = styles["Normal"]
font_std.fontName = 'Helvetica'
font_std.alignment = TA_JUSTIFY
font_std.fontSize = 10

def generar_pdf_detalle_pago(response: Response, pago: PagoMedico) -> Response:

    estudios = [ListNuevoPagoMedicoSerializer(e, context={
                    'calculador': CalculadorHonorariosPagoMedico(e),
                    'medico': pago.medico
                }) for e in pago.estudios_actuantes | pago.estudios_solicitantes]
    datos_pago = get_datos_pago(pago)
    lineas_pago = get_lineas_pago(pago, estudios)
    totales = get_totales(estudios)

    return armar_pdf(response, datos_pago, lineas_pago, totales)

def get_datos_pago(pago: PagoMedico) -> Dict:
    return {
        "doctorx": f"Doctorx:\t\t{pago.medico.apellido}, {pago.medico.nombre}",
        "fecha": f"Fecha:\t\t{pago.fecha.day}/{pago.fecha.day}/{pago.fecha.day}"
    }

def get_lineas_pago(pago: PagoMedico, estudios: ListNuevoPagoMedicoSerializer) -> List:
    return [{
        "fecha": f"{e.fecha.day}/{e.fecha.day}/{e.fecha.day}",
        "paciente": f"{e.paciente.apellido}, {e.paciente.nombre}",
        "obra_social": e.obra_social,
        "practica": e.practica.descripcion,
        "actuante": f"{e.medico_actuante.apellido}, {e.medico_actuante.nombre}",
        "solicitante": f"{e.medico_solicitante.apellido}, {e.medico_solicitante.nombre}",
        "fecha_cobro": f"{e.fecha_cobro.day}/{e.fecha_cobro.day}/{e.fecha_cobro.day}",
        "importe": e.importe,
        "pago": e.pago,
        "iva10.5": e.importe_iva if e.gravado_id == ID_GRAVADO_INSCRIPTO_10_5 else 0,
        "iva21": e.importe_iva if e.gravado_id == ID_GRAVADO_INSCRIPTO_21 else 0,
        "total": e.total,
    } for e in estudios]

def get_totales(estudios: ListNuevoPagoMedicoSerializer) -> Dict:
    return {
        "honorarios_exento": sum([e.pago for e in estudios if e.gravado_id == ID_GRAVADO_EXENTO]),
        "honorarios_10_5": sum([e.pago for e in estudios if e.gravado_id == ID_GRAVADO_INSCRIPTO_10_5]),
        "honorarios_21": sum([e.pago for e in estudios if e.gravado_id == ID_GRAVADO_INSCRIPTO_21]),
        "monto_iva_10_5": sum([e.importe_iva for e in estudios if e.gravado_id == ID_GRAVADO_INSCRIPTO_10_5]),
        "monto_iva_21": sum([e.importe_iva for e in estudios if e.gravado_id == ID_GRAVADO_INSCRIPTO_21]),
        "total": sum([e.pago + e.importe_iva for e in estudios ])
    }

def armar_pdf(response: Response, datos: Dict, lineas: List, totales: Dict) -> Response:
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        topMargin=55*mm,
        bottomMargin=65*mm,
        rightMargin=17*mm,
        leftMargin=17*mm
    )

    elements = []
    doc.build(elements)
    return response