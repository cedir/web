from decimal import Decimal
from rest_framework import serializers
from medico.models import Medico, PagoMedico
from estudio.models import Estudio
from paciente.serializers import PacienteSerializer
from obra_social.serializers import ObraSocialSerializer
from practica.serializers import PracticaSerializer


class MedicoSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Medico
        fields = (u'id', u'nombre', u'apellido', u'matricula')


class PagoMedicoSerializer(serializers.ModelSerializer):

    medico = MedicoSerializer()

    class Meta:
        model = PagoMedico
        fields = (u'id', u'fecha', u'medico', u'observacion')


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

    # NewRow("Paciente") = banderaPCF & est.paciente.nombreCompleto
    # NewRow("Fecha") = est.fechaEstudio
    # NewRow("Importe") = String.Format("{0:f2}", importeEstudio)
    # NewRow("ImporteNeto") = String.Format("{0:f2}", (importeEstudio * (100 - porcentaje.Cedir)) / 100)
    # NewRow("Fecha Cobro") = est.fechaCobro
    # NewRow("Obra Social") = est.obraSocial.ObraSocial
    # NewRow("Practica") = est.practica.Estudio
    # NewRow("Actuante") = est.medicoActuante.nombreCompleto
    # NewRow("Solicitante") = est.medicoSolicitante.nombreCompleto
    # NewRow("%RetencionCedir") = String.Format("{0}%", porcentaje.Cedir)
    # NewRow("%Medico") = String.Format("{0}% ({1:0.##}%)", porcentaje.Medico, porcentaje.GetEfectivo)
    # NewRow("G.A.") = String.Format("{0}%", cLinea.gastosAdministrativos)
    # NewRow("Pago") = String.Format("{0:f2}", pagoDelCorrespondiente)
    # NewRow("Total") = String.Format("{0:f2}", pagoDelCorrespondiente + IVASobreImportePagoAlMedico)
    # NewRow("Cobrado") = est.PagoContraFactura
    # NewRow("MontoIVA21Estudio") = Format(pagoDelCorrespondiente * 0.21, "############0.00")
    # NewRow("MontoIVA10.5Estudio") = 0

    class Meta:
        model = Estudio
        fields = ('id', 'fecha', 'importe_estudio', 'importe_neto', 'fecha_cobro', 'paciente', 'obra_social', 'medico_actuante',
                  'medico_solicitante', 'practica', 'retencion_cedir', 'porcentaje_medico', 'gastos_administrativos',
                  'pago_contra_factura', 'pago', 'importe_iva_21', 'importe_iva_105', 'total')

    def get_days_since_joined(self, obj):
        return self.context.get('calculador')

    def get_importe_neto(self, obj):
        #String.Format("{0:f2}", (importeEstudio * (100 - porcentaje.Cedir)) / 100)
        return Decimal(0)

    def get_retencion_cedir(self, obj):
        #String.Format("{0}%", porcentaje.Cedir)
        return Decimal(0)

    def get_porcentaje_medico(self, obj):
        #String.Format("{0}% ({1:0.##}%)", porcentaje.Medico, porcentaje.GetEfectivo)
        return Decimal(0)

    def get_gastos_administrativos(self, obj):
        #String.Format("{0}%", cLinea.gastosAdministrativos)
        return Decimal(0)

    def get_pago(self, obj):
        #String.Format("{0:f2}", pagoDelCorrespondiente)
        return Decimal(0)

    def get_total(self, obj):
        #String.Format("{0:f2}", pagoDelCorrespondiente + IVASobreImportePagoAlMedico)
        return Decimal(0)

    def get_importe_iva_21(self, obj):
        #Format(pagoDelCorrespondiente * 0.21, "############0.00")
        return Decimal(0)

    def get_importe_iva_105(self, obj):
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
