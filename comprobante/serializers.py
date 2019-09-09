# pylint: disable=unused-argument
from decimal import Decimal, ROUND_UP
from rest_framework import serializers

from .models import Comprobante, LineaDeComprobante, TipoComprobante, Gravado


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
    # Nro
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