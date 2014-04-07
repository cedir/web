
function getSearch (){
	var keyWord = document.getElementById('keyWord').value;
	if (keyWord != ''){
		document.searchForm.submit();
	}
	else{
		alert('Debe ingresar al menos 3 caracteres para realizar la búsqueda.');
	}
}
function CheckAll(){


	for (var i=0;i<document.ordenespresentadas.elements.length;i++)
	{
		var e = document.ordenespresentadas.elements[i];
		if ((e.name.match(/seleccion/)) && (e.type=='checkbox'))
		e.checked = document.ordenespresentadas.allbox.checked;
	}
}
function UnCheckAll(){
	var TotalBoxes = 0;
	var TotalOn = 0;
	for (var i=0;i<document.ordenespresentadas.elements.length;i++)
	{
		var e = document.ordenespresentadas.elements[i];
		if ((e.name != 'allbox') && (e.type=='checkbox'))
		{
			TotalBoxes++;
		if (e.checked)
		{
			TotalOn++;
		}
		}
	}
	if (TotalBoxes==TotalOn)
	{document.ordenespresentadas.allbox.checked=true;}
	else
	{document.ordenespresentadas.allbox.checked=false;}
}


CDate = {
  convertToRegular: function(date){
    if (date == "") return date;
    var str = date.split('-');
    return str[2] + "/" + str[1] + "/" + str[0];
  },
  convertToSQL: function(){
    
  }
  
};