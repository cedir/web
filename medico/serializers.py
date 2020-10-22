from decimal import Decimal

from rest_framework import serializers

from estudio.models import Estudio
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
        porcenteajes = Porcentajes(estudio)
        if estudio.medico == medico:
            return porcenteajes.actuante
        else:
            return porcenteajes.solicitante


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
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        #String.Format("{0:f2}", pagoDelCorrespondiente + IVASobreImportePagoAlMedico)
        return Decimal(0)

    def get_importe_iva_21(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        #Format(pagoDelCorrespondiente * 0.21, "############0.00")
        return Decimal(0)

    def get_importe_iva_105(self, estudio: Estudio) -> Decimal:
        calculador : CalculadorHonorariosPagoMedico = self.context.get('calculador')
        return Decimal(0)


class LineaPagoMedicoSerializer(serializers.Serializer):
    estudio_id = serializers.IntegerField()
    importe = serializers.DecimalField(max_digits=16, decimal_places=2)


class CreateNuevoPagoMedicoSerializer(serializers.Serializer):
    """
    {"medico": 11, "lineas": [{"estudio_id": 22, "importe": 22.22}, ...]}

    """
    medico = serializers.IntegerField()
    lineas = LineaPagoMedicoSerializer(many=True)


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
