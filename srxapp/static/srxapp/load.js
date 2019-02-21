
/**
 * Run loadobjects() two times: load address + application objects while
 * showing progress bar at first run; load policies in background at second run
*/

$(window).on('load', function() {
    loadobjects(true);
});

Pace.on('done', function() {
    $('#loadingtext').hide()
});


function loadobjects(firstRun) {

    var loadpolicies = 'False';
    if (firstRun == false) {
        loadpolicies = 'True';
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
        window.location.replace('/');
        if (firstRun == true) {
            loadobjects(false);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log(errorThrown.toString());
    });
}