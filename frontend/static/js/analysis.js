$(document).ready(function() {
     // render all popover question marks for bootstrap
    $("[data-toggle='popover']").popover();

    // hide error boxes
    hideErrorPanels();

    // booleans to make the server side validation bullet-proof by killing previous AJAX calls
    var request;
    // boolean to prevent submitting the form multiple times
    var left_upload = true;
    // do form validation on mouse over
    $("#analyse-button").on("mouseenter", function(e) {
        if (left_upload) {
            // disable button till we check the form
            $("#analyse-button").prop("disabled", true);
            left_upload = false;
            fd = collectFormData();
            fd.append('check', 'true');
            // if two POST requests go in quickly, cancel the first
            if (request && request.readyState !== 4) {
                request.abort();
            }

            // submit AJAX POST request for server side form validation
            request = $.ajax({
                beforeSend: function (xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken)
                    }
                },
                url: ANALYSIS_URL,
                method: "POST",
                data: fd,
                contentType: false,
                processData: false,
                cache: false,
                error: function (jqXHR, textStatus, errorThrown) {
                    window.location = ERROR_URL;
                },
                success: function (data) {
                    // re-enable button for submission
                    $("#analyse-button").prop("disabled", false);
                    data = JSON.parse(data);
                    if (data.status === "OK") {
                        hideErrorPanels();
                        $('#analyse-button-text').text('ANALYSE')
                        $("#analyse-button").on("click", function (e) {
                            $("#analyse-button").prop("disabled", true);
                            e.preventDefault();
                            doAnalysis();
                            $("#analyse-button").off("click");
                        })
                    } else if (data.status === "errors") {
                        $('#analyse-button-text').text('CHECK FIELDS')
                        // we have errors to display
                        displayErrors(data.errors);
                    } else {
                        window.location = ERROR_URL;
                    }
                }
            });
        }
    });
    // make sure to remove submit event from submit button when user rolls off of it
    $("#analyse-button").on("mouseleave", function(e) {
        $("#analyse-button").off("click");
        left_upload=true;
    })
});

function doAnalysis() {
    // Gray out the form.
    $('#analyse-button-text').text('Please wait till redirected..')
    $("#analysis-form :input").attr("disabled", "disabled");

    fd = collectFormData();
    fd.append('check','false');
    var xhr = $.ajax({
        // setup CSRF protection, so our ajax SEND request is safe
        // http://flask-wtf.readthedocs.org/en/latest/csrf.html#ajax
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        },
        url: ANALYSIS_URL,
        method: "POST",
        data: fd,
        contentType: false,
        processData: false,
        cache: false,
        // if any error occurs, we say sorry and ask them to try again
        error: function(jqXHR, textStatus, errorThrown) {
            window.location = ERROR_URL;
        },
        success: function(data) {
            data = JSON.parse(data);
            if (data.status === "OK") {
                // All set, let's go to the profile page
                window.location = PROFILE_URL;
            } else {
                window.location = ERROR_URL;
            }
        }
    });
}


function collectFormData() {
    // Go through all the form fields and collect their names/values.
    var fd = new FormData();
    $("#analysis-form :input").each(function() {
        var $this = $(this);
        var name  = $this.attr("name");
        var type  = $this.attr("type") || "";
        var value = $this.val();

        // No name = no care.
        if (name === undefined) {
            return;
        }
        // Checkboxes? Only add their value if they're checked.
        if (type === "checkbox" || type === "radio") {
            if (!$this.is(":checked")) {
                return;
            }
        }
        // hack to disable NumberRange validation for constrain_dist field if
        // constrain_corr false
        if (name==='constrain_dist' && !document.getElementById('constrain_corr').checked){
            return
        }
        fd.append(name, value);
    });
    return fd;
}

function hideErrorPanels(){
    $('*[id*=error_]:visible').each(function() {
        $(this).hide()
        $(this).find('#error').text('');
    });
}


function displayErrors(errors){
    // first make sure all errors are hidden from previous rounds
    hideErrorPanels()

    // loop through the errors we got
    for (var key in errors) {
        if (errors.hasOwnProperty(key)) {
            var identifier = "#error_"+key;
            var errorArray = errors[key];
            var error_text = ""
            // loop through error text in each field
            for(var i = 0; i < errorArray.length; i++) {
                error_text += errorArray[i] + "\n";
            }
            $(identifier).show()
            $(identifier).find('#error').text(error_text);
        }
    }
}
