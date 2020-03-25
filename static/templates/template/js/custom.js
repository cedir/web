/* Theme Name: The Project - Responsive Website Template
 * Author:HtmlCoder
 * Author URI:http://www.htmlcoder.me
 * Author e-mail:htmlcoder.me@gmail.com
 * Version:1.3.0
 * Created:March 2015
 * License URI:http://support.wrapbootstrap.com/
 * File Description: Place here your custom scripts
 */

(function($){
	$(document).ready(function(){

		// Notify Plugin - The below code (until line 42) is used for demonstration purposes only
		//-----------------------------------------------
		if (($(".main-navigation.onclick").length>0) && !Modernizr.touch ){
			$.notify({
				// options
				message: 'The Dropdowns of the Main Menu, are now open with click on Parent Items. Click "Home" to checkout this behavior.'
			},{
				// settings
				type: 'info',
				delay: 10000,
				offset : {
					y: 150,
					x: 20
				}
			});
		};
		if (!($(".main-navigation.animated").length>0) && !Modernizr.touch && $(".main-navigation").length>0){
			$.notify({
				// options
				message: 'The animations of main menu are disabled.'
			},{
				// settings
				type: 'info',
				delay: 10000,
				offset : {
					y: 150,
					x: 20
				}
			}); // End Notify Plugin - The above code (from line 14) is used for demonstration purposes only

		};
	}); // End document ready

})(this.jQuery);

function ContactFormHandler(){
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	  if (this.readyState == 4 && this.status == 200) {
	   respuesta = JSON.parse(this.responseText)
	   if(respuesta['sent'] == 'no'){
		   document.getElementById("MessageNotSent2").classList.remove("hidden")
	   }else{
		   document.getElementById("MessageSent2").classList.remove("hidden")
		}
	  }
	};
	
	name = document.getElementById("name").value
	email = document.getElementById("email").value
	tel = document.getElementById("tel").value
	message = document.getElementById("message").value
	captcha = document.getElementById("g-recaptcha-response").value
	
	data = `name=${name}&email=${email}&tel=${tel}&message=${message}&g-recaptcha-response=${captcha}`
	
	
	xhttp.open("POST", "/sendMail/", true);
	xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhttp.send(data);
}