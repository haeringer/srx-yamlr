// Event listeners etc. - run once DOM is ready
$(function() {
  $("#policy-list").on("click", ".pol", function() {
    loadExistingPolicy(this.id)
  })

  $("#policy-list").on("mouseenter", ".pol", function() {
    var polId = $(this).attr('id')
    getPolicyYaml(polId)
  })
  $("#policy-list").on("mouseleave", ".pol", function() {
    $("#yamlcard").addClass("d-none")
    $("#yamlcontainer").html("")
  })
})

function getPolicyYaml(polId) {
  $.get({
    url: "/srx/policysearch/getpolicyyaml/",
    data: { policyhash: polId },
  })
    .done(function(response) {
      $("#yamlcard").removeClass("d-none")
      $("#yamlcontainer").html(response)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function loadExistingPolicy(polId) {
  $.get({
    url: "/srx/policysearch/loadpolicy/",
    data: { policyhash: polId },
  })
    .done(function(response) {
      if (response === "load_existing") {
        window.location.replace("/srx/policybuilder/?loadpolicy")
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function policySearch() {
  var InputFrom = document.getElementById("search-from").value.toUpperCase()
  var InputTo = document.getElementById("search-to").value.toUpperCase()
  var policyList = $("#policy-list")

  var searchValues = {
    from: InputFrom,
    to: InputTo,
  }

  if ((InputFrom.length > 2) || (InputTo.length > 2)) {
    policySearchBackend(searchValues, policySearchCallback)
  } else {
    policyList.addClass("d-none")
    policyList.html("")
    return
  }

  function policySearchCallback(searchResult) {
    policyList.html("")
    policyList.removeClass("d-none")

    for (var i = 0; i < searchResult.length; i++) {
      var pol = searchResult[i]

      policyList.append(
        `<a href="#" class="list-group-item list-group-item-action pol" id=${pol.policyhash}>
          ${pol.name}
        </a>`
      )
    }
  }
}

function policySearchBackend(searchValues, callbackFunc) {
  $.get({
    url: "/srx/policysearch/search/",
    data: {
      input_from: searchValues.from,
      input_to: searchValues.to,
    },
  })
    .done(function(response) {
      callbackFunc(response)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}
