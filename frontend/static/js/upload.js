$(document).ready(function() {
     // render all popover question marks for bootstrap
    $("[data-toggle='popover']").popover();

    // hide error boxes
    hideErrorPanels();
    $("#misformatted").hide();

    // hide secondary data panels on start, then update according to checkboxes
    $("#dataset_panel2").hide();
    conditional_autocorr();

    // make conditional fields conditionally appear
    function conditional_autocorr(){
        if(document.getElementById('autocorr').checked) {
            $("#dataset_panel2").show();
        } else {
            $("#dataset_panel2").hide();
        }
    }

    $('#autocorr').click(conditional_autocorr);

    // booleans to make the server side validation bullet-proof by killing previous AJAX calls
    var request;
    // boolean to prevent submitting the form multiple times
    var left_upload = true;
    // do form validation on mouse over
    $("#upload-button").on("mouseenter", function(e) {
        if (left_upload) {
            // disable button till we check the form
            $("#upload-button").prop("disabled", true);
            left_upload = false;
            fd = collectFormData(false);
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
                url: UPLOAD_URL,
                method: "POST",
                data: fd,
                contentType: false,
                processData: false,
                cache: false,
                statusCode: {
                    413: function () {
                        window.location = TOO_LARGE_URL;
                    }
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    window.location = ERROR_URL;
                },
                success: function (data) {
                    // re-enable button for submission
                    $("#upload-button").prop("disabled", false);
                    data = JSON.parse(data);
                    if (data.status === "OK") {
                        hideErrorPanels();
                        $('#upload-button-text').text('UPLOAD');
                        $("#upload-button").on("click", function (e) {
                            $("#upload-button").prop("disabled", true);
                            $("#upload-button").off("click");
                            e.preventDefault();
                            doUpload();
                        })
                    } else if (data.status === "errors") {
                        $('#upload-button-text').text('CHECK FIELDS');
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
    $("#upload-button").on("mouseleave", function(e) {
        $("#upload-button").off("click");
        left_upload = true;
    })
});


function doUpload() {
    $("#progress").show();
    var $progressBar   = $("#progress-bar");

    // Gray out the form.
    $('#upload-button-text').text('Uploading files..');
    $("#upload-form :input").attr("disabled", "disabled");

    // Initialize the progress bar.
    $progressBar.css({"width": "0%"});
    // Collect the form data.
    fd = collectFormData(true);
    fd.append('check','false');
    var xhr = $.ajax({
        // setup CSRF protection, so our ajax SEND request is safe
        // http://flask-wtf.readthedocs.org/en/latest/csrf.html#ajax
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        },
        xhr: function() {
            var xhrobj = $.ajaxSettings.xhr();
            if (xhrobj.upload) {
                xhrobj.upload.addEventListener("progress", function(event) {
                    var percent = 0;
                    var position = event.loaded || event.position;
                    var total    = event.total;
                    if (event.lengthComputable) {
                        percent = Math.ceil(position / total * 100);
                    }

                    // Set the progress bar.
                    $progressBar.css({"width": percent + "%"});
                    $progressBar.prop('aria-valuenow',percent);
                    $progressBar.text(percent + "%");
                    if (percent === 100){
                        $('#upload-button-text').text('Please wait till redirected! Checking files...')
                    }
                }, false)
            }
            return xhrobj;
        },
        url: UPLOAD_URL,
        method: "POST",
        data: fd,
        contentType: false,
        processData: false,
        cache: false,
        statusCode: {
            // if we couldn't catch the too big file (IE8,9) on client side, we
            // let the user know with a special page
            413: function() {
                window.location = TOO_LARGE_URL;
            }
        },
        // if any error occurs, we say sorry and ask them to try again
        error: function(jqXHR, textStatus, errorThrown) {
            window.location = ERROR_URL;
        },
        success: function(data) {
            $progressBar.css({"width": "100%"});
            data = JSON.parse(data);
            if (data.status === "OK") {
                // All set, let's go to the profile page
                window.location = PROFILE_URL;
            } else if(data.status === "errors"){
                $('#upload-button-text').text('MISFORMATTED DATA FILE(S)');
                // we have errors to display
                displayErrors(data.errors);
            } else {
                window.location = ERROR_URL;
            }
        }
    });
}


function collectFormData(getFile) {
    // Go through all the form fields and collect their names/values.
    var fd = new FormData();
    $("#upload-form :input").each(function() {
        var $this = $(this);
        var name  = $this.attr("name");
        var type  = $this.attr("type") || "";
        var value = $this.val();

        // No name = no care.
        if (name === undefined) {
            return;
        }

        // Add files that are selected
        if (type === "file") {
            if (this.files[0] === undefined){
                return
            }else{
                if (getFile){
                    // we need to return a proper file handler, otherwise for
                    // validation name will be enough
                    value = this.files[0];
                }else{
                    // we add the file size to the name, so we can check it
                    value += '__' + this.files[0].size
                }
            }
        }

        // Checkboxes? Only add their value if they're checked.
        if (type === "checkbox" || type === "radio") {
            if (!$this.is(":checked")) {
                return;
            }
        }
        fd.append(name, value);
    });
    return fd;
}

function hideErrorPanels(){
    $('*[id*=error_]:visible').each(function() {
        $(this).hide();
        $(this).find('#error').text('');
    });
}


function displayErrors(errors){
    // first make sure all errors are hidden from previous rounds
    hideErrorPanels();
    // loop through the errors we got
    for (var key in errors) {
        if (errors.hasOwnProperty(key)) {
            var identifier = "#error_"+key;
            var errorArray = errors[key];
            var error_text = "";
            // loop through error text in each field
            for(var i = 0; i < errorArray.length; i++) {
                error_text += errorArray[i] + "\n";
            }
            $(identifier).show();
            $(identifier).find('#error').text(error_text);
        }
    }
}
