
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
    $('.list-group').on('click', '.lgi-icon-close', function() { deleteObject(this) });

    $('#deploy-config').on('click', function() { deployConfig() });
    $('#create-object-dropdown a').on('click', function () { createInputForm(this) });

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

});


var currentObj = {};
currentObj['from'] = [];
currentObj['to'] = [];
currentObj['app'] = [];
currentObj['configid'] = [];


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

    if (currentObjIsEmpty(currentObj)) {
        var newID = uuidv4();
        currentObj['configid'] = newID;
    }

    var objectId_dj = obj.id.split("_").pop();
    var source = obj.id.split("_").shift();
    var action = 'add';

    if (source === 'from' || source === 'to') {

        $.getJSON('/cgapp/ajax/objectdata/', {
            configid: currentObj.configid,
            objectid: objectId_dj,
            source: source,
            action: action,
            })

        .done(function(response) {
            var objVal = response.obj_val
            if (Array.isArray(objVal) == true) {
                objVal = objVal.join(', ');
            }

            if (source === 'from') {
                var zoneTo = $('#added-zone-body-to').html()
                if (zoneTo === response.parentzone) {
                    swal("Can't use the same zone for source and destination!")
                    return;
                }
            } else if (source === 'to') {
                var zoneFrom = $('#added-zone-body-from').html()
                if (zoneFrom === response.parentzone) {
                    swal("Can't use the same zone for source and destination!")
                    return;
                }
            }

            if (currentObj.from.includes(objectId_dj) ||
                currentObj.to.includes(objectId_dj) ) {
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
                currentObj.from.push(objectId_dj);
            } else if (source === 'to') {
                currentObj.to.push(objectId_dj);
            }
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });
    } else if (source === 'app') {

        $.getJSON('/cgapp/ajax/objectdata/', {
            configid: currentObj.configid,
            objectid: objectId_dj,
            source: source,
            action: action,
        })

        .done(function(response) {
            var objVal;
            if (response.hasOwnProperty('obj_protocol')) {
                objVal = response.obj_protocol + ' ' + response.obj_port;
            } else {
                objVal = response.obj_apps.join(', ');
            }

            if (currentObj.app.includes(objectId_dj)) {
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

            currentObj.app.push(objectId_dj);
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString());
        });

    }
    $(obj).closest('.list-inline').addClass('d-none');
    $('#search-'+source).val('');
}


function deleteObject(obj) {
    var listitem = $(obj).parents('.list-group-item').remove();
    var listitemId = $(listitem).attr('id');
    var objectId = listitemId.split('_', 2).join('_');
    var source = listitemId.split('_').shift();
    var objectId_dj = objectId.split('_').pop();
    var action = 'delete';

    if (!$('#added-list-'+source).has('li').length) {
        $('#added-obj-'+source).addClass('d-none');
        $('#added-zone-'+source).addClass('d-none');
        $('#added-zone-body-'+source).html('');
    }

    if (source === 'from') {
        var index = currentObj.from.indexOf(objectId_dj);
        if (index > -1) {
            currentObj.from.splice(index, 1);
        }
    } else if (source === 'to') {
        var index = currentObj.to.indexOf(objectId_dj);
        if (index > -1) {
            currentObj.to.splice(index, 1);
        }
    } else if (source === 'app') {
        var index = currentObj.app.indexOf(objectId_dj);
        if (index > -1) {
            currentObj.app.splice(index, 1);
        }
    }

    $.getJSON('/cgapp/ajax/objectdata/', {
        configid: currentObj.configid,
        objectid: objectId_dj,
        source: source,
        action: action,
    })

    .done(function(response) {
        console.log(response)
        console.log('do something with returned yaml here')
    })

    .fail(function(errorThrown) {
        console.log(errorThrown.toString());
    });

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


/* UUID cgapp helper function */
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    )
}

/* Check if arrays inside object are empty helper function */
function currentObjIsEmpty(obj) {
    var i = obj['from'].length + obj['to'].length + obj['app'].length
    if (i == 0) {
        return true;
    } else {
        return false;
    }
}