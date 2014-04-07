# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from managers.model.turno import *
from managers.model.personas import *
from managers.view.turnos import *
import time
import datetime
from datetime import timedelta
from django.db.models import Q
from django.utils import simplejson


spanishDays = {u'Sun': u'domingo', u'Sat': u'sabado', u'Mon': u'lunes', u'Tue': u'martes', u'Wed': u'miercoles',
               u'Thu': u'jueves', u'Fri': u'viernes'}
daysIndexes = {u'domingo': 0, u'lunes': 1, u'martes': 2, u'miercoles': 3, u'jueves': 4, u'viernes': 5, u'sabado': 6}
days = [u'domingo', u'lunes', u'martes', u'miercoles', u'jueves', u'viernes', u'sabado']


class Turnos():
    """
        - Si se elige sala, se muestran los dias, solo para esa sala y todos los medicos.
        - Si se elige sala y medico, se mustran solo los dias en los que atiende el medico
        en la sala seleccionada. Se muestran todos los turnos y horarios.

        - Si no se elige la sala, entonces obligatoriamente se debe elejir Medico y Practicas.
        Para este caso, se mezcalan para los dias que atiende un medico, los rango horarios en los que atiende.
        Se muestran solo esos dias, e idealmente solo los rango horarios sin mostrar el resto del dia.

        - Idealmente, si se elige sala y medico, habria que mostrar no solo los dias que atiende el medico, sino tambien
        solo su rango horario. Esto implica que el resto del dia no se debe ver (no es que se ocultan solo los turnos, sino que se oculta todo, hasta las horas)
    """

    def __init__(self, request):
        self.request = request

    def getTurnosDisponibles(self, **kwargs):
        request = self.request
        #session check
        if request.session.get('cedir_user_id') is None:
            return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

        idPaciente = request.GET.get('id-paciente', kwargs.get('id-paciente')) or None
        idSala = request.GET.get('id-sala',kwargs.get('id-sala')) or 0
        idMedico = request.GET.get('id-medico',kwargs.get('id-medico')) or 0
        idObraSocial = request.GET.get('id-obra-social',kwargs.get('id-obra-social')) or 0

        idPracticas = []
        if request.GET.has_key('id-practicas[]') and request.GET['id-practicas[]'] != "":
            idPracticas = request.GET.getlist('id-practicas[]')
        else:
            byRef = kwargs.get('id-practicas[]', "")
            if byRef != "":
                idPracticas = kwargs['id-practicas[]']

        fecha = ""
        if request.GET.has_key('fecha') and request.GET['fecha'] != "":
            fecha = request.GET['fecha']

        medicos = Medico.objects.all().order_by("apellido")
        obraSociales = ObraSocial.objects.all().order_by('nombre')
        practicas = Practica.objects.all().order_by('-usedLevel', 'descripcion')
        salas = Sala.objects.all().order_by('id')

        pacienteSeleccionado = None
        if idPaciente is None:
            pass
        else:
            pacienteSeleccionado = Paciente.objects.get(id=idPaciente)

        selectedDate = date.today()
        if fecha != "":
            selectedDate = datetime.date(int(fecha.split("/")[2]), int(fecha.split("/")[1]), int(fecha.split("/")[0]))

        selectedDate = selectedDate - timedelta(days=1)  #resto uno ya que nextDay le va a sumar uno luego

        dayLines = []

        if idSala or (idMedico and idPracticas):
            for i in range(0, 4):
                nextDate = self._getNextDate(selectedDate, idSala, idMedico, practicas)
                line = self._getDayLine(nextDate, idSala, idMedico, practicas)
                selectedDate = nextDate
                dayLines.append(line)

        viewTurnos = ViewTurnos(request)
        kwargs = {'dayLines': dayLines, 'pacienteSeleccionado': pacienteSeleccionado, 'idMedico': idMedico, 'medicos': medicos,
                  'obraSociales': obraSociales, 'idObraSocial': idObraSocial, 'practicas': practicas, 'idPracticas': idPracticas,
                  'salas': salas, 'idSala':idSala,'fecha': fecha}
        return viewTurnos.getTurnosDisponibles(**kwargs)

    def getNextDayLine(self):
        request = self.request
        fecha = request.GET['fecha']
        idSala = request.GET['id-sala']
        idMedico = request.GET.get('id-medico') or 0
        sp = fecha.split('-')
        currentDate = datetime.date(int(sp[0]), int(sp[1]), int(sp[2]))
        nextDate = self._getNextDate(currentDate, idSala, idMedico)

        dayLines = []
        dayLines.append(self._getDayLine(nextDate, idSala))
        viewTurnos = ViewTurnos()
        return viewTurnos.getDayLines(dayLines)

    def getBackDayLine(self):
        request = self.request
        fecha = request.GET['fecha']
        idSala = request.GET['id-sala']
        idMedico = request.GET.get('id-medico') or 0
        sp = fecha.split('-')
        currentDate = datetime.date(int(sp[0]), int(sp[1]), int(sp[2]))
        backDate = self._getPreviousDate(currentDate, idSala, idMedico)

        dayLines = []
        dayLines.append(self._getDayLine(backDate, idSala))
        viewTurnos= ViewTurnos()
        return viewTurnos.getDayLines(dayLines)

    #TODO: estan mal los valores por defecto de los paramatros. Revisar en todos lo metodos.
    def _getDayLine(self, fecha, idSala=None, idMedico=None, idPracticas=None):
        #dayLines = []
        line = {}
        line["fecha"] = str(fecha)
        t = time.mktime((fecha.year,fecha.month,fecha.day,0,0,0,0,0,0))
        dia = str(time.strftime("%a", time.gmtime(t) ))
        diaNumero = str(time.strftime("%d", time.gmtime(t) ))
        mes = str(time.strftime("%B", time.gmtime(t) ))
        ano = str(time.strftime("%Y", time.gmtime(t) ))
        line["dia"] = spanishDays[dia] + ' ' + diaNumero + ' de ' + mes + ' del ' + ano

        #WALTER: ver si puede pasar que un turno no se traiga por ser de otro medico y se termine dando un turno
        #encima (misma hora) por aparecer el espacio vacio. Mejorar el validador del crear si es asi.
        turnosConditional = {u'fechaTurno': str(fecha), u'estado__id__lt':  3}
        if idMedico == 0:
            turnosConditional[u'sala__id'] = int(idSala)
        else:
            turnosConditional[u'medico__id'] = idMedico

        arrTurnos = Turno.objects.filter(**turnosConditional)
        line["turnos"] = arrTurnos
        line["disponibilidad"] = self._getDisponibilidad(spanishDays[dia], idSala, idMedico, idPracticas)
        return line

    #WALTER: reescribir _getNextDate y _getPreviousDate ya que son casi iguales y para que se adapten a usar _getDisponibilidadForGivenDay
    #WALTER: ver los valores por defecto de los parametros, creo que estan mal en None.
    def _getNextDate(self, date, idSala=None, idMedico=None, idPracticas=None):
        if idMedico == 0:
            return date + timedelta(days=1)

        t = time.mktime((date.year, date.month, date.day, 0, 0, 0, 0, 0, 0))
        dateDay = unicode(time.strftime("%a", time.gmtime(t)))

        disponibilidades = self._getDisponibilidad(None, idSala, idMedico, idPracticas)

        if len(disponibilidades) == 0:
            return date + timedelta(days=1)

        hshDisponibilidades = {}
        for disp in disponibilidades:
            hshDisponibilidades[disp.dia] = disp.horaInicio

        index = daysIndexes[spanishDays[dateDay]]
        for i in range(0, 7):
            index += 1
            if index == 7:
                index = 0
            if days[index] in hshDisponibilidades:
                return date + timedelta(days=i + 1)

    def _getPreviousDate(self, date, idSala=None, idMedico=None, idPracticas=None):
        if idMedico == 0:
            return date - timedelta(days=1)

        disponibilidades = self._getDisponibilidad(None, idSala, idMedico, idPracticas)
        if len(disponibilidades) == 0:
            return date - timedelta(days=1)

        hshDisponibilidades = {}
        for disp in disponibilidades:
            hshDisponibilidades[disp.dia] = disp.horaInicio

        t = time.mktime((date.year, date.month, date.day, 0, 0, 0, 0, 0, 0))
        dateDay = str(time.strftime("%a", time.gmtime(t)))

        index = daysIndexes[spanishDays[dateDay]]
        for i in range(0, 6):
            index += 1
            if index == 7:
                index = 0
            if hshDisponibilidades.has_key(days[index]):
                return date - timedelta(days=i + 1)


    def _getDisponibilidad(self, dia=None, idSala=None, idMedico=None, idPracticas=None):
        """
        Devuelve la disponibilidad para un dia determinado (Ej Lunes).
            - Si se recibe la sala, se devulve la disponibilidad del dia para todos los medicos que atienden ese dia en esa sala.
            - Si se recibe como paramatro Medico-Practicas, devuelve
            la disponibilidad del dia solo para el medico elegido y en todas las salas (puede atender en mas de una sala
            el mismo dia).
        """
        #TODO: si se quiere agregar horarios a futuro, va a haber que agregar fecha_hasta para la disponibilidad

        disponibilidadConditional = {}

        if dia:
            disponibilidadConditional["dia"] = dia

        if idSala:
            disponibilidadConditional["sala__id"] = idSala
        else:
            disponibilidadConditional["sala__id__in"] = (3, 4, 5, 6, 7) #solo consultorio

        if idMedico:
            disponibilidadConditional[u'medico__id'] = idMedico

        disponibilidades = Disponibilidad.objects.filter(**disponibilidadConditional).order_by('horaInicio')
        return disponibilidades

    def guardar(self):
        request = self.request
        response_dict = {}
        #session check
        if request.session.get('cedir_user_id') is None:
            response_dict['status'] = 0
            response_dict['message'] = "Error, la sesion se ha perdido. Por favor, vuelva a loguearse en otra solapa y vuelva a intentarlo."
            json = simplejson.dumps(response_dict)
            return json

        hora_inicio = request.GET['hora_inicio']
        hora_fin_estimada = request.GET['hora_fin_estimada']
        fecha_turno = request.GET['fecha_turno']
        idMedico = request.GET['id-medico']
        idObraSocial = request.GET['id-obra-social']
        idSala = request.GET['id-sala']
        idPaciente = request.GET['id-paciente']
        idPracticas = request.GET.getlist('id-practicas[]')
        observacion_turno = request.GET['observacion_turno']

        #gte...>=  -  lte...<=  -  gt....>  -  lt....<
        #arrTurnos = Turno.objects.filter(Q(fechaTurno=str(fecha_turno)), Q(horaInicio__lt= hora_inicio, horaFinEstimada__gt = hora_inicio) | Q(horaInicio__lt= hora_fin_estimada, horaFinEstimada__gt = hora_fin_estimada)  )
        arrTurnos = Turno.objects.filter(Q(fechaTurno=str(fecha_turno),sala__id=idSala,estado__id__lt = 3), Q(horaInicio__lte= hora_inicio, horaFinEstimada__gt = hora_inicio)  | Q(horaInicio__lt= hora_fin_estimada, horaFinEstimada__gte = hora_fin_estimada) )
        #w = open('/tmp/debug.w','w')
        #w.write('fecha:' + str(fecha_turno))
        #w.write('Hora:' + str(hora_inicio))
        #w.write('turnos:' + str(arrTurnos))
        #w.close

        if len(arrTurnos) > 0:
          response_dict['status'] = 0
          response_dict['message'] = "Error, se ha detectado superposicion de turnos. Por favor, haga click en Mostrar y vuelva a intentarlo"
          json = simplejson.dumps(response_dict)
          return json

        paciente = Paciente.objects.get(id=idPaciente)
        #medico = Medico.objects.get(id=idMedico)
        #obraSocial = ObraSocial.objects.get(id=idObraSocial)
        #sala = Sala.objects.get(id=idSala)
        practicas = Practica.objects.filter(id__in=idPracticas)


        try :
            turno = Turno()
            turno.horaInicio = hora_inicio
            turno.horaFinEstimada = hora_fin_estimada
            turno.horaFinReal = hora_fin_estimada
            turno.fecha_otorgamiento = datetime.datetime.now()
            turno.fechaTurno = fecha_turno
            turno.observacion = observacion_turno
            turno.paciente = paciente
            turno.medico_id = idMedico
            turno.obraSocial_id = idObraSocial
            turno.sala_id = idSala
            turno.estado_id = 1
            turno.save(force_insert=True)

            for practica in practicas:
                turno.practicas.add(practica)

            turno.save()

            log = AuditLog()
            log.user = Usuario.objects.get(id=int(request.session.get('cedir_user_id')))
            log.userActionId = 1
            log.objectTypeId = 3
            log.objectId = turno.id
            log.dateTime = datetime.datetime.now()
            log.observacion = ''
            log.save()

            response_dict['status'] = 1
            response_dict['message'] = "El turno se ha creado correctamente."
            json = simplejson.dumps(response_dict)
            return json
        except Exception, err:
            return str(err)

    def getBuscarTurnos(self):
        request = self.request
        #session check
        if request.session.get('cedir_user_id') is None:
            return HttpResponseRedirect('?controlador=Root&accion=getLogin&error_id=2&next=%s' % request.path)

        cond = {}

        paciente = ""
        if request.GET.has_key('paciente') and request.GET['paciente'] != "":
            paciente = request.GET['paciente']
            cond["paciente__apellido__icontains"] = paciente

        fecha = ""
        if request.GET.has_key('fecha') and request.GET['fecha'] != "":
            fecha = request.GET['fecha']
            if "/" in fecha:
                fecha = fecha.replace(" ", "")
                fecha = fecha.split("/")[2] + "-" + fecha.split("/")[1] + "-" + fecha.split("/")[0]
            cond["fechaTurno"] = fecha

        idMedico = 0
        if request.GET.has_key('id-medico') and request.GET['id-medico'] != "":
            idMedico = request.GET['id-medico']
            cond["medico__id"] = idMedico

        idSala = 0
        if request.GET.has_key('id-sala') and request.GET['id-sala'] != "":
            idSala = request.GET['id-sala']
            cond["sala__id"] = idSala

        ocultarAnulados = request.GET.get('ocultar-turnos-anulados', "false")
        if ocultarAnulados == "true":
            cond["estado__id__lte"] = 2

        rowsLimit = 110
        #default filter if its empty
        a = cond.keys()
        if len(a) == 0:
            #fecha = date.today() + timedelta(days=1)
            #cond = {"fechaTurno": fecha}
            rowsLimit = 50

        arrTurnos = Turno.objects.filter(**cond).order_by("-fechaTurno",'horaInicio')[:rowsLimit]
        medicos = Medico.objects.all().order_by("apellido")
        obraSociales = ObraSocial.objects.all().order_by('nombre')
        salas = Sala.objects.all().order_by('id')

        viewTurnos = ViewTurnos(request)
        kwargs = {'turnos': arrTurnos, 'fecha': fecha, 'idMedico': idMedico, 'medicos': medicos, 'obraSociales': obraSociales,
                  'salas': salas, 'idSala': idSala, 'paciente': paciente, 'ocultarAnulados': ocultarAnulados}
        return viewTurnos.getBuscarTurnos(**kwargs)

    def getTurno(self):
        request = self.request
        idTruno = request.GET['id']
        turno = Turno.objects.get(id=idTruno)
        createdLog = AuditLog.objects.filter(objectId=int(idTruno),objectTypeId=3,userActionId=1)
        user = None
        if len(createdLog) > 0:
            user = createdLog[0].user.nombreUsuario
        #anuladoLog = None
        #if turno.estado= 3:
          #anuladoLog = Turno.objects.get(objectId=idTruno,objectTypeId=3,userActionId=4)

        viewTurnos = ViewTurnos()
        kwargs = {'turno':turno, 'createdUser':user}
        return viewTurnos.getTurno(**kwargs)

    def update(self):
        request = self.request
        idTurno = request.GET['id-turno']
        idEstado = request.GET['id-estado']
        idObraSocial = request.GET['id-obra-social']
        observacion = request.GET['observacion']
        response_dict = {}

        turno = Turno.objects.get(id=idTurno)

        if (turno is None):
            response_dict['status'] = 0
            response_dict['message'] = "Error, no existe turno"
            json = simplejson.dumps(response_dict)
            return json


        obraSocial = ObraSocial.objects.get(id=idObraSocial)
        #estado = Estado.objects.get(id=idEstado)

        try:
            #turno.estado_id = idEstado
            turno.obraSocial = obraSocial
            turno.observacion = observacion
            turno.save()

            response_dict['status'] = 1
            response_dict['message'] = "El turno se ha guardado correctamente."
            json = simplejson.dumps(response_dict)
            return json
        except Exception, err:
            return str(err)

    def anular(self):
        request = self.request
        idTurno = request.GET['id-turno']
        response_dict = {}

        turno = Turno.objects.get(id=idTurno)
        if (turno is None):
            response_dict['status'] = 0
            response_dict['message'] = "Error, no existe turno"
            json = simplejson.dumps(response_dict)
            return json

        estado = Estado.objects.get(id=3)
        try:
            turno.estado = estado
            turno.save()
            response_dict['status'] = 1
            response_dict['message'] = "El turno se ha anulado correctamente."
            json = simplejson.dumps(response_dict)
            return json
        except Exception, err:
            return str(err)

    def reprogramar(self):
        request = self.request
        idTurno = request.GET['id-turno']
        response_dict = {}

        turno = Turno.objects.get(id=idTurno)
        if (turno is None):
            return self.getBuscarTurnos()

        estado = Estado.objects.get(id=3)
        try:
            turno.estado = estado
            turno.save()
            practicas = turno.practicas.all()
            arr = []
            for practica in practicas:
                arr.append(str(practica.id))
            kwargs = {'id-sala':turno.sala.id, 'id-paciente':turno.paciente.id, 'id-medico':turno.medico.id,
                      'id-obra-social':turno.obraSocial.id, 'id-practicas[]':arr }
            return self.getTurnosDisponibles(**kwargs)
        except Exception, err:
            return str(err)

    def confirmar(self):
        request = self.request
        idTurno = request.GET['id-turno']
        response_dict = {}

        turno = Turno.objects.get(id=idTurno)
        if turno is None:
            response_dict['status'] = 0
            response_dict['message'] = "Error, no existe turno"
            json = simplejson.dumps(response_dict)
            return json

        estado = Estado.objects.get(id=2)
        try:
            turno.estado = estado
            turno.save()
            response_dict['status'] = 1
            response_dict['message'] = "El turno se ha confirmado correctamente."
            json = simplejson.dumps(response_dict)
            return json
        except Exception, err:
            return str(err)

    def anunciar(self):
        request = self.request
        idTurno = request.GET['id-turno']
        response_dict = {}

        turno = Turno.objects.get(id=idTurno)
        if turno is None:
            response_dict['status'] = False
            response_dict['message'] = "Error, no existe turno"
            json = simplejson.dumps(response_dict)
            return json

        try:
            #      pacientes = []
            #      paciente = PacienteEstudio()
            #
            #      if (turno.paciente.dni != ""):
            #	pacientes = GetPacienteEstudio.objects.filter(dni=turno.paciente.dni)

            #      if (len(pacientes) == 0):
            #	paciente.dni = turno.paciente.dni
            #	paciente.nombre = turno.paciente.nombre #TODO: escape acentos y enies
            #	paciente.apellido = turno.paciente.apellido
            #	paciente.edad = int(turno.paciente.edad)
            #	paciente.domicilio = turno.paciente.domicilio
            #	paciente.telefono = turno.paciente.telefono
            #	paciente.sexo = turno.paciente.sexo
            #	paciente.nroAfiliado = ""
            #	paciente.save()
            #      else:
            #	paciente.id = pacientes[0].id

            practicas = turno.practicas.all()
            for practica in practicas:
                estudio = Estudio()
                estudio.paciente_id = turno.paciente.id
                estudio.practica_id = practica.id
                estudio.fechaEstudio = turno.fechaTurno
                estudio.motivoEstudio = ""
                estudio.informe = ""
                estudio.save()#TODO: gestionar error: si falla en algun save, ver si se puede hacer rollback, sino informar del error grave! porque se desconfiguran los id de estudio

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
                log.dateTime = datetime.datetime.now()
                log.observacion = 'creado desde turnos'
                log.save()

            response_dict['status'] = True
            response_dict['message'] = "Success"
            json = simplejson.dumps(response_dict)
            return json

        except Exception, err:
            response_dict['status'] = False
            response_dict['message'] = str(err)
            json = simplejson.dumps(response_dict)
            return json
