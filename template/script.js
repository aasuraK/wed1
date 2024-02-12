$(document).ready(function() {
    const inputForm = $("#input-form");
    const userInput = $("#user-input");
    const loadingContainer = $("#loading-container");
    const graphContainer = $("#graph-container");

    $("#upload-button").click(function() {
        const formData = new FormData(inputForm);
        $.ajax({
            url: "/upload",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                // Handle success, store file information (if needed)
                alert("File uploaded!");
                console.log(response);
            },
            error: function(error) {
                alert("Invalid file type! Please upload a CSV file.");
                console.log(error);
            }
        });
    });

    

    inputForm.submit(function(event) {
        event.preventDefault();

        const rawText = userInput.val();

        // Show loading animation
        loadingContainer.removeClass("d-none");

        $.ajax({
            data: {
                query: rawText,
            },
            type: "POST",
            url: "/ask",
        }).done(function(data) {
            console.log(data);
            const botInsight = data.response;
            const graphData = data.graph;

            if (graphData) {
                const graphImage = $(`<img src="data:image/png;base64,${graphData}">`);
                graphContainer.empty().append(graphImage); // Clear and append
            } else {
                alert("No graph generated for this query.");
            }

            loadingContainer.addClass("d-none");

            // Display the chatbot response here (optional)
            // Example: $("#chatbot-response").text(botInsight);
        });
    });
});
