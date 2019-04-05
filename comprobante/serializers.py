from itertools import groupby
from rest_framework import serializers

from anestesista.calculador_honorarios.calculador_honorarios import CalculadorHonorariosAnestesista

from .models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado

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
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    honorarios_medicos = serializers.SerializerMethodField()
    honorarios_anestesistas = serializers.SerializerMethodField()
    retencion_impositiva = serializers.SerializerMethodField()
    retencion_cedir = serializers.SerializerMethodField()
    sala_recuperacion = serializers.SerializerMethodField()
    total_medicamentos = serializers.SerializerMethodField()
    total_material_especifico = serializers.SerializerMethodField()
    
    class Meta:
        model = Comprobante
        fields = ('id',
                  'nombre_cliente',
                  'nro_cuit',
                  'sub_tipo',
                  'numero',
                  'responsable',
                  'nro_terminal',
                  'total_facturado',
                  'total_cobrado',
                  'fecha_emision',
                  'tipo_comprobante',
                  'gravado',
                  'importe_gravado_afip',  # neto
                  'importe_alicuota_afip',  # iva
                  'honorarios_medicos',
                  'honorarios_anestesistas',
                  'retencion_impositiva',
                  'retencion_cedir',
                  'sala_recuperacion',
                  'total_medicamentos',
                  'total_material_especifico')

    def get_honorarios_medicos(self, comprobante):
        return self.context["calculador"].honorarios_medicos

    def get_honorarios_anestesistas(self, comprobante):
        return self.context["calculador"].anestesia

    def get_retencion_impositiva(self, comprobante):
        return self.context["calculador"].retencion_impositiva

    def get_retencion_cedir(self, comprobante):
        return self.context["calculador"].retencion_cedir

    def get_sala_recuperacion(self, comprobante):
        return self.context["calculador"].sala_recuperacion

    def get_total_medicamentos(self, comprobante):
        return self.context["calculador"].total_medicamentos

    def get_total_material_especifico(self, comprobante):
        return self.context["calculador"].total_material_especifico

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
# Retencion Impositiva
# Retencion Cedir (GA)
# Sala de recuperacion
# Retencion Anestesia --> ya se esta mostrando. Aplicar 10% a la suma de todo es una opcion, o bien recorrer cada estudio y aplicar el porcentaje de cada anestesista. Sumarlos y mostrar eso es la otra opcion.
# total Medicamentos         |
# total Material especifico  |  --> Estos 2 hoy aparecen juntos como TotalMedicacion, pero deben ir separados

"""
NOTA: el calculo de honorario medico se aplican las mismas reglas que pago a medico. Si el estudio esta pagado al medico, no importa, volver a aplicar las reglas porque hay qye mostrar lo que se deberia pagar, y no lo que se pago.
      calculo de honorario anestesia sale del campo "anestesia" del estudio. Sino esta cargado se muestra 0 (cero)

NOTA 2: del calculo de pago a medico, se desprenden otros valores como "Retencion Impositiva" y "Gastos Administriativos".
        Estos valores deben ser sumados por separado y mostrado en diferentes columnas.


"""
