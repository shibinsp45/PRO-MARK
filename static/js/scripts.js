$("form[name=signup_form]").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/user/signup/validate",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (data) {
      console.log(data);
      window.location.href = "/dashboard/";
    },
    error: function (data) {
      console.log(data);
      $error.text(data.responseJSON.error).removeClass("error");
    },
  });

  e.preventDefault();
});

$("form[name=login_form]").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/user/login/validate",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (data) {
      console.log(data);
      window.location.href = "/dashboard/";
    },
    error: function (data) {
      console.log(data);
      $error.text(data.responseJSON.error).removeClass("error");
    },
  });

  e.preventDefault();
});

$(window).on("load", function () {
  $(".loading").fadeOut("slow");
});
