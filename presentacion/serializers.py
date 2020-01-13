from decimal import Decimal
from datetime import date

from rest_framework import serializers
from rest_framework import status
from presentacion.models import Presentacion
from obra_social.models import ObraSocial
from comprobante.models import Comprobante, TipoComprobante, Gravado, LineaDeComprobante, ID_TIPO_COMPROBANTE_LIQUIDACION
from estudio.models import Estudio
from estudio.serializers import EstudioDePresetancionRetrieveSerializer, EstudioDePresetancionCreateUpdateSerializer
from obra_social.serializers import ObraSocialSerializer
from comprobante.serializers import ComprobanteSerializer
from comprobante.afip import Afip, AfipErrorRed, AfipErrorValidacion

class EstadoField(serializers.Field):
    def to_representation(self, value):
        return Presentacion.ESTADOS[value][1]

    def to_internal_value(self, data):
        return filter(lambda estado: estado[1] == data, Presentacion.ESTADOS)[0][0]

class PresentacionSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = EstadoField()

    class Meta:
        model = Presentacion

class PresentacionRetrieveSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer()
    comprobante = ComprobanteSerializer()
    estado = EstadoField()
    estudios = EstudioDePresetancionRetrieveSerializer(many=True)

    class Meta:
        model = Presentacion

class PresentacionCreateUpdateSerializer(serializers.ModelSerializer):
    obra_social_id = serializers.IntegerField()
    estudios = serializers.ListField()
    comprobante = serializers.DictField()

    def to_representation(self, instance):
        return {
            u'id': instance.id,
            u'obra_social_id': instance.obra_social_id,
            u'periodo': instance.periodo,
            u'fecha': instance.fecha,
            u'comprobante': ComprobanteSerializer(instance.comprobante).data
        }

    def validate(self, data):
        if ObraSocial.objects.get(pk=data['obra_social_id']).is_particular_or_especial():
            raise serializers.ValidationError('La Obra Social no puede ser Particular o Particular Especial')
        comprobante_data = data['comprobante']
        if "tipo_id" not in data['comprobante']:
            raise serializers.ValidationError('El campo "tipo_id" es obligatorio en "comprobante".')
        # Las liquidaciones no se emiten en AFIP.
        if data["comprobante"]["tipo_id"] == ID_TIPO_COMPROBANTE_LIQUIDACION:
            data["comprobante"]["nro_terminal"] = 0
            data["comprobante"]["sub_tipo"] = ""
            data["comprobante"]["responsable"] = ""
            data["comprobante"]["gravado_id"] = None
        else:
            if "nro_terminal" not in comprobante_data:
                raise serializers.ValidationError('El campo "nro_terminal" es obligatorio en "comprobante" cuando el tipo no es Liquidacion.')
            if "sub_tipo" not in comprobante_data:
                raise serializers.ValidationError('El campo "sub_tipo" es obligatorio en "comprobante" cuando el tipo no es Liquidacion.')
            if "responsable" not in comprobante_data:
                raise serializers.ValidationError('El campo "responsable" es obligatorio en "comprobante" cuando el tipo no es Liquidacion.')
            if "gravado_id" not in comprobante_data:
                raise serializers.ValidationError('El campo "gravado_id" es obligatorio en "comprobante" cuando el tipo no es Liquidacion.')
            if comprobante_data['responsable'] not in ('Cedir', 'Brunetti'):
                raise serializers.ValidationError('"responsable" debe ser "Cedir" o Brunetti"')
            if comprobante_data['sub_tipo'] not in ('A', 'B'):
                raise serializers.ValidationError('"sub_tipo" debe ser "A" o B"')
        for estudio_data in data['estudios']:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            if estudio.obra_social_id != data['obra_social_id']:
                raise serializers.ValidationError('La presentacion contiene un estudio de otra Obra Social')
        return data

    def create(self, validated_data):
        obra_social = ObraSocial.objects.get(pk=validated_data['obra_social_id'])
        periodo = validated_data['periodo']
        estudios_data = validated_data['estudios']
        comprobante_data = validated_data['comprobante']
        tipo_comprobante = TipoComprobante.objects.get(pk=comprobante_data['tipo_id'])
        sub_tipo = comprobante_data['sub_tipo']
        nro_terminal = comprobante_data['nro_terminal']
        responsable = comprobante_data['responsable']
        gravado = Gravado.objects.get(pk=comprobante_data['gravado_id']) \
            if tipo_comprobante.id != ID_TIPO_COMPROBANTE_LIQUIDACION else None
        # Si no es liquidacion, el numero de comprobante nos lo va a dar la Afip.
        nro_comprobante = Comprobante.objects.filter(
            tipo_comprobante=tipo_comprobante,
            nro_terminal=nro_terminal,
            responsable=responsable,
            sub_tipo=sub_tipo).order_by("-numero")[0].numero + 1 \
            if tipo_comprobante.id == ID_TIPO_COMPROBANTE_LIQUIDACION else 0
        neto = sum([Decimal(e['importe_estudio']) for e in estudios_data])
        iva = neto * gravado.porcentaje if tipo_comprobante.id != ID_TIPO_COMPROBANTE_LIQUIDACION else 0
        total = neto + iva
        validated_data['iva'] = iva
        validated_data['total'] = neto
        validated_data['total_facturado'] = total
        comprobante = Comprobante(
            nombre_cliente=obra_social.nombre,
            domicilio_cliente=obra_social.direccion,
            nro_cuit=obra_social.nro_cuit,
            condicion_fiscal=obra_social.condicion_fiscal,
            responsable=responsable,
            tipo_comprobante=tipo_comprobante,
            sub_tipo=sub_tipo,
            nro_terminal=nro_terminal,
            estado=Comprobante.NO_COBRADO,
            numero=nro_comprobante,
            total_facturado=total,
            fecha_emision=date.today(),
            gravado=gravado,
        )
        linea = LineaDeComprobante(
            comprobante=comprobante,
            concepto='FACTURACION CORRESPONDIENTE A ' + periodo,
            importe_neto=neto,
            iva=iva,
            sub_total=total
        )
        if tipo_comprobante.id != ID_TIPO_COMPROBANTE_LIQUIDACION:
            # Si esto falla, el catch se hace desde la view llamante
            Afip().emitir_comprobante(comprobante, [linea])
        comprobante.save()
        linea.comprobante = comprobante # Esto es porque sino genera un error la id del comprobante
        validated_data['comprobante'] = comprobante
        linea.save()
        del validated_data['estudios']
        del validated_data['comprobante']
        presentacion = Presentacion.objects.create(
            comprobante=comprobante,
            estado=Presentacion.PENDIENTE,
            **validated_data
        )
        for estudio_data in estudios_data:
            estudio = Estudio.objects.get(pk=estudio_data['id'])
            estudio.nro_de_orden = estudio_data['nro_de_orden']
            estudio.importe_estudio = estudio_data['importe_estudio']
            estudio.pension = estudio_data['pension']
            estudio.diferencia_paciente = estudio_data['diferencia_paciente']
            estudio.arancel_anestesia = estudio_data['arancel_anestesia']
            estudio.presentacion = presentacion
            estudio.save()
        return presentacion

    class Meta:
        model = Presentacion
        fields = (
            u'id',
            u'obra_social_id',
            u'periodo',
            u'fecha',
            u'estudios',
            u'comprobante'
        )