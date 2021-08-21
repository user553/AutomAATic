$(document).ready(function () {
    $("#loginEmail").bind('input propertychange', monitorInput);
    $("#loginPassword").bind('input propertychange', monitorInput);
    refreshImageCaptcha();
})

function monitorInput() {
    if (!$.trim($("#loginEmail").val()).match(/.+@.+\..+/)) {
        $("#loginEmail").attr("class", "form-control is-invalid");
        $("#loginEmailVerification").attr("class", "invalid-feedback");
        $("#loginEmailVerification").html("Invalid email");
    } else {
        $("#loginEmail").attr("class", "form-control is-valid");
        $("#loginEmailVerification").attr("class", "valid-feedback");
        $("#loginEmailVerification").html("Valid email");
    }

    if ($.trim($("#loginPassword").val()).length === 0) {
        // if ($.trim($("#loginPassword").val()).length < 5) {
        $("#loginPassword").attr("class", "form-control col-sm-12 col-md-6 col-lg-6 is-invalid");
        $("#loginPasswordVerification").attr("class", "invalid-feedback");
        $("#loginPasswordVerification").html("Password must be at least 1 character");
        // $("#loginPasswordVerification").html("Password less than 5 letters");
    } else {
        $("#loginPassword").attr("class", "form-control col-sm-12 col-md-6 col-lg-6 is-valid");
        $("#loginPasswordVerification").attr("class", "valid-feedback");
        $("#loginPasswordVerification").html("Valid password");
    }
}

function refreshImageCaptcha() {
    $.ajax({
        type: "get",
        url: "login/captcha/",
        headers: {
            "Accept": "text/html"
        },
        success: function (data) {
            $('#loginCaptcha').attr("src", data);
        }
    })
}

function sendForgetPasswordEmail(element) {
    let email = $.trim($("#loginEmail").val());
    if (email.match(/.+@.+\..+/)) {
        changeButtonState(element, "sending");
        $("#loginEmail").attr("disabled", true);

        let param = "email=" + email;
        $.post('login/password/', param, function (data) {
            if (data.startsWith("Success")) {
                changeButtonState(element, "tick");
                $("#loginPassword").val("");
                $("#loginPassword").focus();
            } else {
                changeButtonState(element, "retry");
                $("#loginEmail").attr("disabled", false);
            }
        })
    } else {
        alert("Fail (Front) : Invalid email");
        return false;
    }
}

function changeButtonState(element, status) {
    let ticks = 30;
    let tick = function () {
        if (ticks > 0) {
            setTimeout(function () {
                $(element).html("Sent(" + ticks + ")");
                ticks--;
                tick();
            }, 1000);
        } else {
            changeButtonState("retry");
        }
    };
    ticks = 30;
    switch (status) {
        case "sending": {
            $(element).attr("disabled", true);
            $(element).html("Sending");
            break;
        }
        case "tick": {
            $(element).attr("disabled", true);
            tick("Sent");
            break;
        }
        case "retry": {
            $(element).attr("disabled", false);
            $(element).html("Resend");
            break;
        }
    }
}