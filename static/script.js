$(document).ready(function () {
    $('#form').submit(function (e) {
        $("#submit").attr("disabled", true);
        $('#alert').text('Your forms are being compiled, a download will commence in just a sec...');
        return true;
    });
});