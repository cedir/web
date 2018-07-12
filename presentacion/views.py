from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from common.drf.views import StandardResultsSetPagination
from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer


class PresentacionViewSet(viewsets.ModelViewSet):
    queryset = Presentacion.objects.all().order_by('-fecha')
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    @detail_route(methods=['get'])
    def get_detalle_osde(self, request, pk=None):

        presentacion = Presentacion.objects.get(pk=pk)

        csv_string = ''
        estudios = presentacion.estudios.all()

        for estudio in estudios:
            csv_string = '{}\n{}'.format(csv_string, self.get_row_osde(estudio))

        response = HttpResponse(csv_string, content_type='text/csv')
        return response

    def get_row_osde(self, estudio):
        """
        espacios 0 1
        N Prestador	2	7
        N Afiliado	11	21
        Codigo Prestacion	25	30
        Tipo de Prestacion	31	31
        Cantidad de prestacion	43	45
        Fecha 	49	54
        Dlegacion Emisora	58	59
        N Orden	63	68
        Tipo de Orden	72	72
        Importe	76	90
        Letra Espec. Prescriptor	94	94
        N Matricula - Prescriptor	98	107
        Provincia de Matricula	111	111
        Letra Espec. Efector	115	115
        N Matricula - Efector	119	128
        Provincia de Matricula	132	132
        Transacion	136	141
        Prestador Prescriptor	145	150
        """
        nro_prestador_cedir = '051861'
        tipo_prestacion = '1'  # ambulatorio
        cantidad = 1
        fecha = estudio.fecha.strftime('%d%m%y')  # DDMMAA
        dlegacion_emisora = '0'
        nro_de_orden = '0'
        tipo_orden = '0'
        letra_espec_prescriptor = 'M'  #  El la letra que identifica la especialidad del profesional (M= medico, B= bioquimico, etc)
        nro_matricula_prescriptor = estudio.medico.matricula
        provincia_matricula = 'S'  # santa Fe
        transacion = estudio.nro_de_orden
        prestador_prescriptor = 0

        fila_0_a_50 = '  {0}{1}'.format(nro_prestador_cedir, estudio.paciente.nroAfiliado, estudio.practica.codigo_medico_osde,
                                 )



        return fila_0_a_50