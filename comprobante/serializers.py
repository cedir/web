from rest_framework import serializers
from comprobante.models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado

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
    days_since_joined = serializers.SerializerMethodField()

    class Meta:
        model = Comprobante
        fields = ('nombre_cliente',
                  'sub_tipo',
                  'numero',
                  'nro_terminal',
                  'total_facturado',
                  'total_cobrado',
                  'fecha_emision',
                  'tipo_comprobante',
                  'days_since_joined',
                  'estado',
                  'neto',
                  'IVA',
                  'honorarios',
                  'anestesia',
                  'retencion_impositiva',
                  'retencion_cedir',
                  'sala_recuperacion',
                  'medicamentos',
                  'material_especifico')

    def get_days_since_joined(self, obj):
        return self.context.get('calculador')


# Columnas Actuales
# dr("Tipo") = c.TipoComprobante.Descripcion & " " & c.SubTipo.ToUpper() + "  -   " + c.Responsable.ToUpper()
# dr("Nro") = c.NroComprobante.ToString()
# dr("Estado") = c.Estado
# dr("Fecha") = c.FechaEmision.ToString().Remove(10)
# dr("Cliente") = c.NombreCliente.ToUpper()
# dr("TotalFacturado") = Format(c.TotalFacturado, "#################0.00")
# dr("TotalCobrado") = Format(0.0, "#################0.00")
# dr("TotalFacturado") = Format(0.0, "#################0.00")
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
