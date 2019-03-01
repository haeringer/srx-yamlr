
$(window).on('load', function() {

    loadobjects(true)

    function switchText() {
        var loadingText = $('#loadingtext')

        loadingText.fadeOut()
        window.setTimeout(function () {
            loadingText.html('Importing from YAML...')
        }, 400)
        loadingText.delay(400).fadeIn()
   }
    setTimeout(switchText, 1200)

})

Pace.on('done', function() {
    $('#loadingtext').hide()
})


function loadobjects(firstRun) {

    var loadpolicies = 'False'
    if (firstRun == false) {
        loadpolicies = 'True'
    }

    $.get({
        url: '/ajax/loadobjects/',
        data: {
            loadpolicies: loadpolicies,
        }
    })
    .done(function(response) {
        if (response.error != null) {
            alert('YAML import failed because of the following error:\n\n'
                + JSON.parse(response.error)
            )
        }
        window.location.replace('/')
        if (firstRun == true) {
            // Run loadobjects() a second time in order
            // to load policies in background
            loadobjects(false)
        }
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}
