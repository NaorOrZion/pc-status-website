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

        var serialNumberId = "";
        var responseId = "";

        if (getModalType == 'waiting') {
            //make your ajax call populate items
            $(this).find('#modal-title-waiting').html($('<b>מחשב שלא טופל מספר ' + getIdFromRow  + '</b>'));
            serialNumberId = "serial_number-waiting";
            responseId = "response_id-waiting";
        } else if (getModalType == 'not-taken') {
            //make your ajax call populate items
            $(this).find('#modal-title-not-taken').html($('<b>מחשב שטופל ולא נלקח מספר ' + getIdFromRow  + '</b>'));
            serialNumberId = "serial_number-not-taken";
            responseId = "response_id-not-taken";
        } else if (getModalType == 'taken') {
            //make your ajax call populate items
            $(this).find('#modal-title-taken').html($('<b>מחשב שטופל ונלקח מספר ' + getIdFromRow  + '</b>'));
            serialNumberId = "serial_number-taken";
            responseId = "response_id-taken";
        }
        
        // Get the input element by ID
        var inputSerialNumber = document.getElementById(serialNumberId);
        var inputResponseId = document.getElementById(responseId);

        // Set the value of the input element
        inputSerialNumber.value = getSerialNumber;
        inputResponseId.value = getResponseId;
    });
});