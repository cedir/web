import simplejson
from datetime import datetime
from django.http import HttpResponse
from turno.models import Turno
from estudio.models import Estudio, DetalleEstudio, PagoCobroEstudio
from managers.models import AuditLog, Usuario


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
            estudio.set_public_id()
            estudio.save()  # TODO: gestionar error: si falla en algun save, ver si se puede hacer rollback, sino informar del error grave! porque se desconfiguran los id de estudio

            detalleEstudio = DetalleEstudio()
            detalleEstudio.medico_id = turno.medico.id
            detalleEstudio.obraSocial_id = turno.obraSocial.id
            detalleEstudio.medicoSolicitante_id = turno.medico.id
            detalleEstudio.idFacturacion = 0
            detalleEstudio.nroDeOrden = ""
            detalleEstudio.idAnestesista = 1
            detalleEstudio.esPagoContraFactura = 0
            detalleEstudio.save()

            estudioPagoCobro = PagoCobroEstudio()
            estudioPagoCobro.fechaCobro = None
            estudioPagoCobro.importeEstudio = 0
            estudioPagoCobro.importeMedicacion = 0
            estudioPagoCobro.pagoContraFactura = 0
            estudioPagoCobro.diferenciaPaciente = 0
            estudioPagoCobro.pension = 0
            estudioPagoCobro.importePagoMedico = 0
            estudioPagoCobro.importePagoMedicoSol = 0
            estudioPagoCobro.diferenciaPacienteMedicacion = None
            estudioPagoCobro.nroPagoMedicoAct = None
            estudioPagoCobro.nroPagoMedicoSol = None
            estudioPagoCobro.importeCobradoPension = 0
            estudioPagoCobro.importeCobradoArancelAnestesia = 0
            estudioPagoCobro.importeEstudioCobrado = 0
            estudioPagoCobro.importeMedicacionCobrado = 0
            estudioPagoCobro.arancelAnestesia = 0
            estudioPagoCobro.save()

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
