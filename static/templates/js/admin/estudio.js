
if (!$) {
    $ = django.jQuery;
}

$(document).ready(function() {

    var estudioFueModificado = false;

    if ($("form").attr("id") === "estudio_form"){  /* es la forma de saber que estamos en la vista "change estudio" y no en el listado*/
        cargarVistaChangeEstudio();

        practicaChangeHandler();

        /* values have changed events*/
        $("#id_informe").on('input', function() { estudioFueModificado = true;});
        $("#id_motivoEstudio").on('input', function() { estudioFueModificado = true;});
    }

    function cargarVistaChangeEstudio(){

        /* Crear botones de informes*/
        var altaNormalButton = $('<input type="button" value="Alta Normal" id="altaNormalButton" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(altaNormalButton);
        $("#altaNormalButton").click(function() {load_informe(ALTA_NORMAL);});

        var gastritisButton = $('<input type="button" value="Gastritis" id="gastritisButton" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(gastritisButton);
        $("#gastritisButton").click(function() {load_informe(GASTRITIS);});

        var colonoNormalButton = $('<input type="button" value="Colono Normal" id="colonoNormalButton" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(colonoNormalButton);
        $("#colonoNormalButton").click(function() {load_informe(COLONO_NORMAL);});

        var colangioNormalButton = $('<input type="button" value="Colangio Normal" id="colangioNormalButton" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(colangioNormalButton);
        $("#colangioNormalButton").click(function() {load_informe(COLANGIO_NORMAL);});

        var colangioConCalculoButton = $('<input type="button" value="Colangio Con Calclulo" id="colangioConCalculoButton" class="admin-informe-buttons" style="display:none;"/>');
        $(".field-informe").append(colangioConCalculoButton);
        $("#colangioConCalculoButton").click(function() {load_informe(COLANGIO_CON_CALCULO);});

        function load_informe(text){
            $("#id_informe").text(text);
        }


        /* Boton Imprimir */
        var printButton = $('<input type="button" value="Imprimir" id="print_estudio" />');
        $(".submit-row").append(printButton);
        $("#print_estudio").click(function() {
            if (estudioFueModificado){
                alert("Por favor guarde los cambios y luego vuelva a hacer click en Imprimir.");
                return false;
            };

            currentUrl = window.location.href;
            estudioId = currentUrl.split("/")[6];
            printUrl = "/estudio/" + estudioId + "/imprimir/";
            var win = window.open(printUrl, '_blank');
            if (win) {
                win.focus();
            } else {
                alert('Please allow popups for this website');
            }
        });
        

        $("#id_practica").change(function() {
            estudioFueModificado = true;
            practicaChangeHandler();
        });

        ESTUDIOS_ALTOS = [1, 18, 10, 24];
        ESTUDIOS_BAJOS = [2, 19, 23];
        ESTUDIOS_COLANGIOS = [13, 34];

        var ALTA_NORMAL = "ESOFAGO. Normal, cardias a 37 cm de la arcada dentaria superior. No se evidencia reflujo gastro esofágico, hernia hiatal, ni esofagitis por reflujo. \n\n" +
            "ESTOMAGO: Mucosa de características normales. Por retroflexión se observa el techo gástrico con un buen cierre cardial. \n\n" +
            "PILORO: Permeable. \n\n" +
            "BULBO DUODENAL Y SEGUNDA PORCION DUODENAL. Normales. \n\n" +
            "CONCLUSION DIAGNOSTICA: ESOFAGO GASTRO DUODENO DE CARACTERISTICAS NORMALES. \n";

        var GASTRITIS = "ESOFAGO. Normal, cardias a 37 cm de la arcada dentaria superior. \n\n" +
            "ESTOMAGO: Mucosa antral difusamente congestiva eritematosa a predominio pre pilórico.\n\n" +
            "PILORO: Permeable.\n\n" +
            "BULBO DUODENAL Y SEGUNDA PORCION DUODENAL. Normales. \n\n" +
            "CONCLUSION DIAGNOSTICA: GASTRITIS SUPERFICIAL NO EROSIVA DE ANTRO GASTRICO. \n";

        var COLONO_NORMAL = "Ampolla rectal sin lesión mucosa. \n\n" +
            "Se franquea el ángulo recto sigmoides observando el colon sigmoides de características normales. \n\n" +
            "Se progresa por el colon descendente hasta franquear el ángulo esplénico observando el colon transverso, ángulo hepático y colon ascendente sin evidenciar lesión mucosa.\n\n" +
            "CONCLUSION DIAGNOSTICA: AMPOLLA RECTAL Y MARCO COLONICO VISUALIZADO HASTA CIEGO  DE CARACTERISTICAS NORMALES. \n";

        var COLANGIO_NORMAL = "En segunda porción duodenal , se visualiza la Ampolla de Vater de características normales.\n\n" +
            "Se canula sin dificultad observando la vía bilair intra hepática de calibre normal.\n\n" +
            "La vía biliar extra hepática presenta tanto el conducto hepático como el colédoco de aspecto y calibre normal.\n\n" +
            "No se observan imágenes radiolucidas en su interior y el drenaje de la sustancia de contraste se realiza en tiempo aceptable. \n\n" +
            "Buena tolerancia al procedimiento.\n\n" +
            "Las imágenes radioscópicas son digitalizadas e impresas en papel , acompañando el presente informe.\n";

        var COLANGIO_CON_CALCULO = "En segunda porción duodenal se visualiza la Ampolla de Vater de características normales. \n\n" +
            "Se canula sin dificultad observando la vía bilar intra hepática de calibre conservado. \n\n" +
            "La vía biiliar extra hepática se observa dilatada de aproximadamente 20 mm en promedio con una imagen radiolúcida en su interior con limites netos que podría corresponder a un lito coledociano.\n\n" +
            "Se realiza papilotomía ámplia y con canastilla de dormia se extrae un lito con las características descriptas en al imagen radiológica. \n\n" +
            "Buena tolerancia al procedimiento. \n\n" +
            "Las imágenes radioscópicas son digitalizadas e impresas en papel que acompañan al presente informe.";

    }

    function practicaChangeHandler(){
        $(".admin-informe-buttons").css("display", "none");
        practica_id = $("#id_practica option:selected").val();
        practica_id = parseInt(practica_id);

        if (ESTUDIOS_ALTOS.indexOf(practica_id) != -1){
            $("#altaNormalButton").css("display", "block");
            $("#gastritisButton").css("display", "block");
        }
        else if (ESTUDIOS_BAJOS.indexOf(practica_id) != -1){
            $("#colonoNormalButton").css("display", "block");
        }
        else if (ESTUDIOS_COLANGIOS.indexOf(practica_id) != -1){
            $("#colangioNormalButton").css("display", "block");
            $("#colangioConCalculoButton").css("display", "block");
        };
    }

});

