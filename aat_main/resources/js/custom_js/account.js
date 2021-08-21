var base64src = ""

function fileChange(element) {
    $("#filenameLabel").html(element.files[0].name);
    if (!/image\/\w+/.test(element.files[0].type)) {
        return false;
    }
    let reader = new FileReader();
    reader.readAsDataURL(element.files[0]);
    reader.onload = function () {
        base64src = reader.result;
        document.getElementById('avatar').src = reader.result;
    };
}

function updateProfile() {
    if ($("#inputPasswordVerification").attr("class") != "invalid-feedback" && $("#confirmPasswordVerification").attr("class") != "invalid-feedback" && $("#inputNicknameVerification").attr("class") != "invalid-feedback") {
        let name = $("#inputNickname").val();
        let password = $("#inputPassword").val();
        let profile = $("#inputProfile").val();
        let formData = new FormData();
        formData.append("avatar", base64src);
        formData.append("name", name);
        formData.append("password", password);
        formData.append("profile", profile);
        $.ajax({
            url: "/account/profile/",
            type: 'POST',
            cache: false,
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                alert(data);
                setTimeout('window.location.href="/auth/logout/";', 500)
            }
        });
    } else {
        alert("Fail (Front) : Invalid information or no modification");
        return false;
    }
}

$(document).ready(function () {
    $("#inputPassword").bind('input propertychange', monitorAccountInput);
    $("#confirmPassword").bind('input propertychange', monitorAccountInput);
    $("#inputNickname").bind('input propertychange', monitorAccountInput);
    $("#avatar").attr("src", $("#avatar").attr("src") + "?r" + Math.random());
    $("#cardAvatar").attr("src", $("#cardAvatar").attr("src") + "?r" + Math.random());
})

function monitorAccountInput() {
    if ($.trim($("#inputPassword").val()).length < 3 && $.trim($("#inputPassword").val()).length > 0) {
        $("#inputPassword").attr("class", "form-control is-invalid");
        $("#inputPasswordVerification").attr("class", "invalid-feedback");
        $("#inputPasswordVerification").html("Password less than 3 letters, empty input will not change your password");
    } else {
        $("#inputPassword").attr("class", "form-control is-valid");
        $("#inputPasswordVerification").attr("class", "valid-feedback");
        $("#inputPasswordVerification").html("Valid password");
    }

    if ($.trim($("#confirmPassword").val()) != $.trim($("#inputPassword").val())) {
        $("#confirmPassword").attr("class", "form-control is-invalid");
        $("#confirmPasswordVerification").attr("class", "invalid-feedback");
        $("#confirmPasswordVerification").html("Check your password");
    } else {
        $("#confirmPassword").attr("class", "form-control is-valid");
        $("#confirmPasswordVerification").attr("class", "valid-feedback");
        $("#confirmPasswordVerification").html("Valid password");
    }

    let re = new RegExp(/[.,\/#!$%\^&\*;:{}=\-_`~()?0-9]/g);
    if (re.test($.trim($("#inputNickname").val())) || $.trim($("#inputNickname").val()) == "") {
        $("#inputNickname").attr("class", "form-control is-invalid");
        $("#inputNicknameVerification").attr("class", "invalid-feedback");
        $("#inputNicknameVerification").html("Invalid name, do not include punctuation and number");
    } else {
        $("#inputNickname").attr("class", "form-control is-valid");
        $("#inputNicknameVerification").attr("class", "valid-feedback");
        $("#inputNicknameVerification").html("Valid name");
    }
}