 // Handle button click event
 $('#myButton').click(function() {
    event.preventDefault();  // Prevent the default form submission
    // Retrieve the input value
    var prompt = $('#prompt').val();
    var context = $('#context').text();

    $('#gptoutput').show();

    $.ajax({
      url: '/get_answer',  // Replace with the URL of your Flask route
      method: 'POST',    // Replace with the HTTP method you want to use (e.g., POST, GET)
      data: { prompt: prompt, context: context },  // Pass the input value as data
      success: function(response) {
        // Handle the response from the server
        $('#gptoutput').text(response.message);
      },
      error: function(error) {
        // Handle any errors
        console.error(error);
      }
    });
  });