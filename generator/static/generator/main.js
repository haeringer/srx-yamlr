
/* Loading animation */

var timeout;
function loading() {
    timeout = setTimeout(showPage, 1200);
}

function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("mainDiv").style.display = "block";
}


/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    /* Recognize clicks on search result item */
    // use .on 'click' with parent selected to recognize events also on newly added items
    $('.list-inline').on('click', '.search-results-item', function() { addObject(this) });

    $('.list-group').on('click', '.lgi-icon-close', function() { removeObject(this) });

});


/* After click on search result item (see event listener),
retrieve parent zone and add object to card element */
function addObject(obj) {
    var objectId_dj = obj.id.split("_").pop();
    var source = obj.id.split("_").shift();

    if (source === 'from' || source === 'to') {

        $.getJSON('/generator/getaddressdata/', {objectid: objectId_dj})

        .done(function(response) {
            var objVal = response.obj_val
            if (Array.isArray(objVal) == true) {
                objVal = objVal.join(', ');
            }
            // blend in card element
            if ($('#added-zone-'+source).hasClass('d-none')) {
                if (source === 'to') {
                    var zoneFrom = $('#added-zone-body-from').html();
                    if (zoneFrom === response.parentzone) {
                        swal("Please choose an object from another zone!");
                        return;
                    }
                } else if (source === 'from') {
                    var zoneFrom = $('#added-zone-body-to').html();
                    if (zoneFrom === response.parentzone) {
                        swal("Please choose an object from another zone!");
                        return;
                    }
                }
                $('#added-zone-'+source).removeClass('d-none');
                $('#added-zone-body-'+source).html(response.parentzone);
            } else {
                var zonePresent = $('#added-zone-body-'+source).html();
                if (zonePresent !== response.parentzone) {
                    swal("Can't use objects from different zones!");
                    return;
                }
            }

            $('#added-obj-'+source).removeClass('d-none');
            $('#added-list-'+source).append(
                `<li class="list-group-item" id="${source}_${objectId_dj}_added">
                  <div class="row">
                    <div class="col-auto mr-auto lgi-name">${response.obj_name}</div>
                    <div class="lgi-icon-close pr-2">
                      <button type="button" class="close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                    <div class="w-100"></div>
                    <div class="col-auto mr-auto lgi-name text-black-50"><small>${objVal}</small></div>
                  </div>
                </li>`
            );
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });
    } else if (source === 'app') {

        $.getJSON('/generator/getapplicationdata/', {objectid: objectId_dj})

        .done(function(response) {
            var objVal;
            if (response.hasOwnProperty('obj_protocol')) {
                objVal = response.obj_protocol + ' ' + response.obj_port;
            } else {
                objVal = response.obj_apps.join(', ');
            }
            $('#added-obj-app').removeClass('d-none');
            $('#added-list-app').append(
                `<li class="list-group-item" id="app_${objectId_dj}_added">
                  <div class="row">
                    <div class="col-auto mr-auto lgi-name">${response.obj_name}</div>
                    <div class="lgi-icon-close pr-2">
                      <button type="button" class="close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                  <div class="w-100"></div>
                  <div class="col-auto mr-auto lgi-name text-black-50"><small>${objVal}</small></div>
                  </div>
                </li>`
            );
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });

    }
    $(obj).closest('.list-inline').addClass('d-none');
    $('#search-'+source).val('')
}


function removeObject(obj) {
    listitem = $(obj).parents('.list-group-item').remove();
    listitemid = $(listitem).attr('id');
    var source = listitemid.split("_").shift();

    if (!$('#added-list-'+source).has('li').length) {
        $('#added-obj-'+source).addClass('d-none');
        $('#added-zone-'+source).addClass('d-none');
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
        a0 = li[i].getElementsByTagName('a')[0];
        a1 = li[i].getElementsByTagName('a')[1];
        a = a0.innerHTML.toUpperCase() + ' ' + a1.innerHTML.toUpperCase();
        if (a.indexOf(filter) > -1 && filter.length >= 1) {
            ul.classList.remove('d-none');
            li[i].style.display = '';
        } else {
            li[i].style.display = 'none';
        }
    }
}