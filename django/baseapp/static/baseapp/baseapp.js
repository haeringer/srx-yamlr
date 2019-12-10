  /*
   * Run on page load
   */
  $(window).on("load", function() {
    setInterval(function() {
      checkSessionStatus()
    }, 10000)
  })

  // Make ajax POST requests work with Django's CSRF protection
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      function getCookie(name) {
        var cookieValue = null
        if (document.cookie && document.cookie != "") {
          var cookies = document.cookie.split(";")
          for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i])
            if (cookie.substring(0, name.length + 1) == name + "=") {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
              break
            }
          }
        }
        return cookieValue
      }
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"))
      }
    },
  })

  /*
   * Event listeners etc. - run once DOM is ready
   */
  $(function() {
    document.onclick= function() {
      extendSession()
    }

    // Settings Modal
    $("button#settings-save").click(function() {
      settingsHandler()
    })
    $("#update-cache").on("click", function() {
      $("#settings-modal").modal("toggle")
      importObjects()
    })
    $("#host-var-file-path-edit").on("click", function() {
      $("#host-var-file-path-value").addClass("d-none")
      $("#host-var-file-path-input").removeClass("d-none")
    })

    $('[data-toggle="tooltip"]').tooltip({
      trigger: "hover",
    })
    $("#settings-modal").on("hidden.bs.modal", function () {
      $(this).find("input").val("")
    })
  })

  function checkSessionStatus() {
    $.get("/session/status/")
      .done(function(response) {
        if (response === 1) {
          window.location.replace("/auth/logout/")
        }
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  function extendSession () {
    setTimeout(function(){
      $.post("/session/extend/")
        .fail(function(errorThrown) {
          console.log(errorThrown.toString())
        })
    }, 1000)
  }

  function settingsHandler() {
    var gogsToken = $("input#gogs-token").val()
    var pwNew = $("input#pw-new").val()
    var pwNewConfirm = $("input#pw-new-confirm").val()
    var newHostVarFilePath = $("input#host-var-file-path-input").val()

    if (gogsToken !== "") {
      setToken(gogsToken)
    }
    if (pwNew !== "") {
      if (pwNew !== pwNewConfirm) {
        showCreateFormError("password-form-alert", 1)
      } else {
        if (gogsToken !== "") {
          setTimeout(function() {
            changePassword(pwNew)
          }, 1000)
        } else {
          changePassword(pwNew)
        }
      }
    }
    if (newHostVarFilePath !== "") {
      setHostVarFilePath(newHostVarFilePath)
    }
  }

  function setToken(token) {
    var tokenIndicator = $("#token-indicator")
    var tokenText = $("#token-set-check")

    if (tokenIndicator.hasClass("custom-green") === true) {
      tokenIndicator.removeClass("custom-green").addClass("custom-red")
      tokenText.html("Token not set")
    }
    $(".spinner-container").fadeIn()

    $.post({
      url: "/settings/token/gogs/",
      data: {
        token: token,
      },
    })
      .done(function(response) {
        if (response === 0) {
          setTimeout(function() {
            $(".spinner-container").fadeOut()
            tokenIndicator.removeClass("custom-red").addClass("custom-green")
            tokenText.html("Token has been set")
            if ($("#yamlcard").hasClass("d-none") === false) {
              window.location.replace("/srx/policybuilder/")
            }
          }, 1500)
        }
      })
      .fail(function(errorThrown) {
        $(".spinner-container").fadeOut()
        console.log(errorThrown.toString())
      })
  }

  function changePassword(pwNew) {
    $("#settings-modal").modal("toggle")
    $.post({
      url: "/settings/password/change/",
      data: {
        password: pwNew,
      },
    })
      .done(function(response) {
        swal({
          title: "Password changed",
          text: "Please log in again",
          icon: "success",
        }).then(() => {
          window.location.replace("/auth/logout/")
        })
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  function setHostVarFilePath(newHostVarFilePath) {
    $(".spinner-container").fadeIn()

    $.post("/srx/policybuilder/sethostvarfilepath/", {
      host_var_file_path: newHostVarFilePath,
    })
      .done(function(response) {
        if (response === 0) {
          $("#host-var-file-path-input").addClass("d-none")
          $("#host-var-file-path-value").removeClass("d-none")
          $("#host-var-file-path-value").html(newHostVarFilePath)
          setTimeout(function() {
            $(".spinner-container").fadeOut()
            window.location.replace("/srx/policybuilder/")
          }, 1500)
        }
      })
      .fail(function(errorThrown) {
        $(".spinner-container").fadeOut()
        console.log(errorThrown.toString())
      })
  }
