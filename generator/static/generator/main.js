
/* Loading animation */

$(window).on('load', function() {
    // Animate loader off screen
    $(".loading").fadeOut("slow");
});


/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    /* Recognize clicks on search result item */
    // use .on 'click' with parent selected to recognize events also on newly added items
    $('.list-inline').on('click', '.search-results-item', function() { addObject(this) });
    $('.list-group').on('click', '.lgi-icon-close', function() { removeObject(this) });

    $('#deploy-config').on('click', function() { deployConfig() });
    $('#create-object-dropdown a').on('click', function () { createInputForm(this) });

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

});


var currentObjects = {};
currentObjects['from'] = [];
currentObjects['to'] = [];
currentObjects['app'] = [];


function createInputForm(obj) {
    var selItem = $(obj).text();

    $('#form-container').find('form').addClass('d-none')

    if (selItem === 'Address') {
        $('#address-form').removeClass('d-none')
    } else if (selItem === 'Address Set') {
        $('#adrset-form').removeClass('d-none')
    } else if (selItem === 'Application') {
        $('#application-form').removeClass('d-none')
    } else if (selItem === 'Application Set') {
        $('#appset-form').removeClass('d-none')
    } else if (selItem === 'Zone') {
        swal('is noch nich implementiert')
    }
}

function deployConfig() {
    console.log('deploy config')
}



/* After click on search result item (see event listener),
retrieve parent zone and add object to card element */
function addObject(obj) {
    var objectId_dj = obj.id.split("_").pop();
    var source = obj.id.split("_").shift();

    if (source === 'from' || source === 'to') {

        $.getJSON('/generator/objectajax/', {objectid: objectId_dj})

        .done(function(response) {
            var objVal = response.obj_val
            if (Array.isArray(objVal) == true) {
                objVal = objVal.join(', ');
            }

            if (currentObjects.from.includes(objectId_dj) ||
                currentObjects.to.includes(objectId_dj) ) {
                swal("Object already in use!");
                return;
            }

            // blend in card element
            if ($('#added-zone-'+source).hasClass('d-none')) {
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

            if (source === 'from') {
                currentObjects.from.push(objectId_dj);
            } else if (source === 'to') {
                currentObjects.to.push(objectId_dj);
            }
            console.log(currentObjects)
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });
    } else if (source === 'app') {

        $.getJSON('/generator/objectajax/', {objectid: objectId_dj})

        .done(function(response) {
            var objVal;
            if (response.hasOwnProperty('obj_protocol')) {
                objVal = response.obj_protocol + ' ' + response.obj_port;
            } else {
                objVal = response.obj_apps.join(', ');
            }

            if (currentObjects.app.includes(objectId_dj)) {
                swal("Object already in use!");
                return;
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

            currentObjects.app.push(objectId_dj);
            console.log(currentObjects)
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });

    }
    $(obj).closest('.list-inline').addClass('d-none');
    $('#search-'+source).val('');
}


function removeObject(obj) {
    var listitem = $(obj).parents('.list-group-item').remove();
    var listitemId = $(listitem).attr('id');
    var objectId = listitemId.split('_', 2).join('_');
    var source = listitemId.split('_').shift();
    var objectId_dj = objectId.split('_').pop();

    if (!$('#added-list-'+source).has('li').length) {
        $('#added-obj-'+source).addClass('d-none');
        $('#added-zone-'+source).addClass('d-none');
    }

    if (source === 'from') {
        var index = currentObjects.from.indexOf(objectId_dj);
        if (index > -1) {
            currentObjects.from.splice(index, 1);
        }
    } else if (source === 'to') {
        var index = currentObjects.to.indexOf(objectId_dj);
        if (index > -1) {
            currentObjects.to.splice(index, 1);
        }
    } else if (source === 'app') {
        var index = currentObjects.app.indexOf(objectId_dj);
        if (index > -1) {
            currentObjects.app.splice(index, 1);
        }
    }
    console.log(currentObjects)
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