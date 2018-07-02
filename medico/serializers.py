from rest_framework import serializers
from medico.models import Medico


class MedicoSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Medico
        fields = (u'id', u'nombre', u'apellido', )


from estudio.models import estudio
class PagoMedicoSerializer(serializers.ModelSerializer):

    days_since_joined = serializers.SerializerMethodField()

    class Meta:
        model = Estudio
        fields = ('nombre_cliente', )

    def get_days_since_joined(self, obj):
        return self.context.get('calculador')



# NewRow("MontoIVA21Estudio") = Format(pagoDelCorrespondiente * 0.21, "############0.00")
# NewRow("MontoIVA10.5Estudio") = 0
# NewRow("Paciente") = banderaPCF & est.paciente.nombreCompleto
# NewRow("Fecha") = est.fechaEstudio
# NewRow("Importe") = String.Format("{0:f2}", importeEstudio)
# NewRow("ImporteNeto") = String.Format("{0:f2}", (importeEstudio * (100 - porcentaje.Cedir)) / 100)
# NewRow("Fecha Cobro") = est.fechaCobro
# NewRow("Obra Social") = est.obraSocial.ObraSocial
# NewRow("Práctica") = est.practica.Estudio
# NewRow("Actuante") = est.medicoActuante.nombreCompleto
# NewRow("Solicitante") = est.medicoSolicitante.nombreCompleto
# NewRow("%RetencionCedir") = String.Format("{0}%", porcentaje.Cedir)
# NewRow("%Medico") = String.Format("{0}% ({1:0.##}%)", porcentaje.Medico, porcentaje.GetEfectivo)
# NewRow("G.A.") = String.Format("{0}%", cLinea.gastosAdministrativos)
# NewRow("Pago") = String.Format("{0:f2}", pagoDelCorrespondiente)
# NewRow("Total") = String.Format("{0:f2}", pagoDelCorrespondiente + IVASobreImportePagoAlMedico)
# NewRow("Cobrado") = est.PagoContraFactura