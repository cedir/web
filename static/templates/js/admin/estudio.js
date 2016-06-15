
if (!$) {
    $ = django.jQuery;
}

$(document).ready(function() {
    CONSULTA = 20;
    
    if ($("form").attr("id") === "estudio_form"){  /* es la forma de saber que estamos en la vista "change estudio" y no en el listado*/
 
        var r1 = $('<input type="button" value="new button" id="infrome_20" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(r1);

        var r1 = $('<input type="button" value="Imprimir" id="print_estudio" />');
        $(".submit-row").append(r1);
        
        $("#print_estudio").click(function() {
            currentUrl = window.location.href;
            estudioId = currentUrl.split("/")[6];
            printUrl = "/estudio/imprimir/" + estudioId;
            var win = window.open(printUrl, '_blank');
            if (win) {
                //Browser has allowed it to be opened
                win.focus();
            } else {
                //Browser has blocked it
                alert('Please allow popups for this website');
            }
        });
        

        $("#id_practica").change(function() {
            practica_id = $("#id_practica option:selected").val();
            $(".admin-informe-buttons").css("display", "none");
            if (practica_id == CONSULTA){
                $("#infrome_20").css("display", "block");
            }
        });


        $("#infrome_20").click(function() {load_informe("asdasdasda");});

    }

    

    
    function load_informe(text){
        $("#id_informe").text(text);
    }
    
});

