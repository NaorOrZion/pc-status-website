$(function(){
    $('#alert-modal-waiting').modal({
        keyboard: true,
        backdrop: "static",
        show:false,
        
    }).on('show.bs.modal', function(event){
        // get the id of the row
        var getIdFromRow = $(event.relatedTarget).data('id');
        var getSerialNumber = $(event.relatedTarget).data('serialnum');

        // Set the data-serial-number attribute for each button
        $(this).find('button[data-serial-number]').attr('data-serial-number', getSerialNumber);

        //make your ajax call populate items
        $(this).find('#modal-title-waiting').html($('<b>מחשב שלא טופל מספר ' + getIdFromRow  + '</b>'))

        // Handle the click event for the "מחיקה" button
        $(this).on('click', '.delete-button', function() {
            var serialNumberToDelete = $(this).data('serial-number');

            // Send the serial number to your Python function using an AJAX request
            $.ajax({
                type: 'POST',
                url: '/delete-row',  // Replace with the actual endpoint on your server
                data: { serial_number: serialNumberToDelete },
                success: function(response) {
                    console.log('Row deleted successfully:', response);
                },
                error: function(error) {
                    console.error('Error deleting row:', error);
                }
            });

            // Close the modal or perform other actions if needed
            $('#alert-modal-waiting').modal('hide');
        });
    });
});

$(function(){
    $('#alert-modal-not-taken').modal({
        keyboard: true,
        backdrop: "static",
        show:false,
        
    }).on('show.bs.modal', function(event){
        // get the id of the row
        var getIdFromRow = $(event.relatedTarget).data('id');
        var getSerialNumber = $(event.relatedTarget).data('serialnum');

        // Set the data-serial-number attribute for each button
        $(this).find('button[data-serial-number]').attr('data-serial-number', getSerialNumber);

        //make your ajax call populate items
        $(this).find('#modal-title-not-taken').html($('<b>מחשב שטופל ולא נלקח מספר ' + getIdFromRow  + '</b>'))
    });
});

$(function(){
    $('#alert-modal-taken').modal({
        keyboard: true,
        backdrop: "static",
        show:false,
        
    }).on('show.bs.modal', function(event){
        // get the id of the row
        var getIdFromRow = $(event.relatedTarget).data('id');
        var getSerialNumber = $(event.relatedTarget).data('serialnum');

        // Set the data-serial-number attribute for each button
        $(this).find('button[data-serial-number]').attr('data-serial-number', getSerialNumber);

        //make your ajax call populate items
        $(this).find('#modal-title-taken').html($('<b>מחשב שטופל ונלקח מספר ' + getIdFromRow  + '</b>'))
    });
});