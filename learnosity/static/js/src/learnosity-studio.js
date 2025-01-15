/**
 * learnosityXBlockStudio-studio.js
 * JavaScript for handling the Studio view interactions of LearnosityXBlockStudio.
 */
function LearnosityXBlockStudio(runtime, element) {
    // Save button event
    $('.xblock-studio-view button[type="submit"]', element).click(function (event) {
        event.preventDefault();

        // Get input values from the form
        const parameterOne = $('input[name="parameter_one"]', element).val();
        const parameterTwo = $('input[name="parameter_two"]', element).val();

        // Prepare data to send to the XBlock handler
        const data = {
            parameter_one: parameterOne,
            parameter_two: parameterTwo,
        };

        // Save the parameters via the runtime's handler
        const handlerUrl = runtime.handlerUrl(element, 'save_studio_parameters');
        $.post(handlerUrl, JSON.stringify(data))
            .done(function (response) {
                if (response.result === "success") {
                    // Notify the user that saving was successful
                    alert('Parameters saved successfully!');
                } else {
                    // Handle any error returned by the server
                    alert('An error occurred while saving parameters.');
                }
            })
            .fail(function () {
                // Notify the user about a failure in the request
                alert('Failed to save parameters.');
            });
    });
}
