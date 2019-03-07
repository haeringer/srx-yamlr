
$(window).on('load', function() {

    loadobjects()

    function switchText() {
        var loadingText = $('#loadingtext')

        loadingText.fadeOut('fast')
        window.setTimeout(function () {
            loadingText.html('Importing from YAML...')
        }, 200)
        loadingText.delay(200).fadeIn('fast')
   }
    setTimeout(switchText, 600)

})

Pace.on('done', function() {
    $('#loadingtext').hide()
})


function loadobjects() {
    $.get({
        url: '/ajax/loadobjects/',
    })
    .done(function(response) {
        if (response.error != null) {
            alert('YAML import failed because of the following error:\n\n'
                + JSON.parse(response.error)
            )
        }
        window.location.replace('/')
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}
