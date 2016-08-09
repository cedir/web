/*
  Turnos

*/

//(function($) {
$(document).ready(function() {
  $("ul.topnav li a").hover(function() { //When trigger is clicked...
      $(this).parent().find("ul.subnav").slideDown('fast').show(); //Drop down the subnav on click
      $(this).parent().hover(function() {}, function() {
        $(this).parent().find("ul.subnav").slideUp('slow'); //When the mouse hovers out of the subnav, move it back up
      });
  }).hover(function() {
    $(this).addClass("subhover"); //On hover over, add class "subhover"
  }, function() { //On Hover Out
    $(this).removeClass("subhover"); //On hover out, remove class "subhover"
  });
});

function isValidTime(timeStr) {
  // Checks if time is in HH:MM:SS AM/PM format.
  // The seconds and AM/PM are optional.

  var timePat = /^(\d{1,2}):(\d{2})(:(\d{2}))?(\s?(AM|am|PM|pm))?$/;

  var matchArray = timeStr.match(timePat);
  if (matchArray == null) {
    alert("La hora no esta en un formato correcto.");
    return false;
  }
  hour = matchArray[1];
  minute = matchArray[2];
  second = matchArray[4];
  ampm = matchArray[6];

  if (second == "") {
    second = null;
  }
  if (ampm == "") {
    ampm = null
  }

  if (hour < 0 || hour > 23) {
    alert("La hora debe ser entre 1 y 23");
    return false;
  }
  //   if (hour <= 12 && ampm == null) {
  //     if (confirm("Please indicate which time format you are using.  OK = Standard Time, CANCEL = Military Time")) {
  //       alert("You must specify AM or PM.");
  //       return false;
  //     }
  //   }
  //   if  (hour > 12 && ampm != null) {
  //     alert("You can't specify AM or PM for military time.");
  //     return false;
  //   }
  if (minute < 0 || minute > 59) {
    alert("Los minutos deben ser entre 0 y 59.");
    return false;
  }
  if (second != null && (second < 0 || second > 59)) {
    alert("Los segundos deben ser entre 0 y 59.");
    return false;
  }
  return true;
}


/*******************AJAX**************************/

function getNext() {
  var rand = Math.round(100 * Math.random());
  var main = document.getElementById('lineasSector');
  var lastchild = main.lastElementChild;
  var inputObjs = lastchild.getElementsByTagName('input');
  var fecha = inputObjs[0].value;
  var sala = $("#id-sala").val();
  var medico = $("#id-medico").val();

  $.ajax({
    url: '/turnos/nextday/',
    data: "fecha=" + fecha + "&id-sala=" + sala + "&id-medico=" + medico + "&_nocache=" + rand,
    success: function(data) {
      // 	$('#lineasSector').html(data);
      var main = document.getElementById('lineasSector');
      var child = main.firstElementChild;
      main.removeChild(child);

      var el = document.createElement('div');
      el.innerHTML = data;
      main.appendChild(el);

    }
  });
}

function getBack() {
  var rand = Math.round(100 * Math.random());
  var main = document.getElementById('lineasSector');
  var firstchild = main.firstElementChild;
  var inputObjs = firstchild.getElementsByTagName('input');
  var fecha = inputObjs[0].value;
  var sala = $("#id-sala").val();
  var medico = $("#id-medico").val();

  $.ajax({
    url: '/turnos/backday/',
    data: "fecha=" + fecha + "&id-sala=" + sala + "&id-medico=" + medico + "&_nocache=" + rand,
    success: function(data) {
      var main = document.getElementById('lineasSector');
      var child = main.lastElementChild;
      main.removeChild(child);

      var el = document.createElement('div');
      el.innerHTML = data;
      // 	      main.appendChild(el);

      // 	      var main= document.getElementsByTagName('div')[0];

      main.insertBefore(el, main.firstChild);

    }
  });
}

function save() {
  var rand = Math.round(100 * Math.random());
  var hora_inicio = $("#hora_inicio").val();
  var hora_fin_estimada = $("#hora_fin_estimada").val();
  var fecha = $("#selected-fecha-value").val();
  var medico = $("#id-medico").val();
  var obraSocial = $("#id-obra-social").val();
  var sala = $("#id-sala").val();
  var idPaciente = $("#id-paciente").val();
  var idPracticas = $("#id-practicas").val();
  var observacion = $("#observacion").val();

  var arr = String(idPracticas).split(",");
  var strPracticas = "";
  for (var i = 0; i < arr.length; i++) {
    if (arr[i] != 'null') strPracticas += "&id-practicas[]=" + arr[i];
  }


  if (!medico) {
    alert("Debe seleccionarse un Medico antes de crear un turno.");
    return;
  }
  if (!obraSocial) {
    alert("Debe seleccionarse una Obra Social antes de crear un turno.");
    return;
  }
  if (strPracticas == "") {
    alert("Debe seleccionarse al menos una Practica antes de crear un turno.");
    return;
  }
  if (idPaciente == "") {
    alert("Debe seleccionarse un Paciente antes de crear un turno.");
    return;
  }
  if (!isValidTime(hora_inicio)) {
    return;
  }
  if (!isValidTime(hora_fin_estimada)) {
    return;
  }

  $.ajax({
    url: '/turnos/guardar/',
    dataType: 'json',
    data: "hora_inicio=" + hora_inicio + "&hora_fin_estimada=" + hora_fin_estimada + "&fecha_turno=" + fecha + "&id-medico=" + medico + "&id-obra-social=" + obraSocial + "&id-sala=" + sala + "&id-paciente=" + idPaciente + strPracticas + "&observacion_turno=" + observacion + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        window.location.href = "/turnos/buscar/?fecha=" + fecha + "&id-sala=" + sala
      } else {
        alert(data.message);
      }

    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}

function getVerPlanilla() {
  var idSala = $("#id-sala").val();
  if (!idSala) {
    alert("Debe seleccionar una sala para poder ver la planilla de turnos");
    return;
  }
  $("#ver-planilla").submit();
}

function getConfirmarTurno(event) {
  var button = $(event.relatedTarget);
  var fecha = button.data('fecha');
  var horaInicio = button.data('hora');

  var modal = $(this)

  modal.find("#selected-medico").text($("#id-medico option:selected").text());
  modal.find("#selected-obrasocial").text($("#id-obra-social option:selected").text());
  modal.find("#selected-practicas").text($("#id-practicas option:selected").text());
  modal.find("#selected-fecha").text(fecha);
  modal.find("#selected-fecha-value").val(fecha);
  modal.find("#hora_inicio").val(horaInicio);
  modal.find("#selected-sala").text($("#id-sala option:selected").text());

}


function setPaciente(id, nombre, apellido) {
  $('#selectedPaciente').html(apellido + ", " + nombre);
  $("#id-paciente").val(id);
  $("#dialogPaciente").modal("hide");
}


function getEdit(event) {
  var button = $(event.relatedTarget);
  var idTurno = button.data('turno-id');
  var modal = $(this)

  $.ajax({
    url: '/turnos/' + idTurno + '/',
    dataType: 'json',
    success: function(data) {
      modal.find("#popup-paciente")
           .text(data.paciente)
           .attr("href", "/paciente/" + data.paciente_id + "/editar/");

      modal.find("#popup-paciente-tel").text(data.tel);
      modal.find("#popup-paciente-dni").text(data.dni);
      modal.find("#popup-fecha").text(data.fecha);
      modal.find("#popup-medico").text(data.medico);
      modal.find("#popup-practicas").text(data.practicas);
      modal.find("#popup-sala").text(data.sala);
      modal.find("#popup-estado").text(data.estado);
      modal.find("#popup-hora-inicio").text(data.hora_inicio);
      modal.find("#popup-hora-fin").text(data.hora_fin);
      modal.find("#popup-fecha-otorgamiento").text(data.fecha_otorgamiento);
      modal.find("#popup-observacion_turno")
           .text(data.observacion)
           .val(data.observacion);
      modal.find("#current-turno-id").val(data.id);
      modal.find("#id-obra-social").val(data.obra_social);
      modal.find("#id-obra-social").trigger("chosen:updated");
      modal.find("#popup-creado-por").text(data.creado_por);
    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}

function updateTurno() {
  var rand = Math.round(100 * Math.random());
  var obraSocial = $("#id-obra-social").val();
  var idTurno = $("#current-turno-id").val();
  var observacion = $("#popup-observacion_turno").val();

  if (!obraSocial) {
    alert("Debe seleccionarse una Obra Social antes de crear un turno.");
    return;
  }

  $.ajax({
    url: '/turnos/' + idTurno + '/actualizar/',
    dataType: 'json',
    data: "id-obra-social=" + obraSocial + "&observacion=" + observacion + "&id-estado=" + 1 + "&_nocache=" + rand,
    success: function(data) {
      alert(data.message);
      $("#frmBuscar").submit();
    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}

function confirmar() {
  var rand = Math.round(100 * Math.random());
  var idTurno = $("#current-turno-id").val();
  if (!confirm('¿Seguro desea confirmar el turno?')) {
    return;
  }
  $.ajax({
    url: '/turnos/' +idTurno + '/confirmar/',
    dataType: 'json',
    data: "&_nocache=" + rand,
    success: function(data) {
      alert(data.message);
      $('#frmBuscar').trigger('submit');
    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}

function anular() {
  var rand = Math.round(100 * Math.random());
  var idTurno = $("#current-turno-id").val();
  if (!confirm('¿Seguro desea anular el turno?')) {
    return;
  }
  $.ajax({
    url: '/turnos/' + idTurno + '/anular/',
    dataType: 'json',
    data: "&_nocache=" + rand,
    success: function(data) {
      alert(data.message);
      $('#frmBuscar').trigger('submit');
    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}

function reprogramar() {
  var idTurno = $("#current-turno-id").val();
  if (confirm('¿Seguro desea reprogramar el turno?')) {
    window.location.href = "/turnos/" + idTurno + "/reprogramar/";
  }
}

function anunciarTurno() {
  var rand = Math.round(100 * Math.random());
  var idTurno = $("#current-turno-id").val();
  if (!confirm('¿Seguro desea anunciar el paciente?')) {
    return;
  }
  $.ajax({
    url: '/turnos/' + idTurno + '/anunciar/',
    dataType: 'json',
    data: "_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert("El paciente fue anunciado exitosamente");
      } else {
        alert("Se ha producido un error al crear el paciente y los estudios. Por favor revise en el sistema que esten los datos ingresados y vuelva a intentarlo. \n\n Error: " + data.message);
      }
    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}


/*obtiene horario para el medico seleccionado en el combo y lo muestra*/
function getHorarioAtencionMedico() {
  var rand = Math.round(100 * Math.random());
  var medicoId = $("#id-medico").val();

  if (!medicoId) {
    $('#med-info').hide();
    return;
  }

  $.ajax({
    url: '/app/',
    dataType: 'json',
    data: "/medicos/disponibilidad/json/?id-medico=" + medicoId + "&_nocache=" + rand,
    success: function(data) {
      var medico = $("#id-medico option:selected").text();
      $('#med-horario').html("<b>" + medico + "</b>" + data.horario);
      $('#med-info').show();
    }
  });
}

function getInfoTurno() {
    var medicoId = $("#id-medico").val();
    var obraSocialId = $("#id-obra-social").val();
    var idPracticas = $("#id-practicas").val();

    if (!medicoId && !obraSocialId && !idPracticas){
        $('#info-turno').hide();
        return;
    }

    if (idPracticas === null){
        idPracticas = "";
    }
    
    $.ajax({
      url: '/api/turno/infoturno/',
      dataType: 'json',
      data: 'medico=' + medicoId + '&obras_sociales=' + obraSocialId + "&practicas=" + idPracticas,
      success: function(data) {
            $('#info-turno tbody tr').remove();
            $.each(data, function(index, infoTurno) {
                var info_turno_practicas = '';
                $.each(infoTurno.practicas, function(index, practica) {
                    info_turno_practicas += ' -' + (practica.abreviatura? practica.abreviatura : practica.descripcion);
                });
                if (!info_turno_practicas){
                    info_turno_practicas = 'Todas';
                }

                $('#info-turno table tbody').append("<tr><td>" + infoTurno.texto + '</td><td>' + info_turno_practicas + "</td></tr>");
            });
            if (data.length) {
              $('#info-turno').show();
            }else{
              $('#info-turno').hide();
            }
      }
    });
}

/********** PACIENTES **********/
function createPaciente(createTurno) {
  var rand = Math.round(100 * Math.random());
  var nombre = $("#txtNombre").val();
  var apellido = $("#txtApellido").val();
  var dni = $("#txtDni").val();
  var telefono = $("#txtTelefono").val();
  var fechaNacimiento = $("#txtFechaNacimiento").val();
  var sexo = $("#txtSexo").val();
  var domicilio = $("#txtDomicilio").val();
  var nroAfiliado = $("#txtNroAfiliado").val();
  var email = $("#txtEmail").val();

  if (!nombre) {
    alert("Error, el campo Nombre debe completarse.");
    return false;
  }
  if (!apellido) {
    alert("Error, el campo Apellido debe completarse.");
    return false;
  }
  if (!telefono) {
    alert("Error, el campo Telefono debe completarse.");
    return false;
  }

  if (!isEmail(email)) {
    alert("Error, email no esta bien formado.");
    return false;
  }

  $.ajax({
    url: '/paciente/nuevo/',
    dataType: 'json',
    type: 'POST',
    data: "nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
      "&telefono=" + telefono + "&fechaNacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
      "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        if (createTurno) {
          window.location.href = "/turnos/disponibles/?id-paciente=" + data.idPaciente;
        } else {
          window.location.href = "/paciente/buscar/?dni=" + dni;
        }
      } else { //error
        alert(data.message);
      }
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Error, puede que ya exista un paciente con DNI " + dni + ". Verifique que se trate del mismo paciente y vuelva a intentarlo");
    }
  });
}

function createAndAsignPaciente(createTurno) { //TODO: aca llamar a createPaciente para no repetir codigo
  var rand = Math.round(100 * Math.random());
  var nombre = $("#txtNombre").val();
  var apellido = $("#txtApellido").val();
  var dni = $("#txtDni").val();
  var telefono = $("#txtTelefono").val();
  var fechaNacimiento = $("#txtFechaNacimiento").val();
  var sexo = $("#txtSexo").val();
  var domicilio = $("#txtDomicilio").val();
  var nroAfiliado = $("#txtNroAfiliado").val();
  var email = $("#txtEmail").val();

  if (!nombre) {
    alert("Error, el campo Nombre debe completarse.");
    return false;
  }
  if (!apellido) {
    alert("Error, el campo Apellido debe completarse.");
    return false;
  }
  if (!telefono) {
    alert("Error, el campo Telefono debe completarse.");
    return false;
  }

  if (!isEmail(email)) {
    alert("Error, email no esta bien formado.");
    return false;
  }

  $.ajax({
    url: '/paciente/nuevo/',
    dataType: 'json',
    type: 'POST',
    data: "nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
      "&telefono=" + telefono + "&fechaNacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
      "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        setPaciente(data.idPaciente, $("#txtNombre").val(), $("#txtApellido").val());
        $('#formCrearPaciente').clearForm();
      } else { //error
        alert(data.message);
      }
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Error, puede que ya exista un paciente con DNI " + dni + ". Verifique que se trate del mismo paciente y vuelva a intentarlo");
    }
  });
}

function updatePaciente() { //TODO: aca llamar a createPaciente para no repetir codigo
  var rand = Math.round(100 * Math.random());
  var form = $("#form1");
  var nombre = $("#txtNombre").val();
  var apellido = $("#txtApellido").val();
  var dni = $("#txtDni").val();
  var telefono = $("#txtTelefono").val();
  var fechaNacimiento = $("#txtFechaNacimiento").val();
  var sexo = $("#txtSexo").val();
  var domicilio = $("#txtDomicilio").val();
  var nroAfiliado = $("#txtNroAfiliado").val();
  var email = $("#txtEmail").val();

  if (!nombre) {
    alert("Error, el campo Nombre debe completarse.");
    return false;
  }
  if (!apellido) {
    alert("Error, el campo Apellido debe completarse.");
    return false;
  }
  if (!telefono) {
    alert("Error, el campo Telefono debe completarse.");
    return false;
  }

  if (!isEmail(email)) {
    alert("Error, email no esta bien formado.");
    return false;
  }

  $.ajax({
    url: form.attr('action'),
    dataType: 'json',
    type: 'POST',
    data: "nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
      "&telefono=" + telefono + "&fecha_nacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
      "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        window.location.href = "/paciente/buscar/?dni=" + dni;
      } else { //error
        alert(data.message);
      }
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Se ha producido un error al intentar guardar. Salga y vuelva a intentarlo, si el error persiste, informe al administrador.");
    }
  });
}

function buscarPacientes() {
  var rand = Math.round(100 * Math.random());
  var apellido = $("#apellidoPacienteBuscar").val();
  var nombre = $("#nombrePacienteBuscar").val();
  var dni = $("#dniPacienteBuscar").val();

  $.get("/paciente/buscar/?apellido=" + apellido + "&nombre=" + nombre + "&dni=" + dni + "&request_type=ajax" + "&_nocache=" + rand, function(data) {
    $('.result').html(data);
  });
}


function createHorario() {
  var rand = Math.round(100 * Math.random());
  var hora_desde = $("#hora_desde").val();
  var hora_hasta = $("#hora_hasta").val();
  var medico = $("#id-medico-horario").val();
  var sala = $("#id-sala").val();
  var dia = $("#id-dia").val();

  if (!medico) {
    alert("Debe seleccionarse un Medico.");
    return;
  }
  if (!sala) {
    alert("Debe seleccionarse una Sala.");
    return;
  }
  if (!dia) {
    alert("Debe seleccionarse un Dia.");
    return;
  }
  if (!isValidTime(hora_desde)) {
    return;
  }
  if (!isValidTime(hora_hasta)) {
    return;
  }

  $.ajax({
    url: '/disponibilidad/',
    dataType: 'json',
    type: 'POST',
    data: "hora_desde=" + hora_desde + "&hora_hasta=" + hora_hasta + "&id-medico=" + medico + "&id-dia=" + dia + "&id-sala=" + sala + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        $('#frmBuscar').trigger('submit');
      } else {
        alert(data.message);
      }

    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });

}

/****************Horarios medicos***************/
function getCreateHorario(event) {
  var button = $(event.relatedTarget);
  var modal = $(this)

  $("#btnEliminar").hide();
  $("#btnGuardar").hide();
  $("#btnCrear").show();
  //set all to default
  modal.find("#hora_desde").val('');
  modal.find("#hora_hasta").val('');
  modal.find("#current-disponibilidad-id").val('');

  modal.find("#id-medico-horario option[value='']").attr('selected', 'selected');
  modal.find("#id-sala option[value='']").attr('selected', 'selected');
  modal.find("#id-dia option[value='']").attr('selected', 'selected');

  modal.find("#id-medico-horario").trigger("chosen:updated");
  modal.find("#id-sala").trigger("chosen:updated");
  modal.find("#id-dia").trigger("chosen:updated");
}

function getUpdateHorario(event) {
  var button = $(event.relatedTarget);
  var id = button.data('horario');

  var modal = $(this)

  $("#btnCrear").hide();
  $("#btnEliminar").show();
  $("#btnGuardar").show();

  $.ajax({
    url: '/disponibilidad/',
    dataType: 'json',
    data: "id=" + id,
    success: function(data) {
      modal.find("#hora_desde").val(data.hora_inicio);
      modal.find("#hora_hasta").val(data.hora_fin);
      modal.find("#current-disponibilidad-id").val(data.id);
      modal.find("#id-medico-horario option[value='" + data.medico + "']").attr('selected', 'selected');
      modal.find("#id-sala option[value='" + data.sala + "']").attr('selected', 'selected');
      modal.find("#id-dia option[value='" + data.dia + "']").attr('selected', 'selected');

      modal.find("#id-medico-horario").trigger("chosen:updated");
      modal.find("#id-sala").trigger("chosen:updated");
      modal.find("#id-dia").trigger("chosen:updated");

    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }

  });
}

function updateHorario() {
  var rand = Math.round(100 * Math.random());
  var hora_desde = $("#hora_desde").val();
  var hora_hasta = $("#hora_hasta").val();
  var medico = $("#id-medico-horario").val();
  var sala = $("#id-sala").val();
  var dia = $("#id-dia").val();
  var id = $("#current-disponibilidad-id").val();

  if (!medico) {
    alert("Debe seleccionarse un Medico.");
    return;
  }
  if (!sala) {
    alert("Debe seleccionarse una Sala.");
    return;
  }
  if (!dia) {
    alert("Debe seleccionarse un Dia.");
    return;
  }
  if (!isValidTime(hora_desde)) {
    return;
  }
  if (!isValidTime(hora_hasta)) {
    return;
  }

  $.ajax({
    url: '/disponibilidad/actualizar/',
    dataType: 'json',
    type: 'POST',
    data: "id=" + id + "&hora_desde=" + hora_desde + "&hora_hasta=" + hora_hasta + "&id-medico=" + medico + "&id-dia=" + dia + "&id-sala=" + sala + "&_nocache=" + rand,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        $('#frmBuscar').trigger('submit');
      } else {
        alert(data.message);
      }

    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });

}

function eliminarHorario() {
  if (!confirm('¿Seguro desea eliminar este horario?')) {
    return;
  }
  var id = $("#current-disponibilidad-id").val();
  $.ajax({
    url: '/disponibilidad/eliminar/',
    dataType: 'json',
    type: 'POST',
    data: "id=" + id,
    success: function(data) {
      if (data.status) {
        alert(data.message);
        $('#frmBuscar').trigger('submit');
      } else {
        alert(data.message);
      }

    },
    error: function(response, err) {
      alert("Error en el servidor: " + err);
    }
  });
}


/*------------------Utils-------------------------*/

function isEmail(email) {
  // allow empty string as valid email
  if (email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
  }
  return true
}

//})(jQuery);

