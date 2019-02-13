
/*
* Run on page load
*/
$(window).on('load', function() {
    // generate an initial configuration id
    var newID = uuidv4();
    currentObj['policyid'] = newID;
});

/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    $("button#create-object-save").click(function() { createObject() });

    // use .on 'click' with parent selected to recognize events also on
    // dynamically added items
    $('#search-forms').on('click', '.search-results-item', function() {
        var objtype = this.id.split("_", 3).pop()

        resetSearch(this)

        if (objtype === 'address' || objtype === 'addrset') {
            const policyAddrObject = new PolicyAddrObject(this)
            var valid = policyAddrObject.validate_policy_logic()
            if (valid === true) {
                policyAddrObject.ajax_add_address_to_policy_yaml()
                policyAddrObject.blend_in_zone()
                policyAddrObject.add_object_to_list()
            } else {
                return;
            }
        } else if (objtype === 'application' || objtype === 'appset') {
            const policyAppObject = new PolicyAppObject(this)
            var valid = policyAppObject.validate_application_use()
            if (valid === true) {
                policyAppObject.ajax_add_application_to_policy_yaml()
                policyAppObject.add_object_to_list()
            } else {
                return;
            }
        }
    })

    $('.list-group').on('click', '.lgi-icon-close', function() { deleteObject(this) });

    $('#create-object-dropdown a').on('click', function () { createInputForm(this) });
    $('#adrset-form-control-zone').on('click', function() { filterObjects(this) });

    $('#add-policy').on('click', function() { addPolicy() });
    $('#clear-config').on('click', function() { window.location.replace('/load') });
    $('#check-config').on('click', function() { checkConfig() });
    $('#deploy-config').on('click', function() { deployConfig() });
    $('#edit-yaml').on('click', function() { editYaml() });

    $('#output-close').on('click', function() { $('#output-modal').modal('toggle')});

    $('[data-toggle="tooltip"]').tooltip()

});


class PolicyAddrObject {
    constructor(search_result_item) {
        this.objtype = search_result_item.id.split("_", 3).pop()
        this.objectid = search_result_item.id.split("_", 2).pop()
        this.direction = search_result_item.id.split("_").shift()
        this.name = $(search_result_item).find('.obj-name').html()
        this.val = $(search_result_item).find('.obj-val').html()
        this.zone = $(search_result_item).find('.obj-zone').html()
    }

    validate_policy_logic() {
        var errorDifferent = "Can't use objects from different zones!"
        var errorZone = "Can't use the same zone for source and destination!"
        var errorUsed = "Object already in use!"

        var presentZone = $('#added-zone-body-'+this.direction).html()
        var thisZoneContainerCard = $('#added-zone-'+this.direction)

        if (this.direction === 'from') {
            var otherZone = $('#added-zone-body-to').html()
            var currentObjStack = currentObj.from
        } else if (this.direction === 'to') {
            var otherZone = $('#added-zone-body-from').html()
            var currentObjStack = currentObj.to
        }

        if (this.zone === otherZone) {
            swal(errorZone)
        } else if (!thisZoneContainerCard.hasClass('d-none') &&
                  (this.zone != presentZone)) {
            swal(errorDifferent)
        } else if (currentObjStack.includes(this.objectid)) {
            swal(errorUsed)
        } else {
            return true;
        }
    }

    blend_in_zone() {
        var thisZoneContainerCard = $('#added-zone-'+this.direction)
        var thisZoneBody = $('#added-zone-body-'+this.direction)

        if (thisZoneContainerCard.hasClass('d-none')) {
            thisZoneContainerCard.removeClass('d-none')
            thisZoneBody.html(this.zone)
        } else {
            return;
        }
    }

    ajax_add_address_to_policy_yaml() {
        $.post('/ajax/add-address-to-policy/', {
            policyid: currentObj.policyid,
            objectid: this.objectid,
            direction: this.direction,
        })
        .done(function(response) {
            if (response.error != null) {
                alert('Policy update failed because of the following error:\n\n'
                    + JSON.parse(response.error)
                )
            }
            updateYaml(response.yamlconfig)
        })

        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    add_object_to_list() {
        console.log(this)

        var addedObj = {
            obj: this,
            container: $('#added-obj-'+this.direction),
            list: $('#added-list-'+this.direction),
            id: this.direction+'_'+this.objectid+'_'+this.objtype+'_'+'_added',
        }

        objectlist_append_html(addedObj)

        if (this.direction === 'from') {
            currentObj.from.push(this.objectid)
        } else if (this.direction === 'to') {
            currentObj.to.push(this.objectid)
        }
    }
}

class PolicyAppObject {
    constructor(search_result_item) {
        this.objectid = search_result_item.id.split("_", 2).pop()
        this.name = $(search_result_item).find('.obj-name').html()
        this.val = $(search_result_item).find('.obj-val').html()
    }

    validate_application_use() {
        if (currentObj.app.includes(this.objectid)) {
            swal("Object already in use!")
        } else {
            return true;
        }
    }

    ajax_add_application_to_policy_yaml() {
        $.post('/ajax/add-application-to-policy/', {
            policyid: currentObj.policyid,
            objectid: this.objectid,
        })
        .done(function(response) {
            if (response.error != null) {
                alert('Policy update failed because of the following error:\n\n'
                    + JSON.parse(response.error)
                )
            }
            updateYaml(response.yamlconfig)
        })
        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    add_object_to_list() {
        console.log(this)

        var addedObj = {
            obj: this,
            container: $('#added-obj-app'),
            list: $('#added-list-app'),
            id: 'app_'+this.objectid+'_'+this.objtype+'_'+'_added',
        }

        objectlist_append_html(addedObj)
        currentObj.app.push(this.objectid)
    }
}


function objectlist_append_html(addedObj) {
    addedObj.container.removeClass('d-none')
    addedObj.list.append(
        `<li class="list-group-item" id="${addedObj.id}">
          <div class="row">
            <div class="col-auto mr-auto lgi-name">${addedObj.obj.name}</div>
            <div class="lgi-icon-close pr-2">
              <button type="button" class="close" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="w-100"></div>
            <div class="col-auto mr-auto lgi-name text-black-50">
              <small>${addedObj.obj.val}</small>
            </div>
          </div>
        </li>`
    )
}


function updateYaml(yamlconfig) {
    $('#yamlcontainer').html(yamlconfig)
    $('#yamlcard').removeClass('d-none')
}


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

        if (Array.isArray(addresses) === true) {
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
        var zone = $("select#address-form-control-zone").val();
        var name = $("input#address-form-control-name").val();
        var value = $("input#address-form-control-ip").val();

        if (zone === 'Choose Zone...' || name === '' || value === '') {
            $('#address-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $('#create-object-modal').modal('toggle');
        $('.spinner-container').fadeIn()

        $.post({
            url: '/ajax/newobject/',
            data: {
                objtype: objtype,
                zone: zone,
                name: name,
                value: value,
            }
        })
        .done(function(response) {
            updateYamlAndReload(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Address Set') {
        var objtype = 'addrset';
        var zone = $("select#adrset-form-control-zone").val();
        var name = $("input#adrset-form-control-name").val();
        var valuelist = $("#adrset-form-control-objects").val();

        if (zone === 'Choose Zone...' || name === '' || valuelist === '') {
            $('#addrset-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $('#create-object-modal').modal('toggle');
        $('.spinner-container').fadeIn()

        $.post({
            url: '/ajax/newobject/',
            data: {
                objtype: objtype,
                zone: zone,
                name: name,
                valuelist: valuelist,
            }
        })
        .done(function(response) {
            updateYamlAndReload(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Application') {
        var objtype = 'application';
        var name = $("input#application-form-control-name").val();
        var port = $("input#application-form-control-port").val();
        var protocol = $("select#application-form-control-protocol").val();

        if (protocol === 'Protocol' || name === '' || port === '') {
            $('#application-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $('#create-object-modal').modal('toggle');
        $('.spinner-container').fadeIn()

        $.post({
            url: '/ajax/newobject/',
            data: {
                objtype: objtype,
                name: name,
                port: port,
                protocol: protocol,
            }
        })
        .done(function(response) {
            updateYamlAndReload(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });

    } else if (selObj === 'Application Set') {
        var objtype = 'appset';
        var name = $("input#appset-form-control-name").val();
        var valuelist = $("#appset-form-control-objects").val();

        if (name === '' || valuelist === '') {
            $('#appset-form-alert').append('<div class="alert alert-info" ' +
              'role="alert" id="field-empty">Please fill all values!</div>')
            return false;
        }

        $('#create-object-modal').modal('toggle');
        $('.spinner-container').fadeIn()

        $.post({
            url: '/ajax/newobject/',
            data: {
                objtype: objtype,
                name: name,
                valuelist: valuelist,
            }
        })
        .done(function(response) {
            updateYamlAndReload(response)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(errorThrown.toString());
        });
    }
}


function updateYamlAndReload(response) {

    // reload specific div of index.html
    $('#search-forms').load('/?param=reloadforms #search-forms');

    $('.spinner-container').fadeOut()

    // update yaml config
    $('#yamlcontainer').html(response.yamlconfig);
    $('#yamlcard').removeClass('d-none');

}


function checkConfig() {

    var ws = new WebSocket(
        'ws://' + window.location.host +
        '/ws/consoleout/');

    var message = ['ansible', '--version']
    var message2 = ['ping', '-c 5', '10.13.0.1']

    ws.onopen = function() {
        ws.send(JSON.stringify({
            'message': message
        }));
        ws.send(JSON.stringify({
            'message': message2
        }));
    }

    ws.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        ol = document.querySelector('#output-log')
        ol.value += (message);
        ol.scrollTop = ol.scrollHeight
    };

    ws.onclose = function() {
        console.log('Websocket closed')
    };

}


function deployConfig() {
    swal('geht noch nich')
}

function addPolicy() {
    swal('geht noch nich')
}

function editYaml() {
    swal('geht noch nich')
}

function deleteObject(obj) {
    var listitem = $(obj).parents('.list-group-item').remove();
    var listitemId = $(listitem).attr('id');
    var source = listitemId.split('_').shift();
    var objectId_db = listitemId.split('_', 2).pop();
    var objtype = listitemId.split('_', 3).pop();
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

    console.log(objtype)

    $.post('/ajax/updatepolicy/', {
        policyid: currentObj.policyid,
        objectid: objectId_db,
        objtype: objtype,
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


function resetSearch(item) {
    var searchForm = item.closest('.col-sm').querySelector('.searchform')
    var resultList = item.closest('.list-inline')

    resultList.classList.add('d-none')
    searchForm.value = ''
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
    if (i === 0) {
        return true;
    } else {
        return false;
    }
}