
function policySearch(e) {
  var inputEl = document.getElementById(e.id)
  var input = inputEl.value.toUpperCase()
  var ul = document.getElementById(e.id + "-ul")

  var searchType = e.id.split("-").pop()
  var listElement = $("#search-" + searchType + "-ul")

  if (input.length < 1) {
    listElement.html("")
    ul.classList.add("d-none")
    return
  }

  console.log("input: " + input)
  console.log("searchType: " + searchType)
}
