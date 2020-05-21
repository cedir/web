# pylint: disable=unused-argument
from decimal import Decimal, ROUND_UP
from datetime import date
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from comprobante.models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado, ID_TIPO_COMPROBANTE_LIQUIDACION
from settings import CEDIR_PTO_VENTA, BRUNETTI_PTO_VENTA
from comprobante.afip import Afip

class TipoComprobanteSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = TipoComprobante
        fields = ('id', 'nombre')


class GravadoSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Gravado
        fields = ('id', 'descripcion', 'porcentaje')


class LineaDeComprobanteSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = LineaDeComprobante
        fields = ('id', 'concepto', 'sub_total', 'iva', 'importe_neto')


class ComprobanteSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    lineas = LineaDeComprobanteSerializer(many=True)

    class Meta(object):
        model = Comprobante
        fields = ('id', 'nombre_cliente', 'sub_tipo', 'numero', 'nro_terminal', 'total_facturado', 'total_cobrado',
                  'fecha_emision', 'tipo_comprobante', 'gravado', 'lineas')


class ComprobanteSmallSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()

    class Meta:
        model = Comprobante
        fields = ('id', 'nombre_cliente', 'sub_tipo', 'numero', 'nro_terminal', 'total_facturado', 'total_cobrado',
                  'fecha_emision', 'tipo_comprobante', 'responsable')


class ComprobanteListadoSerializer(serializers.ModelSerializer):
    tipo_comprobante = TipoComprobanteSerializer()
    gravado = GravadoSerializer()
    honorarios_medicos = serializers.SerializerMethodField()
    honorarios_solicitantes = serializers.SerializerMethodField()
    uso_de_materiales = serializers.SerializerMethodField()
    honorarios_anestesistas = serializers.SerializerMethodField()
    retencion_anestesia = serializers.SerializerMethodField()
    retencion_impositiva = serializers.SerializerMethodField()
    retencion_cedir = serializers.SerializerMethodField()
    sala_recuperacion = serializers.SerializerMethodField()
    total_medicamentos = serializers.SerializerMethodField()
    total_material_especifico = serializers.SerializerMethodField()
    neto = serializers.SerializerMethodField()
    iva = serializers.SerializerMethodField()
    total_facturado = serializers.SerializerMethodField()

    class Meta(object):
        model = Comprobante
        fields = ('id',
                  'numero',
                  'responsable',
                  'fecha_emision',
                  'nombre_cliente',
                  'nro_cuit',
                  'tipo_comprobante',
                  'sub_tipo',
                  'nro_terminal',
                  'neto',
                  'iva',
                  'gravado',
                  'total_facturado',
                  'honorarios_medicos',
                  'honorarios_solicitantes',
                  'uso_de_materiales',
                  'retencion_cedir',
                  'retencion_impositiva',
                  'sala_recuperacion',
                  'honorarios_anestesistas',
                  'retencion_anestesia',
                  'total_medicamentos',
                  'total_material_especifico')

    def get_total_facturado(self, comprobante):
        return Decimal(self.context["calculador"].total_facturado).quantize(Decimal('.01'), ROUND_UP)

    def get_neto(self, comprobante):
        return Decimal(self.context["calculador"].neto).quantize(Decimal('.01'), ROUND_UP)

    def get_iva(self, comprobante):
        return Decimal(self.context["calculador"].iva).quantize(Decimal('.01'), ROUND_UP)

    def get_honorarios_medicos(self, comprobante):
        return Decimal(self.context["calculador"].honorarios_medicos).quantize(Decimal('.01'), ROUND_UP)

    def get_honorarios_solicitantes(self, comprobante):
        return Decimal(self.context["calculador"].honorarios_solicitantes).quantize(Decimal('.01'), ROUND_UP)

    def get_retencion_cedir(self, comprobante):
        return Decimal(self.context["calculador"].retencion_cedir).quantize(Decimal('.01'), ROUND_UP)

    def get_uso_de_materiales(self, comprobante):
        return Decimal(self.context["calculador"].uso_de_materiales).quantize(Decimal('.01'), ROUND_UP)

    def get_honorarios_anestesistas(self, comprobante):
        return Decimal(self.context["calculador"].honorarios_anestesia).quantize(Decimal('.01'), ROUND_UP)

    def get_retencion_anestesia(self, comprobante):
        return Decimal(self.context["calculador"].retencion_anestesia).quantize(Decimal('.01'), ROUND_UP)

    def get_retencion_impositiva(self, comprobante):
        return Decimal(self.context["calculador"].retencion_impositiva).quantize(Decimal('.01'), ROUND_UP)

    def get_sala_recuperacion(self, comprobante):
        return Decimal(self.context["calculador"].sala_recuperacion).quantize(Decimal('.01'), ROUND_UP)

    def get_total_medicamentos(self, comprobante):
        return Decimal(self.context["calculador"].total_medicamentos).quantize(Decimal('.01'), ROUND_UP)

    def get_total_material_especifico(self, comprobante):
        return Decimal(self.context["calculador"].total_material_especifico).quantize(Decimal('.01'), ROUND_UP)

class CrearComprobanteLiquidacionSerializer(serializers.ModelSerializer):
    neto = serializers.DecimalField(16, 2)
    concepto = serializers.CharField()
    class Meta(object):
        model = Comprobante
        fields = ('neto', 'nombre_cliente', 'domicilio_cliente', 'nro_cuit', \
            'condicion_fiscal', 'concepto', 'fecha_emision')

    def create(self, validated_data):
        neto = validated_data["neto"]
        concepto = validated_data["concepto"]
        del validated_data["neto"]
        del validated_data["concepto"]
        comprobante = Comprobante.objects.create(
                estado=Comprobante.NO_COBRADO,
                tipo_comprobante=TipoComprobante.objects.get(pk=ID_TIPO_COMPROBANTE_LIQUIDACION),
                nro_terminal=0,
                sub_tipo="",
                responsable="",
                gravado=None,
                numero=Comprobante.objects.filter(
                    tipo_comprobante=ID_TIPO_COMPROBANTE_LIQUIDACION
                ).order_by("-numero")[0].numero + 1,
                total_facturado=neto,
                **validated_data
            )
        linea = LineaDeComprobante.objects.create(
            comprobante=comprobante,
            concepto=concepto,
            importe_neto=neto,
            iva=0,
            sub_total=neto
        )
        return comprobante
class CrearComprobanteAFIPSerializer(serializers.ModelSerializer):
    neto = serializers.DecimalField(16, 2)
    concepto = serializers.CharField()
    # Traigo las ids como campos numericos para no tener que mandar un diccionario con todo el gravado
    # Debe haber una forma estandar y ya hecha de hacer esto en django, pero no la encontre
    tipo_comprobante_id = serializers.IntegerField()
    gravado_id = serializers.IntegerField()
    class Meta(object):
        model = Comprobante
        fields = ('tipo_comprobante_id', 'sub_tipo', 'responsable', 'gravado_id', \
            'neto', 'nombre_cliente', 'domicilio_cliente', 'nro_cuit', 'condicion_fiscal', 'concepto')

    def validate_gravado_id(self, value):
        try:
            Gravado.objects.get(pk=value)
        except Gravado.DoesNotExist:
            raise ValidationError("id de gravado invalida")
        return value

    def validate_tipo_comprobante_id(self, value):
        try:
            TipoComprobante.objects.get(pk=value)
        except Gravado.DoesNotExist:
            raise ValidationError("id de tipo_comprobante invalida")
        return value

    def validate_sub_tipo(self, value):
        if value not in ('A', 'B'):
            raise serializers.ValidationError('"sub_tipo" debe ser "A" o B"')
        return value

    def validate_responsable(self, value):
        if value not in ('Cedir', 'Brunetti'):
            raise serializers.ValidationError('"responsable" debe ser "Cedir" o Brunetti"')
        return value

    def create(self, validated_data):
        neto = validated_data["neto"]
        gravado = Gravado.objects.get(pk=validated_data['gravado_id'])
        responsable = validated_data['responsable']
        tipo_comprobante = TipoComprobante.objects.get(pk=validated_data['tipo_comprobante_id'])
        iva = neto * gravado.porcentaje / Decimal("100.00")
        total = neto + iva
        concepto = validated_data["concepto"]
        del validated_data["neto"]
        del validated_data["concepto"]
        comprobante = Comprobante(
                estado=Comprobante.NO_COBRADO,
                numero=0, # el numero nos lo va a dar la afip cuando emitamos
                fecha_emision=date.today(),
                total_facturado=total,
                nro_terminal=CEDIR_PTO_VENTA if responsable == "Cedir" else BRUNETTI_PTO_VENTA,
                **validated_data
            )
        linea = LineaDeComprobante(
            comprobante=comprobante,
            concepto=concepto,
            importe_neto=neto,
            iva=iva,
            sub_total=total
        )
        Afip().emitir_comprobante(comprobante, [linea])
        comprobante.save()
        linea.comprobante = comprobante
        linea.save()
        return comprobante

def crear_comprobante_serializer_factory(data):
    if data["tipo_comprobante_id"] == ID_TIPO_COMPROBANTE_LIQUIDACION:
        return CrearComprobanteLiquidacionSerializer(data=data)
    else:
        return CrearComprobanteAFIPSerializer(data=data)