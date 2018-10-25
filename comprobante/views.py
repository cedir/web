# -*- coding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect

import zipfile
import StringIO

from imprimir import generar_factura, obtener_comprobante, obtener_filename
from informe_ventas import obtener_comprobantes_ventas, obtener_archivo_ventas
from comprobante.serializers import ComprobanteListadoSerializer


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


from rest_framework import generics
from comprobante.models import Comprobante
from rest_framework.response import Response
class ComprobantesList(generics.ListAPIView):
    serializer_class = ComprobanteListadoSerializer

    def list(self, request):
        #import pdb; pdb.set_trace()
        queryset = Comprobante.objects.filter(fecha_emision__month=request.query_params["mes"],
                                              fecha_emision__year=request.query_params["anio"])
        data = [ComprobanteListadoSerializer(q, context={'calculador': 1}).data
                for q in queryset]
        return Response(data)

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

NOTA: el calculo de honorario medico se aplican las mismas reglas que pago a medico. Si el estudio esta pagado al medico, no importa, volver a aplicar las reglas porque hay qye mostrar lo que se deberia pagar, y no lo que se pago.
      calculo de honorario anestesia sale del campo "anestesia" del estudio. Sino esta cargado se muestra 0 (cero)

NOTA 2: del calculo de pago a medico, se desprenden otros valores como "Retencion Impositiva" y "Gastos Administriativos".
        Estos valores deben ser sumados por separado y mostrado en diferentes columnas.

*
Columnas Actuales
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


Columnas extras que hay que mostrar:
Retencion Imposotva
Retencion Cedir (GA)
Sala de recuperacion
Retencion Anestesia --> ya se esta mostrando. Aplicar 10% a la suma de todo es una opcion, o bien recorrer cada estudio y aplicar el porcentaje de cada anestesista. Sumarlos y mostrar eso es la otra opcion.
Medicamentos         |
Material especifico  |  --> Estos 2 hoy aparecen juntos como TotalMedicacion, pero deben ir separados


# TODO next:
 - Terminar de entender calclulo de honorario para un estudio, y como se relaciona eso con Pago A Medico, ya que se
 puede usar lo mismo para ambos.
 - Se puede empezar a hacer el listado sin calcular los honorarios medicos. Y dejar eso para el final.
"""



"""
PAGO A MEDICO:

--


"""
