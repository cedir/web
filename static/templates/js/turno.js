/*
  Turnos

*/

//(function($) {

$(document).ready(function(){
	$("ul.topnav li a").hover(function() { //When trigger is clicked...
		$(this).parent().find("ul.subnav").slideDown('fast').show(); //Drop down the subnav on click

		$(this).parent().hover(function() {
		}, function(){
			$(this).parent().find("ul.subnav").slideUp('slow'); //When the mouse hovers out of the subnav, move it back up
		});
		}).hover(function() {
			$(this).addClass("subhover"); //On hover over, add class "subhover"
		}, function(){	//On Hover Out
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

  if (second=="") { second = null; }
  if (ampm=="") { ampm = null }

  if (hour < 0  || hour > 23) {
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
  if (minute<0 || minute > 59) {
    alert ("Los minutos deben ser entre 0 y 59.");
    return false;
  }
  if (second != null && (second < 0 || second > 59)) {
    alert ("Los segundos deben ser entre 0 y 59.");
    return false;
  }
  return true;
}


/*******************AJAX**************************/

function getNext() {
    var rand = Math.round(100*Math.random());
    var main = document.getElementById('lineasSector');
    var lastchild = main.lastElementChild;
    var inputObjs = lastchild.getElementsByTagName('input');
    var fecha = inputObjs[0].value;
    var sala = $("#id-sala").val();
    var medico = $("#id-medico").val();

    $.ajax({
      url: '/app/',
      data: "controlador=Turnos&accion=getNextDayLine&fecha=" + fecha + "&id-sala=" + sala + "&id-medico=" + medico + "&_nocache=" + rand,
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
     var rand = Math.round(100*Math.random());
    var main = document.getElementById('lineasSector');
    var firstchild = main.firstElementChild;
    var inputObjs = firstchild.getElementsByTagName('input');
    var fecha = inputObjs[0].value;
    var sala = $("#id-sala").val();
    var medico = $("#id-medico").val();

    $.ajax({
      url: '/app/',
      data: "controlador=Turnos&accion=getBackDayLine&fecha=" + fecha + "&id-sala=" + sala + "&id-medico=" + medico + "&_nocache=" + rand ,
      success: function(data) {
 	      var main = document.getElementById('lineasSector');
	      var child = main.lastElementChild;
	      main.removeChild(child);

	      var el = document.createElement('div');
	      el.innerHTML = data;
// 	      main.appendChild(el);

// 	      var main= document.getElementsByTagName('div')[0];
	        
	      main.insertBefore(el,main.firstChild);

      }
    });
}

function save() {
    var rand = Math.round(100*Math.random());
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
    for(var i = 0;i< arr.length; i++){if(arr[i] != 'null')strPracticas += "&id-practicas[]=" + arr[i];}


    if(!medico){
      alert("Debe seleccionarse un Medico antes de crear un turno.");
      return;
    }
    if(!obraSocial){
      alert("Debe seleccionarse una Obra Social antes de crear un turno.");
      return;
    }
    if(strPracticas == ""){
      alert("Debe seleccionarse al menos una Practica antes de crear un turno.");
      return;
    }
    if(idPaciente == ""){
      alert("Debe seleccionarse un Paciente antes de crear un turno.");
      return;
    }
    if (!isValidTime(hora_inicio)){
      return;
    }
    if (!isValidTime(hora_fin_estimada)){
      return;
    }

    $.ajax({
      url: '/app/',
      dataType: 'json',
      data: "controlador=Turnos&accion=guardar&hora_inicio=" + hora_inicio + "&hora_fin_estimada=" + hora_fin_estimada + "&fecha_turno=" + fecha + "&id-medico=" + medico + "&id-obra-social=" + obraSocial + "&id-sala=" + sala + "&id-paciente=" + idPaciente + strPracticas + "&observacion_turno=" + observacion +  "&_nocache=" + rand,
      success: function(data) {
	  if(data.status){
	    alert(data.message);
	    window.location.href = "/app/?controlador=Turnos&accion=getBuscarTurnos&fecha=" + fecha + "&id-sala=" + sala
	  }
	  else{
	    alert(data.message);
	  }

      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });
}

function getVerPlanilla(){
  var idSala = $("#id-sala").val();
  if(!idSala){
    alert("Debe seleccionar una sala para poder ver la planilla de turnos");
    return;
  }
  $("#ver-planilla").submit();
}

function getEdit(idTurno){
      $("#dialog").dialog({ width: 550 });

      $.ajax({
	url: '/app/',
	dataType: 'json',
	data: "controlador=Turnos&accion=getTurno&id=" + idTurno,
	success: function(data) {
	  $("#popup-paciente").text(data.paciente);
	  $("#popup-paciente").attr("href", "/app/?controlador=Pacientes&accion=getUpdate&id=" + data.paciente_id);
	  $("#popup-paciente-tel").text(data.tel);
	  $("#popup-paciente-dni").text(data.dni);
	  $("#popup-fecha").text(data.fecha);
	  $("#popup-medico").text(data.medico);
	  $("#popup-practicas").text(data.practicas);
	  $("#popup-sala").text(data.sala);
	  $("#popup-estado").text(data.estado);
	  $("#popup-hora-inicio").text(data.hora_inicio);
	  $("#popup-hora-fin").text(data.hora_fin);
	  $("#popup-fecha-otorgamiento").text(data.fecha_otorgamiento);
	  $("#popup-observacion_turno").text(data.observacion);
	  $("#popup-observacion_turno").val(data.observacion);
	  $("#current-turno-id").val(data.id);
	  $("#id-obra-social option[value='" + data.obra_social + "']").attr('selected', 'selected');
	  $("#popup-creado-por").text(data.creado_por);
	},
	error: function(response,err) {
	    alert("Error en el servidor: " + err);
	}

      });
}

function updateTurno() {
    var rand = Math.round(100*Math.random());
    var obraSocial = $("#id-obra-social").val();
    var idTurno = $("#current-turno-id").val();
    var observacion = $("#popup-observacion_turno").val();
    
    if(!obraSocial){
      alert("Debe seleccionarse una Obra Social antes de crear un turno.");
      return;
    }

    $.ajax({
      url: '/app/',
      dataType: 'json',
      data: "controlador=Turnos&accion=update&id-obra-social=" + obraSocial + "&id-turno=" + idTurno + "&observacion=" + observacion + "&id-estado=" + 1 + "&_nocache=" + rand,
      success: function(data) {
// 	  if(data.status){
	    alert(data.message);
		$("#frmBuscar").submit();
// 	  }

      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });
}

function confirmar(){
    var rand = Math.round(100*Math.random());
    var idTurno = $("#current-turno-id").val();
    if(!confirm('¿Seguro desea confirmar el turno?')){return;}
    $.ajax({
      url: '/app/',
      dataType: 'json',
      data: "controlador=Turnos&accion=confirmar&id-turno=" + idTurno + "&_nocache=" + rand,
      success: function(data) {
	   alert(data.message);
	   $('#frmBuscar').trigger('submit');
      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });
}
function anular(){
    var rand = Math.round(100*Math.random());
    var idTurno = $("#current-turno-id").val();
    if(!confirm('¿Seguro desea anular el turno?')){return;}
    $.ajax({
      url: '/app/',
      dataType: 'json',
      data: "controlador=Turnos&accion=anular&id-turno=" + idTurno + "&_nocache=" + rand,
      success: function(data) {
	   alert(data.message);
	   $('#frmBuscar').trigger('submit');
      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });
}
function reprogramar(){
    var idTurno = $("#current-turno-id").val();
    if(confirm('¿Seguro desea reprogramar el turno?')){
      window.location.href = "/app/?controlador=Turnos&accion=reprogramar&id-turno=" + idTurno;
    }
}
function anunciarTurno(){
    var rand = Math.round(100*Math.random());
    var idTurno = $("#current-turno-id").val();
    if(!confirm('¿Seguro desea anunciar el paciente?')){return;}
    $.ajax({
      url: '/turnos/anunciar/' + idTurno,
      dataType: 'json',
      data: "_nocache=" + rand,
      success: function(data) {
	  if (data.status){
	    alert("El paciente fue anunciado con exitosamente");
	  }
	  else{
	    alert("Se ha producido un error al crear el paciente y los estudios. Por favor revise en el sistema que esten los datos ingresados y vuelva a intentarlo. \n\n Error: " + data.message);
	  }
      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });
}


/*obtiene horario para el medico seleccionado en el combo y lo muestra*/
function getHorarioAtencionMedico() {
    var rand = Math.round(100*Math.random());
    var medicoId = $("#id-medico").val();

    if (!medicoId){
      $('#med-info').hide();
      return;
    }
    
    $.ajax({
      url: '/app/',
      dataType: 'json',
      data: "controlador=Root&accion=getDisponibilidadMedicosJson&id-medico=" + medicoId + "&_nocache=" + rand ,
      success: function(data) {
	      var medico = $("#id-medico option:selected").text();
	      $('#med-horario').html("<b>" + medico + "</b>" + data.horario);
	      $('#med-info').show();
      }
    });
}

function getInfoMedico() {
    var medicoId = $("#id-medico").val();
    var obraSocialId = $("#id-obra-social").val();

    if (!medicoId || !obraSocialId){
      $('#med-os-info').hide();
      return;
    }
    
    $.ajax({
      url: '/api/medico/infomedicos/',
      dataType: 'json',
      data: 'medico=' + medicoId + '&obra_social=' + obraSocialId,
      success: function(data) {
            $('#med-os-info ul').empty();
            for (var i = 0; i < data.length; i++) {
                $('#med-os-info ul').append("<li>" + data[i].texto + "</li>");
            };
            var nombreObraSocial = $("#id-obra-social option:selected").text();
            $('#infomed-obrasocial').html(nombreObraSocial);
            $('#med-os-info').show();
      }
    });
}

/********** PACIENTES **********/
function createPaciente(createTurno) {
    var rand = Math.round(100*Math.random());
    var nombre = $("#txtNombre").val();
    var apellido = $("#txtApellido").val();
    var dni = $("#txtDni").val();
    var telefono = $("#txtTelefono").val();
    var fechaNacimiento = $("#txtFechaNacimiento").val();
    var sexo = $("#txtSexo").val();
    var domicilio = $("#txtDomicilio").val();
	var nroAfiliado = $("#txtNroAfiliado").val();
	var email = $("#txtEmail").val();

    if(!nombre){
      alert("Error, el campo Nombre debe completarse.");
      return false;
    }
    if(!apellido){
      alert("Error, el campo Apellido debe completarse.");
      return false;
    }
    if(!telefono){
      alert("Error, el campo Telefono debe completarse.");
      return false;
    }

	if(!isEmail(email)){
		alert("Error, email no esta bien formado.");
		return false;
	}

    $.ajax({
      url: '/app/',
      dataType: 'json',
      type:'POST',
      data: "controlador=Pacientes&accion=crear&nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
		  "&telefono=" + telefono + "&fechaNacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
		  "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
      success: function(data) {
	  if(data.status){
	    alert(data.message);
	    if(createTurno){window.location.href = "/app/?controlador=Turnos&accion=getTurnosDisponibles&id-paciente=" + data.idPaciente;}
	    else{window.location.href = "/app/?controlador=Pacientes&accion=getBuscar&dni=" + dni;}
	  }
	  else{//error
	    alert(data.message);
	  }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
		alert("Error, puede que ya exista un paciente con DNI " + dni + ". Verifique que se trate del mismo paciente y vuelva a intentarlo" );
      }
    });
}
function createAndAsignPaciente(createTurno) {//TODO: aca llamar a createPaciente para no repetir codigo
    var rand = Math.round(100*Math.random());
    var nombre = $("#txtNombre").val();
    var apellido = $("#txtApellido").val();
    var dni = $("#txtDni").val();
    var telefono = $("#txtTelefono").val();
    var fechaNacimiento = $("#txtFechaNacimiento").val();
    var sexo = $("#txtSexo").val();
    var domicilio = $("#txtDomicilio").val();
	var nroAfiliado = $("#txtNroAfiliado").val();
	var email = $("#txtEmail").val();

    if(!nombre){
      alert("Error, el campo Nombre debe completarse.");
      return false;
    }
    if(!apellido){
      alert("Error, el campo Apellido debe completarse.");
      return false;
    }
    if(!telefono){
      alert("Error, el campo Telefono debe completarse.");
      return false;
    }

	if(!isEmail(email)){
		alert("Error, email no esta bien formado.");
		return false;
	}

    $.ajax({
      url: '/app/',
      dataType: 'json',
      type:'POST',
      data: "controlador=Pacientes&accion=crear&nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
		  "&telefono=" + telefono + "&fechaNacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
		  "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
      success: function(data) {
	if(data.status){
	  setPaciente(data.idPaciente,$("#txtNombre").val(),$("#txtApellido").val());
	  $('#formCrearPaciente').clearForm();
	}
	else{//error
	    alert(data.message);
	}
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
	  alert("Error, puede que ya exista un paciente con DNI " + dni + ". Verifique que se trate del mismo paciente y vuelva a intentarlo" );
      }
    });
}
function updatePaciente() {//TODO: aca llamar a createPaciente para no repetir codigo
    var rand = Math.round(100*Math.random());
    var id = $("#id").val();
    var nombre = $("#txtNombre").val();
    var apellido = $("#txtApellido").val();
    var dni = $("#txtDni").val();
    var telefono = $("#txtTelefono").val();
    var fechaNacimiento = $("#txtFechaNacimiento").val();
    var sexo = $("#txtSexo").val();
    var domicilio = $("#txtDomicilio").val();
	var nroAfiliado = $("#txtNroAfiliado").val();
	var email = $("#txtEmail").val();

    if(!nombre){
      alert("Error, el campo Nombre debe completarse.");
      return false;
    }
    if(!apellido){
      alert("Error, el campo Apellido debe completarse.");
      return false;
    }
    if(!telefono){
      alert("Error, el campo Telefono debe completarse.");
      return false;
    }

	if(!isEmail(email)){
		alert("Error, email no esta bien formado.");
		return false;
	}

    $.ajax({
      url: '/app/',
      dataType: 'json',
      type:'POST',
      data: "controlador=Pacientes&accion=update&id=" + id + "&nombre=" + nombre + "&apellido=" + apellido + "&dni=" + dni +
		  "&telefono=" + telefono + "&fechaNacimiento=" + fechaNacimiento + "&sexo=" + sexo + "&domicilio=" + domicilio +
		  "&email=" + email + "&nro_afiliado=" + nroAfiliado + "&_nocache=" + rand,
      success: function(data) {
	  if(data.status){
	    alert(data.message);
	    window.location.href = "/app/?controlador=Pacientes&accion=getBuscar&dni=" + dni;
	  }
	  else{//error
	    alert(data.message);
	  }
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
	  alert("Se ha producido un error al intentar guardar. Salga y vuelva a intentarlo, si el error persiste, informe al administrador.");
      }
    });
}

function buscarPacientes() {
    var rand = Math.round(100*Math.random());
    var apellido = $("#apellidoPacienteBuscar").val();
    var nombre = $("#nombrePacienteBuscar").val();
    var dni = $("#dniPacienteBuscar").val();

  $.get("/app/?controlador=Pacientes&accion=getBuscar&apellido=" + apellido + "&nombre=" + nombre + "&dni=" + dni + "&requestType=ajax" + "&_nocache=" + rand, function(data) {
    $('.result').html(data);
  });
}


/****************Horarios medicos***************/
function getCreateHorario(){
      $("#dialog").dialog({ width: 550 });
      $("#btnEliminar").hide();
      $("#btnGuardar").hide();
      $("#btnCrear").show();
      //set all to default
      $("#hora_desde").val('');
      $("#hora_hasta").val('');
      $("#current-disponibilidad-id").val('');
      $("#id-medico-horario option[value='']").attr('selected', 'selected');
      $("#id-sala option[value='']").attr('selected', 'selected');
      $("#id-dia option[value='']").attr('selected', 'selected');
}
function createHorario(){
    var rand = Math.round(100*Math.random());
    var hora_desde = $("#hora_desde").val();
    var hora_hasta = $("#hora_hasta").val();
    var medico = $("#id-medico-horario").val();
    var sala = $("#id-sala").val();
    var dia = $("#id-dia").val();

    if(!medico){
      alert("Debe seleccionarse un Medico.");
      return;
    }
    if(!sala){
      alert("Debe seleccionarse una Sala.");
      return;
    }
    if(!dia){
      alert("Debe seleccionarse un Dia.");
      return;
    }
    if (!isValidTime(hora_desde)){
      return;
    }
    if (!isValidTime(hora_hasta)){
      return;
    }

    $.ajax({
      url: '/app/',
      dataType: 'json',
      type:'POST',
      data: "controlador=Root&accion=crearDisponibilidad&hora_desde=" + hora_desde + "&hora_hasta=" + hora_hasta + "&id-medico=" + medico + "&id-dia=" + dia + "&id-sala=" + sala +  "&_nocache=" + rand,
      success: function(data) {
	  if(data.status){
	    alert(data.message);
	    $('#frmBuscar').trigger('submit');
	  }
	  else{
	    alert(data.message);
	  }

      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });

}
function getUpdateHorario(id){
      $("#dialog").dialog({ width: 550 });
      $("#btnCrear").hide();
      $("#btnEliminar").show();
      $("#btnGuardar").show();

      $.ajax({
	url: '/app/',
	dataType: 'json',
	data: "controlador=Root&accion=getDisponibilidad&id=" + id,
	success: function(data) {
	  $("#hora_desde").val(data.hora_inicio);
	  $("#hora_hasta").val(data.hora_fin);
	  $("#current-disponibilidad-id").val(data.id);
	  $("#id-medico-horario option[value='" + data.medico + "']").attr('selected', 'selected');
	  $("#id-sala option[value='" + data.sala + "']").attr('selected', 'selected');
	  $("#id-dia option[value='" + data.dia + "']").attr('selected', 'selected');
	},
	error: function(response,err) {
	    alert("Error en el servidor: " + err);
	}

      });
}
function updateHorario(){
    var rand = Math.round(100*Math.random());
    var hora_desde = $("#hora_desde").val();
    var hora_hasta = $("#hora_hasta").val();
    var medico = $("#id-medico-horario").val();
    var sala = $("#id-sala").val();
    var dia = $("#id-dia").val();
    var id = $("#current-disponibilidad-id").val();

    if(!medico){
      alert("Debe seleccionarse un Medico.");
      return;
    }
    if(!sala){
      alert("Debe seleccionarse una Sala.");
      return;
    }
    if(!dia){
      alert("Debe seleccionarse un Dia.");
      return;
    }
    if (!isValidTime(hora_desde)){
      return;
    }
    if (!isValidTime(hora_hasta)){
      return;
    }

    $.ajax({
      url: '/app/',
      dataType: 'json',
      type:'POST',
      data: "controlador=Root&accion=updateDisponibilidad&id=" + id + "&hora_desde=" + hora_desde + "&hora_hasta=" + hora_hasta + "&id-medico=" + medico + "&id-dia=" + dia + "&id-sala=" + sala +  "&_nocache=" + rand,
      success: function(data) {
	  if(data.status){
	    alert(data.message);
	    $('#frmBuscar').trigger('submit');
	  }
	  else{
	    alert(data.message);
	  }

      },
      error: function(response,err) {
	  alert("Error en el servidor: " + err);
      }
    });

}
function eliminarHorario(){
  if(!confirm('¿Seguro desea eliminar este horario?')){return;}
  var id = $("#current-disponibilidad-id").val();
  $.ajax({
    url: '/app/',
    dataType: 'json',
    type:'POST',
    data: "controlador=Root&accion=deleteDisponibilidad&id=" + id,
    success: function(data) {
	if(data.status){
	  alert(data.message);
	  $('#frmBuscar').trigger('submit');
	}
	else{
	  alert(data.message);
	}

    },
    error: function(response,err) {
	alert("Error en el servidor: " + err);
    }
  });
}


/*------------------Utils-------------------------*/

function isEmail(email) {
	// allow empty string as valid email
	if(email){
		var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
		return regex.test(email);
	}
	return true
}

//})(jQuery);

