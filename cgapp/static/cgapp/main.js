
/*
* Run on page load
*/
$(window).on('load', function() {
    // generate an initial configuration id
    var newID = uuidv4();
    currentObj['configid'] = newID;
});


/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    $("button#create-object-save").click(function() { createObject() });

    // use .on 'click' with parent selected to recognize events also on newly added items
    $('#search-forms').on('click', '.search-results-item', function() { addObject(this) });

    $('.list-group').on('click', '.lgi-icon-close', function() { deleteObject(this) });

    $('#create-object-dropdown a').on('click', function () { createInputForm(this) });
    $('#adrset-form-control-zone').on('click', function() { filterObjects(this) });

    $('#clear-config').on('click', function() { window.location.replace('/load') });
    $('#check-config').on('click', function() { checkConfig() });
    $('#deploy-config').on('click', function() { deployConfig() });

    $('[data-toggle="tooltip"]').tooltip()

});


var currentObj = {};
currentObj['from'] = [];
currentObj['to'] = [];
currentObj['app'] = [];
currentObj['configid'] = [];
var selObj;



function filterObjects(zoneselector) {
    var selectedzone = $(zoneselector).val();

    $.get({
        url: '/ajax/filterobjects/',
        data: {
            selectedzone: selectedzone,
        }
    })
    .done(function(response) {
        if (response === null) {
            return;
        }
        addresses = response.addresses

        if (Array.isArray(addresses) == true) {
            $('#adrset-form-control-objects').html('')
            $.each(addresses, function(key, value) {
                $('#adrset-form-control-objects')
                    .append($('<option class="small">', { value : key })
                    .text(value));
            });
        } else {
            $('#adrset-form-control-objects').html(
                `<option class="small">${ addresses }</option>`
            )
        }

    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log(errorThrown.toString());
    });
}


function createInputForm(obj) {
    selObj = $(obj).text();

    $('#form-container').find('form').addClass('d-none')

    if (selObj === 'Address') {
        $('#address-form').removeClass('d-none')
    } else if (selObj === 'Address Set') {
        $('#adrset-form').removeClass('d-none')
    } else if (selObj === 'Application') {
        $('#application-form').removeClass('d-none')
    } else if (selObj === 'Application Set') {
        $('#appset-form').removeClass('d-none')
    }
}


function createObject() {

    if (selObj === 'Address') {
        var objtype = 'address';
        var addresszone = $("select#address-form-control-zone").val();
        var addressname = $("input#address-form-control-name").val();
        var addressip = $("input#address-form-control-ip").val();

        if (addresszone == '' || addressname == '' || addressip == '') {
            $('#address-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $.post({
            url: '/ajax/newobject/',
            data: {
                configid: currentObj.configid,
                objtype: objtype,
                addresszone: addresszone,
                addressname: addressname,
                addressip: addressip,
            }
        })
        .done(function(response) {
            closeModalAndRefresh(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Address Set') {
        var objtype = 'addrset';
        var addrsetzone = $("select#adrset-form-control-zone").val();
        var addrsetname = $("input#adrset-form-control-name").val();
        var addrsetobjects = $("#adrset-form-control-objects").val();

        if (addrsetzone == '' || addrsetname == '' || addrsetobjects == '') {
            $('#addrset-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $.post({
            url: '/ajax/newobject/',
            data: {
                configid: currentObj.configid,
                objtype: objtype,
                addrsetzone: addrsetzone,
                addrsetname: addrsetname,
                addrsetobjects: addrsetobjects,
            }
        })
        .done(function(response) {
            closeModalAndRefresh(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Application') {
        var objtype = 'application';
        var appname = $("input#application-form-control-name").val();
        var appport = $("input#application-form-control-port").val();
        var appprotocol = $("select#application-form-control-protocol").val();

        if (appprotocol == '' || appname == '' || appport == '') {
            $('#application-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $.post({
            url: '/ajax/newobject/',
            data: {
                configid: currentObj.configid,
                objtype: objtype,
                appname: appname,
                appport: appport,
                appprotocol: appprotocol,
            }
        })
        .done(function(response) {
            closeModalAndRefresh(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Application Set') {
        var objtype = 'appset';
        var appsetname = $("input#appset-form-control-name").val();
        var appsetobjects = $("#appset-form-control-objects").val();

        if (appsetname == '' || appsetobjects == '') {
            $('#appset-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $.post({
            url: '/ajax/newobject/',
            data: {
                configid: currentObj.configid,
                objtype: objtype,
                appsetname: appsetname,
                appsetobjects: appsetobjects,
            }
        })
        .done(function(response) {
            closeModalAndRefresh(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    }
}


function closeModalAndRefresh(response) {
    // update yaml config
    $('#yamlcontainer').html(response.yamlconfig);
    $('#yamlcard').removeClass('d-none');

    // reload specific div of index.html
    $('#search-forms').load('/ #search-forms');

    // close modal
    $('#create-object-modal').modal('toggle');
}


function checkConfig() {
    $.post({
        url: '/ajax/checkconfig/',
        data: {
            configid: currentObj.configid,
        }
    })
    .done(function(response) {
        console.log(response.output)
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log(errorThrown.toString());
    });
}


function deployConfig() {
    console.log('deploy config')
}



/* After click on search result item (see event listener),
retrieve parent zone and add object to card element */
function addObject(obj) {

    $('.spinner-container').fadeIn()

    var objectId_dj = obj.id.split("_", 2).pop();
    var objectId_db = obj.id.split("_", 3).pop();
    var source = obj.id.split("_").shift();
    var action = 'add';

    if (source === 'from' || source === 'to') {

        $.post('/ajax/objectdata/', {
            configid: currentObj.configid,
            objectid: objectId_db,
            source: source,
            action: action,
            })

        .done(function(response) {
            if (response.error != null) {
                alert('YAML build failed because of the following error:\n\n'
                    + JSON.parse(response.error)
                )
            }
            var objVal = response.obj_val
            if (Array.isArray(objVal) == true) {
                objVal = objVal.join(', ');
            }

            $('.spinner-container').fadeOut()

            if (source === 'from') {
                var zoneTo = $('#added-zone-body-to').html()
                if (zoneTo === response.parentzone) {
                    swal("Can't use the same zone for source and destination!")
                    return;
                }
                if (currentObj.from.includes(objectId_db)) {
                    swal("Object already in use!");
                    return;
                }
            } else if (source === 'to') {
                var zoneFrom = $('#added-zone-body-from').html()
                if (zoneFrom === response.parentzone) {
                    swal("Can't use the same zone for source and destination!")
                    return;
                }
                if (currentObj.to.includes(objectId_db)) {
                    swal("Object already in use!");
                    return;
                }
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
                `<li class="list-group-item" id="${source}_${objectId_dj}_${objectId_db}_added">
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
                currentObj.from.push(objectId_db);
            } else if (source === 'to') {
                currentObj.to.push(objectId_db);
            }

            $('#yamlcontainer').html(response.yamlconfig);
            $('#yamlcard').removeClass('d-none');

        })

        .fail(function(errorThrown) {
            $('.spinner-container').fadeOut()
            console.log(errorThrown.toString());
        });

    } else if (source === 'app') {

        $.post('/ajax/objectdata/', {
            configid: currentObj.configid,
            objectid: objectId_db,
            source: source,
            action: action,
        })

        .done(function(response) {
            if (response.error != null) {
                alert('YAML build failed because of the following error:\n\n'
                    + JSON.parse(response.error)
                )
            }
            var objVal;
            if (response.hasOwnProperty('obj_protocol')) {
                objVal = response.obj_protocol + ' ' + response.obj_port;
            } else {
                objVal = response.obj_apps.join(', ');
            }

            $('.spinner-container').fadeOut()

            if (currentObj.app.includes(objectId_db)) {
                swal("Object already in use!");
                return;
            }

            $('#added-obj-app').removeClass('d-none');
            $('#added-list-app').append(
                `<li class="list-group-item" id="app_${objectId_dj}_${objectId_db}_added">
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

            currentObj.app.push(objectId_db);

            $('#yamlcontainer').html(response.yamlconfig);
            $('#yamlcard').removeClass('d-none');
        })

        .fail(function(errorThrown) {
            $('.spinner-container').fadeOut()
            console.log(errorThrown.toString());
        });

    }
    $(obj).closest('.list-inline').addClass('d-none');
    $('#search-'+source).val('');
}


function deleteObject(obj) {
    var listitem = $(obj).parents('.list-group-item').remove();
    var listitemId = $(listitem).attr('id');
    var source = listitemId.split('_').shift();
    var objectId_db = listitemId.split('_', 3).pop();
    var action = 'delete';

    if (!$('#added-list-'+source).has('li').length) {
        $('#added-obj-'+source).addClass('d-none');
        $('#added-zone-'+source).addClass('d-none');
        $('#added-zone-body-'+source).html('');
    }

    if (source === 'from') {
        var index = currentObj.from.indexOf(objectId_db);
        if (index > -1) {
            currentObj.from.splice(index, 1);
        }
    } else if (source === 'to') {
        var index = currentObj.to.indexOf(objectId_db);
        if (index > -1) {
            currentObj.to.splice(index, 1);
        }
    } else if (source === 'app') {
        var index = currentObj.app.indexOf(objectId_db);
        if (index > -1) {
            currentObj.app.splice(index, 1);
        }
    }

    $.post('/ajax/objectdata/', {
        configid: currentObj.configid,
        objectid: objectId_db,
        source: source,
        action: action,
    })

    .done(function(response) {
        if (response.error != null) {
            alert('YAML build failed because of the following error:\n\n'
                + JSON.parse(response.error)
            )
        }
        $('#yamlcontainer').html(response.yamlconfig);
        if (currentObjIsEmpty(currentObj)) {
            $('#yamlcard').addClass('d-none');
        }

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