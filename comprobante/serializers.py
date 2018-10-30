from itertools import groupby
from rest_framework import serializers
from comprobante.models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado
from anestesista.calculador_honorarios.calculador_honorarios import CalculadorHonorariosAnestesista


class TipoComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComprobante
        fields = ('id', 'nombre')


class GravadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gravado
        fields = ('id', 'descripcion', 'porcentaje')


class LineaDeComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaDeComprobante
        fields = ('id', 'concepto', 'sub_total', 'iva', 'importe_neto')


class ComprobanteSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    lineas = LineaDeComprobanteSerializer(many=True)

    class Meta:
        model = Comprobante
        fields = ('id', 'nombre_cliente', 'sub_tipo', 'numero', 'nro_terminal', 'total_facturado', 'total_cobrado',
                  'fecha_emision', 'tipo_comprobante', 'gravado', 'lineas')


class ComprobanteListadoSerializer(serializers.ModelSerializer):
    # tipo_comprobante = TipoComprobanteSerializer()
    # gravado = GravadoSerializer()
    honorarios_medicos = serializers.SerializerMethodField()
    honorarios_anestesistas = serializers.SerializerMethodField()

    class Meta:
        model = Comprobante
        fields = ('nombre_cliente',
                  'nro_cuit',
                  'sub_tipo',
                  'numero',
                  'nro_terminal',
                  'total_facturado',
                  'total_cobrado',
                  'fecha_emision',
                  'tipo_comprobante',
                  'estado',
                  'importe_gravado_afip',  # neto
                  'importe_alicuota_afip',  # iva
                  'honorarios_medicos',
                  'honorarios_anestesistas',
                  'retencion_impositiva',
                  'retencion_cedir',
                  'sala_recuperacion',
                  'medicamentos',
                  'material_especifico')

    def get_honorarios_medicos(self, comprobante):
        # self.context.get('calculador')
        # presentacion = comprobante.presentacion
        #
        # return presentacion.get_total_honorarios()
        #
        # # TODO: decir si mover esto a presentacion
        # estudios = presentacion.estudios.all()
        #
        # total = 0
        # for estudio in estudios:
        #     honorario = calculate_honorario(estudio)
        #     total +=honorario
        #
        # return total
        return 0

    def get_honorarios_anestesistas(self, comprobante):
        # estudios_todos = comprobante.presentacion.get().estudios.all().order_by('fecha','paciente','obra_social')
        # grupos_de_estudios = groupby(estudios_todos, lambda e: (e.fecha, e.paciente, e.obra_social))
        #
        total = 0
        # for (fecha, paciente, obra_social), grupo in grupos_de_estudios:
        #     estudios = list(grupo)
        #
        #     calculador_honorarios = CalculadorHonorariosAnestesista(estudios[0].anestesista, estudios, estudios[0].obra_social)
        #     result = calculador_honorarios.calculate()
        #     ara = result.get('ara')
        #     if ara:
        #         total += ara.get('retencion')   # TODO: validar que valor se toma con Mariana
        #     no_ara = result.get('no_ara')
        #     if no_ara:
        #         total += no_ara.get('a_pagar')
        return total

# Columnas Actuales
# dr("Tipo") = c.TipoComprobante.Descripcion & " " & c.SubTipo.ToUpper() + "  -   " + c.Responsable.ToUpper()
# dr("Nro") = c.NroComprobante.ToString()
# dr("Estado") = c.Estado
# dr("Fecha") = c.FechaEmision.ToString().Remove(10)
# dr("Cliente") = c.NombreCliente.ToUpper()
# dr("TotalFacturado") = Format(c.TotalFacturado, "#################0.00")
# dr("Neto") = Format(0.0, "#################0.00")
# dr("IVA") = Format(0.0, "#################0.00")
# dr("Honorarios") = Format(0.0, "#################0.00")
# dr("Anestesia") = Format(0.0, "#################0.00")
# dr("TotalMedicacion") = Format(0.0, "#################0.00")
#
#
# Columnas extras que hay que mostrar:
# Retencion Imposotva
# Retencion Cedir (GA)
# Sala de recuperacion
# Retencion Anestesia --> ya se esta mostrando. Aplicar 10% a la suma de todo es una opcion, o bien recorrer cada estudio y aplicar el porcentaje de cada anestesista. Sumarlos y mostrar eso es la otra opcion.
# Medicamentos         |
# Material especifico  |  --> Estos 2 hoy aparecen juntos como TotalMedicacion, pero deben ir separados
