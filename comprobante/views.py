# -*- coding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect

import zipfile
import StringIO

from imprimir import generar_factura, obtener_comprobante, obtener_filename
from informe_ventas import obtener_comprobantes_ventas, obtener_archivo_ventas


def imprimir(request, cae):
    # Imprime leyenda?
    leyenda = request.method == 'GET' and 'leyenda' in request.GET

    # Adquiere datos
    comp = obtener_comprobante(cae)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = u'filename="{0}.pdf"'.format(obtener_filename(comp['responsable'], comp['cabecera']))

    return generar_factura(response, comp, leyenda)


def ventas(request, responsable, anio, mes):
    if not request.user.is_authenticated() or not request.user.has_perm('comprobante.informe_ventas'):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    # Adquiere datos
    comprobantes = obtener_comprobantes_ventas(responsable, anio, mes)

    # Genera el archivo
    (ventas, alicuotas) = obtener_archivo_ventas(comprobantes)

    # Abre un StringIO para guardar el contenido del archivo
    stream = StringIO.StringIO()

    # Compresor zip
    zipcomp = zipfile.ZipFile(stream, 'w')

    # Agrega los archivos
    zipcomp.writestr(u'VENTAS.txt', u'\r\n'.join(ventas).encode('ascii', 'replace'))
    zipcomp.writestr(u'ALICUOTAS.txt', u'\r\n'.join(alicuotas).encode('ascii', 'replace'))

    # Cierra el archivo y escribe el contenido
    zipcomp.close()

    # Genera el response adecuado
    resp = HttpResponse(stream.getvalue(), content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename={0}_{1}_{2}.zip'.format(responsable, anio, mes)

    return resp



"""
- traer comprobantes filtrando por fecha desde - fecha hasta
- para cada comprobante hay que calcular los honorarios
- el "calcular honorarios" devuelve 3 importes nuevos: honorario, anestesia y total medicacion
- Con el comprobante se trae la presentacion asociada
- Con la presentacion se cargan las lineasDePresentacion
- Para cada linea, se obtiene el estudio
- Con el estudio se calculan el honorario del medico (esta logica se comparte con Pago a Medico), el total medicacion y anestesia.
  (https://github.com/cedir/intranet/blob/81f708d089f02efd8d98c886782572428752913f/CedirNegocios/Interfaces/CalculadorHonorariosComprobantes.vb#L79)
- Finalmente se muestran los datos de comprobante (*) mas honorario, anestesia y total medicacion

NOTA: tanto el calculo de honorario medico como el calculo de honorario anestesista, deben calcularse del mismo modo
      que se hace en sus respectivas pantallas (pago a medico, pago anestesista)

*
dr("Tipo") = c.TipoComprobante.Descripcion & " " & c.SubTipo.ToUpper() + "  -   " + c.Responsable.ToUpper()
dr("Nro") = c.NroComprobante.ToString()
dr("Estado") = c.Estado
dr("Fecha") = c.FechaEmision.ToString().Remove(10)
dr("Cliente") = c.NombreCliente.ToUpper()
dr("TotalFacturado") = Format(c.TotalFacturado, "#################0.00")
dr("TotalCobrado") = Format(0.0, "#################0.00")
dr("TotalFacturado") = Format(0.0, "#################0.00")
dr("Neto") = Format(0.0, "#################0.00")
dr("IVA") = Format(0.0, "#################0.00")
dr("Honorarios") = Format(0.0, "#################0.00")
dr("Anestesia") = Format(0.0, "#################0.00")
dr("TotalMedicacion") = Format(0.0, "#################0.00")

# TODO next:
 - Terminar de entender calclulo de honorario para un estudio, y como se relaciona eso con Pago A Medico, ya que se
 puede usar lo mismo para ambos.
"""



"""
PAGO A MEDICO:




"""