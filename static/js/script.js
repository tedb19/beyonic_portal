function autoCloseAlert(selector){
    $(selector).fadeTo(2000, 500).slideUp(2000, function(){
        $(selector).alert('close');
    });  
}


autoCloseAlert(".alert");