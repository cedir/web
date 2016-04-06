# -*- coding: utf-8 -*-
from django.template import Template, Context, loader
from datetime import datetime
import simplejson


PIXELS_PER_MINUTE = 1.333


class ViewTurnos():
    def __init__(self, request=None):
        self.request = request

    def getTurnosDisponibles(self,**kwargs):
        dayLines = kwargs['dayLines']
        medicos = kwargs['medicos']
        paciente = kwargs['pacienteSeleccionado']
        idMedico = kwargs['idMedico']
        obraSociales = kwargs['obraSociales']
        idObraSocial = kwargs['idObraSocial']
        practicas = kwargs['practicas']
        idPracticas = kwargs['idPracticas']
        salas = kwargs['salas']
        idSala = kwargs['idSala']
        fecha = kwargs['fecha']

        strLines = None
        showLines = None

        arrMedicos = []
        for medico in medicos:
            hshMedico = {}
            hshMedico["id"] = medico.id
            hshMedico["nombre"] = medico.nombre
            hshMedico["apellido"] = medico.apellido
            if medico.id == int(idMedico):
              hshMedico["selected"] = 1
            arrMedicos.append(hshMedico)

        arrSalas = []
        for sala in salas:
            hshMedico = {}
            hshMedico["id"] = sala.id
            hshMedico["nombre"] = sala.nombre
            if sala.id == int(idSala):
              hshMedico["selected"] = 1
            arrSalas.append(hshMedico)

        arrObrasSociales = []
        for medico in obraSociales:
            hshMedico = {}
            hshMedico["id"] = medico.id
            hshMedico["nombre"] = medico.nombre
            if medico.id == int(idObraSocial):
              hshMedico["selected"] = 1
            arrObrasSociales.append(hshMedico)

        arrPracticas = []
        for practica in practicas:
            hshMedico = {}
            hshMedico["id"] = practica.id
            hshMedico["nombre"] = practica.descripcion
            if str(practica.id) in idPracticas:
              hshMedico["selected"] = 1
            arrPracticas.append(hshMedico)

        nombrePaciente = ""
        apellidoPaciente = ""
        idPaciente = ""
        if (paciente is None):
          pass
        else:
          nombrePaciente = paciente.nombre
          apellidoPaciente = paciente.apellido
          idPaciente = paciente.id

        if dayLines:
          showLines = True
          strLines = self.getDayLines(dayLines)

        c = Context({
          'dayLines':strLines,
          'nombrePaciente':nombrePaciente,
          'apellidoPaciente':apellidoPaciente,
          'idPaciente':idPaciente,
          'showLines':showLines,
          'medicos':arrMedicos,
          'obrasSociales':arrObrasSociales,
          'practicas':arrPracticas,
          'salas':arrSalas,
          'fecha':fecha,
          'logged_user_name':self.request.session["cedir_user_name"],
        })

        t = loader.get_template('turnos/buscarTurnosDisponibles.html')

        return t.render(c)

    def getDayLines(self, dayLines):
        strLines = None
        i = 0
        for dayLine in dayLines:
            i +=1

            turnos = dayLine["turnos"]
            arrHshTurnos = []
            for turno in turnos:
                hshTurno = {}
                hshTurno["id"] = turno.id
                hshTurno["paciente"] = turno.paciente.nombre + ' ' + turno.paciente.apellido
                hshTurno["top"] = (((turno.horaInicio.hour - 7) * 60) + turno.horaInicio.minute) * PIXELS_PER_MINUTE + 11
                hshTurno["fecha"] = turno.fechaTurno
                hshTurno["hora"] = turno.horaInicio
                hshTurno["duracion"] = turno.getDuracionEnMinutos()
                hshTurno["duracionEnPixeles"] = turno.getDuracionEnMinutos() * PIXELS_PER_MINUTE - (1 * PIXELS_PER_MINUTE)
                hshTurno["medico"] = turno.medico.nombre + ' ' + turno.medico.apellido
                hshTurno["obra_social"] = turno.obraSocial.nombre
                hshTurno["practicas"] = u'-'.join([p.abreviatura for p in turno.practicas.all()])
                arrHshTurnos.append(hshTurno)

            disponibilidades = dayLine["disponibilidad"]
            arrHshDisponibilidad = []
            colors = ('#71FF86', '#fffccc', '#A6C4FF')
            index = 0
            for disp in disponibilidades:
                row = {}
                row["id"] = disp.id
                row["top"] = (((disp.horaInicio.hour - 7) * 60) + disp.horaInicio.minute) * 1.333 + 9
                row["fecha"] = disp.fecha
                row["hora"] = disp.horaInicio
                row["duracionEnPixeles"] = disp.getDuracionEnMinutos() * 1.333
                medicoChars = list(disp.medico.apellido)
                strMedico = ''
                for char in medicoChars:
                    strMedico += char + " "
                row["medico"] = strMedico
                row["color"] = colors[index]
                row["sala"] = disp.sala.nombre
                index += 1
                if index == 3:
                    index = 0

                arrHshDisponibilidad.append(row)

            dayLineTemplate = loader.get_template('turnos/dayLine.html')
            dayLineContext = Context({'lineDay': dayLine["dia"], 'fechaTurno':dayLine["fecha"],
                                      'turnos': arrHshTurnos, 'disponibilidades':arrHshDisponibilidad})
            if strLines:
                strLines = strLines + dayLineTemplate.render(dayLineContext)
            else:
                strLines = dayLineTemplate.render(dayLineContext)
        return strLines

    def getBuscarTurnos(self,**kwargs):
        turnos = kwargs['turnos']
        fecha = kwargs['fecha']
        idMedico = kwargs['idMedico']
        medicos = kwargs['medicos']
        obraSociales = kwargs['obraSociales']
        salas = kwargs['salas']
        idSala = kwargs['idSala']
        paciente = kwargs['paciente']
        ocultarAnulados = kwargs['ocultarAnulados']

        arrHshTurnos = []
        for turno in turnos:
            hshTurno = {}
            hshTurno["id"] = turno.id
            hshTurno["nombre"] = turno.paciente.nombre
            hshTurno["apellido"] = turno.paciente.apellido
            hshTurno["id_paciente"] = turno.paciente.id
            hshTurno["fecha"] = self._sqlDateToNormalDate(turno.fechaTurno)
            hshTurno["hora_inicio"] = turno.horaInicio
            hshTurno["medico"] = turno.medico.apellido + ", " + turno.medico.nombre
            hshTurno["obra_social"] = turno.obraSocial.nombre
            hshTurno["observacion"] = turno.observacion
            hshTurno["img_estado"] = turno.estado.img

            practicasDelTurno = ""
            for practica in turno.practicas.all():
                if practica.abreviatura is None or practica.abreviatura == "":
                    practicasDelTurno += practica.descripcion + " - "
                else:
                    practicasDelTurno += practica.abreviatura + " - "

            practicasDelTurno = practicasDelTurno[:-2]
            hshTurno["practica"] =  practicasDelTurno
            arrHshTurnos.append(hshTurno)

        arrMedicos = []
        for medico in medicos:
            hshMedico = {}
            hshMedico["id"] = medico.id
            hshMedico["nombre"] = medico.nombre
            hshMedico["apellido"] = medico.apellido
            if medico.id == int(idMedico):
              hshMedico["selected"] = 1
            arrMedicos.append(hshMedico)


        arrSalas = []
        for sala in salas:
            hshMedico = {}
            hshMedico["id"] = sala.id
            hshMedico["nombre"] = sala.nombre
            if sala.id == int(idSala):
              hshMedico["selected"] = 1
            arrSalas.append(hshMedico)

        arrObrasSociales = []
        for medico in obraSociales:
            hshMedico = {}
            hshMedico["id"] = medico.id
            hshMedico["nombre"] = medico.nombre
            arrObrasSociales.append(hshMedico)

        ocultarAnuladosState = ''
        if ocultarAnulados == 'true':
          ocultarAnuladosState = 'checked'

        c = Context({
          'turnos':arrHshTurnos,
          'medicos':arrMedicos,
          'fecha':self._sqlDateToNormalDate(fecha),
          'obrasSociales':arrObrasSociales,
          'salas':arrSalas,
          'paciente':paciente,
          'ocultarAnuladosState':ocultarAnuladosState,
          'logged_user_name':self.request.session["cedir_user_name"],
        })

        t = loader.get_template('turnos/buscarTurnos.html')

        return t.render(c)

    def getTurno(self,**kwargs):
        turno = kwargs['turno']
        createdUser = kwargs['createdUser'] or '-no disponible-'
        response_dict = {}
        response_dict['id'] = turno.id
        response_dict['fecha'] = self._sqlDateToNormalDate(turno.fechaTurno)
        response_dict["paciente"] = turno.paciente.apellido + ", " + turno.paciente.nombre
        response_dict["tel"] = turno.paciente.telefono
        response_dict["dni"] = turno.paciente.dni
        response_dict["paciente_id"] = turno.paciente.id
        response_dict["hora_inicio"] = str(turno.horaInicio)
        response_dict["hora_fin_real"] = str(turno.horaFinReal)
        response_dict["hora_fin"] = str(turno.horaFinEstimada)
        response_dict["observacion"] = turno.observacion
        response_dict["fecha_otorgamiento"] = self._sqlDateToNormalDate(turno.fecha_otorgamiento)
        response_dict["medico"] = turno.medico.apellido + ", " + turno.medico.nombre
        response_dict["obra_social"] =  turno.obraSocial.id
        response_dict["obra_social_nombre"] =  turno.obraSocial.nombre
        response_dict["sala"] =  turno.sala.nombre
        response_dict["estado"] =  turno.estado.descripcion
        response_dict["creado_por"] =  createdUser
        #response_dict["anulado_por"] =
        #response_dict["observacion_anulacion"] =

        practicas = turno.practicas.all()
        strPracticas = ""
        for practica in practicas:
            strPracticas += practica.descripcion + ' - '

        response_dict["practicas"] =  strPracticas

        json = simplejson.dumps(response_dict)
        return json

    def _sqlDateToNormalDate(self,dateTime):
        if str(dateTime) == "":
            return ""
        try:
            arr = str(dateTime).split(" ")
            arr2 = arr[0].split("-")
            time = ""
            if (len(arr) > 1):
                time = arr[1]
            return arr2[2] + "/" + arr2[1] + "/" + arr2[0] + " " + time
        except Exception, err:
            return str(dateTime)
