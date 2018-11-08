
/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    /* Recognize clicks on search result item */
    // use .on 'click' with parent selected to recognize events also on newly added items
    $('.list-inline').on('click', '.search-results-item', function(e) {
        var objText = this.textContent;
        var objectId_dj = this.id.split("_").pop();
        var source = this.id.split("_").shift();

        addObject(objText, objectId_dj, source);

        $(e.target).closest('.list-inline').addClass('d-none');
        $('#search-'+source).val('')
    });

});


/* After click on search result item (see event listener),
retrieve parent zone and add object to card element */
function addObject(objText, objectId_dj, source) {
    if (source === 'from' || source === 'to') {
        // ajax call to retrieve parent zone
        $.getJSON('/generator/getparentzone/', {objectid: objectId_dj})

        .done(function(response) {
            // blend in card element
            $('#added-obj-'+source).removeClass('d-none');
            $('#added-zone-'+source).html(response);
            $('#added-list-'+source).append(`<li class="list-group-item">${objText}</li>`);
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });
    } else if (source === 'app') {
        $('#added-obj-app').removeClass('d-none');
        $('#added-list-app').append(`<li class="list-group-item">${objText}</li>`);
    }
}

/* Filter elements in provided object list and blend in result list element */
function objectSearch(e) {
    var input, filter, ul, li, a, i;
    input = document.getElementById(e.id);
    filter = input.value.toUpperCase();
    ul = document.getElementById(e.id + '-ul');
    li = ul.getElementsByTagName('li');

    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName('a')[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1 && filter.length >= 1) {
            $(ul).removeClass('d-none');
            li[i].style.display = '';
        } else {
            li[i].style.display = 'none';
        }
    }
}