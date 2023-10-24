$(function(){
    $('.alert-modal').modal({
        keyboard: true,
        backdrop: "static",
        show:false,
        
    }).on('show.bs.modal', function(event){
        // get the id of the row
        var getIdFromRow = $(event.relatedTarget).data('id');
        var getModalType = $(event.relatedTarget).data('modal');
        var getSerialNumber = $(event.relatedTarget).data('serialnum');
        var getResponseId = $(event.relatedTarget).data('responseid');

        var serialNumberClass = "";
        var responseClass = "";

        if (getModalType == 'waiting') {
            //make your ajax call populate items
            $(this).find('#modal-title-waiting').html($('<b>מחשב שלא טופל מספר ' + getIdFromRow  + '</b>'));
            serialNumberClass = ".serial-number-waiting";
            responseClass = ".response-id-waiting";
        } else if (getModalType == 'not-taken') {
            //make your ajax call populate items
            $(this).find('#modal-title-not-taken').html($('<b>מחשב שטופל ולא נלקח מספר ' + getIdFromRow  + '</b>'));
            serialNumberClass = ".serial-number-not-taken";
            responseClass = ".response-id-not-taken";
        } else if (getModalType == 'taken') {
            //make your ajax call populate items
            $(this).find('#modal-title-taken').html($('<b>מחשב שטופל ונלקח מספר ' + getIdFromRow  + '</b>'));
            serialNumberClass = ".serial-number-taken";
            responseClass = ".response-id-taken";
        }
        
        $(serialNumberClass).val(getSerialNumber);
        $(responseClass).val(getResponseId);
    });
});