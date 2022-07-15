$(document).ready(function () {

    $("#link").click(function () {
        $("#db").show();
        $('.New').hide();
        $('#table').show();

    });
    $("#link2").click(function () {
        $("#db").hide();
        $('.New').show();
        $('#table').hide();
        $('#redcod').hide()
    });


    // validations
//     $('form[name="register"]').on("submit", function (e) {
//         var username = $(this).find('input[name="username"]');
//         if ($.trim(username.val()) === "") {
//             e.preventDefault();
//            $("#errorAlert").hide().slideDown(400).removeClass('hide')
//         } else {


$(function () {

    $('form').each(function() {   // <- selects every <form> on page
        $(this).validate({        // <- initialize validate() on each form
            rules: {
                ip: "required",
                sid: "required",
                username: "required",
                password: {
                    required: true,
                    minlength: 5
                },
                ip1: "required",
                sid1: "required",
                username1: "required",
                password1: {
                    required: true,
                    minlength: 5
                },
            },
    
            // Specify validation error messages
            messages: {
                ip: "Please enter Hostname *",
                sid: "Please provide SID *",
                username: "Please enter your Username *",
                password: {
                    required: "Please provide Password *",
                    minlength: "Your password must be at least 5 characters long *"
    
                },
                ip1: "Please enter Port No *",
                username1: "Please enter your Username *",
                sid1: "Please provide SID *",
                password1: {
                    required: "Please provide Password *",
                    minlength: "Your password must be at least 5 characters long *"
                },
            },
    
            submitHandler: function (form) {
                form.submit();
                $("#loading").show();
            }
        });
    });

});


// db select
// if($('#exampleFormControlSelect').val()=='ORCL'){
//     // do something
//     alert("orcl selected!")
// } else {
//     // do something else
// }



$(".loading").hide();
          $("#btn").click(function () {
            //   $(this).hide();
              $("#loading").show();
          });

          

});
