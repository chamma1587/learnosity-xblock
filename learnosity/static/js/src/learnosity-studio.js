/**
 * learnosityXBlockStudio-studio.js
 * JavaScript for handling the Studio view interactions of LearnosityXBlockStudio.
 */
function LearnosityXBlockStudio(runtime, element) {
    // Save button event
    $('.xblock-studio-view button[type="submit"]', element).click(function (event) {
        event.preventDefault();

        // Get input values from the form
        const activityId = $('input[name="activity_id"]', element).val();
        const activityName = $('input[name="activity_name"]', element).val();

        // Prepare data to send to the XBlock handler
        const data = {
            activity_id: activityId,
            activity_name: activityName,
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