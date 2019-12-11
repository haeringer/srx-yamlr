
function policySearch(e) {
  var InputFrom = document.getElementById("search-from").value.toUpperCase()
  var InputTo = document.getElementById("search-to").value.toUpperCase()

  var searchValues = {
    from: InputFrom,
    to: InputTo,
  }

  console.log(searchValues)

  if ((InputFrom.length > 2) || (InputTo.length > 2)) {
    policySearchBackend(searchValues, policySearchCallback)
  }

  function policySearchCallback(searchResult) {
    console.log(searchResult)
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
