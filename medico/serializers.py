from datetime import date
from decimal import Decimal

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from estudio.models import Estudio
from comprobante.models import ID_GRAVADO_EXENTO, ID_GRAVADO_INSCRIPTO_10_5, ID_GRAVADO_INSCRIPTO_21
from paciente.serializers import PacienteSerializer
from obra_social.serializers import ObraSocialSerializer
from practica.serializers import PracticaSerializer

from .models import Medico, PagoMedico
from .calculo_honorarios.calculador import CalculadorHonorariosPagoMedico
from .calculo_honorarios.porcentajes import Porcentajes

class MedicoSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Medico
        fields = ('id', 'nombre', 'apellido', 'matricula')


class PagoMedicoSerializer(serializers.ModelSerializer):

    medico = MedicoSerializer()

    class Meta:
        model = PagoMedico
        fields = ('id', 'fecha', 'medico', 'observacion')


class ListNuevoPagoMedicoSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    obra_social = ObraSocialSerializer()
    medico_actuante = MedicoSerializer(source='medico')
    medico_solicitante = MedicoSerializer()
    practica = PracticaSerializer()
    importe_neto = serializers.SerializerMethodField()
    retencion_cedir = serializers.SerializerMethodField()
    porcentaje_medico = serializers.SerializerMethodField()
    gastos_administrativos = serializers.SerializerMethodField()
    pago = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    importe_iva_21 = serializers.SerializerMethodField()
    importe_iva_105 = serializers.SerializerMethodField()

    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'importe_estudio', 'importe_neto', 'fecha_cobro', 'paciente', 'obra_social', 'medico_actuante',
                  'medico_solicitante', 'practica', 'retencion_cedir', 'porcentaje_medico', 'gastos_administrativos',
                  'pago_contra_factura', 'pago', 'importe_iva_21', 'importe_iva_105', 'total')

    def get_importe_neto(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        return calculador.get_importe() - calculador.cedir

    def get_retencion_cedir(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        return calculador.cedir

    def get_porcentaje_medico(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        medico: Medico = self.context.get('medico')
        porcentajes = Porcentajes(estudio)
        if estudio.medico == medico:
            return porcentajes.actuante
        else:
            return porcentajes.solicitante


    def get_gastos_administrativos(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        return calculador.porcentaje_GA() * calculador.get_importe() / Decimal('100.00')

    def get_pago(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        medico: Medico = self.context.get('medico')
        if estudio.medico == medico:
            return calculador.actuante
        else:
            return calculador.solicitante

    def get_total(self, estudio: Estudio) -> Decimal:
        return self.get_pago(estudio) + self.get_importe_iva_105(estudio) + self.get_importe_iva_21(estudio)

    def get_importe_iva_21(self, estudio: Estudio) -> Decimal:
        correspondiente = self.get_pago(estudio)
        if estudio.presentacion.comprobante.gravado.id == ID_GRAVADO_INSCRIPTO_21:
            correspondiente * Decimal(0.21)

    def get_importe_iva_105(self, estudio: Estudio) -> Decimal:
        correspondiente = self.get_pago(estudio)
        if estudio.presentacion.comprobante.gravado.id == ID_GRAVADO_INSCRIPTO_21:
            correspondiente * Decimal(0.105)


class LineaPagoMedicoSerializer(serializers.Serializer):
    estudio_id = serializers.IntegerField()
    importe = serializers.DecimalField(max_digits=16, decimal_places=2)


class CreateNuevoPagoMedicoSerializer(serializers.ModelSerializer):
    """
    {"medico": 11, "lineas": [{"estudio_id": 22, "importe": 22.22}, ...]}

    """
    medico = serializers.IntegerField()
    lineas = LineaPagoMedicoSerializer(many=True)

    def validate(self, data):
        medico = Medico.objects.get(pk=data['medico'])
        for l in data['lineas']:
            estudio : Estudio = Estudio.objects.get(pk=l.estudio_id)
            importe : Decimal = l.importe
            if estudio.fecha_cobro is None:
                ValidationError(f"El estudio {l.estudio_id} aun no fue cobrado")
            if estudio.medico == medico:
                if estudio.pago_medico_actuante != 0:
                    raise ValidationError(f'El estudio {l.estudio_id} ya esta pago para este actuante.')
                data['es_actuante'] = True
            elif estudio.medico_solicitante == medico:
                if estudio.pago_medico_solicitante != 0:
                    raise ValidationError(f'El estudio {l.estudio_id} ya esta pago para este solicitante.')
                data['es_actuante'] = False
            if importe == 0:
                raise ValidationError('El importe del pago del estudio no puede ser 0.')

    def create(self, validated_data) -> PagoMedico:
        medico = Medico.objects.get(pk=validated_data['medico'])
        for l in validated_data['lineas']:
            estudio : Estudio = Estudio.objects.get(pk=l.estudio_id)
            importe : Decimal = l.importe
            if validated_data['es_actuante']:
                estudio.pago_medico_actuante = importe
            else:
                estudio.pago_medico_solicitante = importe
            estudio.save()
        return PagoMedico.create(
            fecha=date.today(),
            medico=Medico,
            observacion='',
        )

    class Meta:
        model = PagoMedico
        fields = (
            'medico',
            'lineas'
        )

class GETLineaPagoMedicoSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    obra_social = ObraSocialSerializer()
    medico_actuante = MedicoSerializer(source='medico')
    medico_solicitante = MedicoSerializer()
    practica = PracticaSerializer()

    class Meta:
        model = Estudio
        fields = ('fecha', 'paciente', 'obra_social', 'medico_actuante', 'medico_solicitante', 'practica',
                  'importe_pago_medico', 'importe_pago_medico_solicitante', 'pago_medico_actuante', 'pago_medico_solicitante', )
