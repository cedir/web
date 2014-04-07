//Ponemos el validador del formulario de login

function checkUser(){

  var usr = document.getElementById("txtNomUsuario").value;
  var psw = document.getElementById("txtPassword").value;
  if (usr =="" || psw == ""){
      alert("Usuario y Password no pueden estar vacios.");  
  }
  else{
    document.form1.submit();
  }
  
  return;

}

//Detectamos la tecla presionada

document.onkeyup = keyPressed;      
document.onclick = clickHandler;

function keyPressed()
{
	alert("The document was keypressed!");	
  var KeyID = (window.event) ? event.keyCode : e.keyCode;

  if(window.event){ //IE
   KeyID = e.keyCode;
  }
  else
  { //Mozilla
    code = e.which;
  }
  
  
  if(KeyID == 13)
  {
    //Enter key pressed
    alert.("Ha presionado la tecla enter");
  }
  
}//fin keyPressed

function clickHandler()
{
	var s1 = document.button.toString();
	var s2 = "The document was clicked!";
	alert(s1);
}
