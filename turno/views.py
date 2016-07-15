import simplejson
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Q
from rest_framework import viewsets
from turno.models import Turno, InfoTurno
from estudio.models import Estudio
from managers.models import AuditLog, Usuario
from utils.security import encode
from turno.serializers import InfoTurnoSerializer


def anunciar(request, id_turno):
    response_dict = {}

    try:
        turno = Turno.objects.get(id=id_turno)
    except Turno.DoesNotExist:
        response_dict['status'] = False
        response_dict['message'] = "Error, no existe turno"
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)

    try:
        practicas = turno.practicas.all()
        for practica in practicas:
            estudio = Estudio()
            estudio.paciente_id = turno.paciente.id
            estudio.practica_id = practica.id
            estudio.fechaEstudio = turno.fechaTurno
            estudio.motivoEstudio = ""
            estudio.informe = ""
            estudio.medico_id = turno.medico.id
            estudio.obraSocial_id = turno.obraSocial.id
            estudio.medicoSolicitante_id = turno.medico.id
            estudio.idFacturacion = 0
            estudio.nroDeOrden = ""
            estudio.anestesista_id = 1
            estudio.esPagoContraFactura = 0
            estudio.fechaCobro = None
            estudio.importeEstudio = 0
            estudio.importeMedicacion = 0
            estudio.pagoContraFactura = 0
            estudio.diferenciaPaciente = 0
            estudio.pension = 0
            estudio.importePagoMedico = 0
            estudio.importePagoMedicoSol = 0
            estudio.diferenciaPacienteMedicacion = None
            estudio.nroPagoMedicoAct = None
            estudio.nroPagoMedicoSol = None
            estudio.importeCobradoPension = 0
            estudio.importeCobradoArancelAnestesia = 0
            estudio.importeEstudioCobrado = 0
            estudio.importeMedicacionCobrado = 0
            estudio.arancelAnestesia = 0
            estudio.save()
            estudio.public_id = encode(estudio.id)
            estudio.save()

            #log estudio
            log = AuditLog()
            log.user = Usuario.objects.get(id=int(request.session.get('cedir_user_id')))
            log.userActionId = 1
            log.objectTypeId = 1
            log.objectId = estudio.id
            log.dateTime = datetime.now()
            log.observacion = 'creado desde turnos'
            log.save()

        response_dict['status'] = True
        response_dict['message'] = "Success"
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)
    except Exception, err:
        response_dict['status'] = False
        response_dict['message'] = str(err)
        json = simplejson.dumps(response_dict)
        return HttpResponse(json)


class InfoTurnoViewSet(viewsets.ModelViewSet):
    model = InfoTurno
    queryset = InfoTurno.objects.all()
    serializer_class = InfoTurnoSerializer

    def get_queryset(self):
        queryset = InfoTurno.objects.all()
        medico_id = self.request.query_params.get(u'medico')
        practica_ids = self.request.query_params.get(u'practicas')
        obra_social_ids = self.request.query_params.get(u'obras_sociales')

        if medico_id:
            queryset = queryset.filter(Q(medico=medico_id) | Q(medico__isnull=True))

        if obra_social_ids:
            queryset = queryset.filter(Q(obra_sociales__id__in=obra_social_ids.split(u',')) | Q(obra_sociales__isnull=True))

        if practica_ids:
            queryset = queryset.filter(Q(practicas__id__in=practica_ids.split(u',')) | Q(practicas__isnull=True))

        return queryset.distinct()

