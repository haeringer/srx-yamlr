
var currentObj = {
    policyid: [],
    from: [],
    to: [],
    app: [],
}

/*
* Run on page load
*/
$(window).on('load', function() {
    var newID = generateId()
    currentObj.policyid = newID
})

// Make ajax POST requests work with Django's CSRF protection
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';')
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i])
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(
                                                         name.length + 1))
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) ||
              /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'))
        }
    }
})

/*
* Event listeners etc. - run once DOM is ready
*/
$(function() {

    // Search Forms - use .on 'click' with parent selected to recognize
    // events also on dynamically added items
    $('#search-forms').on('click', '.search-results-item', function() {
        objectSearchHandler(this)
    })
    $('.list-group').on('click', '.lgi-icon-close', function() {
	    var list_item = this.parentNode.parentNode
        listObjectHandler(list_item)
    })

    // Create Object Modal related functions
    $('#create-object-dropdown a').on('click', function () {
        showCreateObjectForm(this)
    })
    $('#adrset-form-control-zone').on('click', function() {
        filterObjects(this)
    })
    $("button#create-object-save").click(function() {
        createObjectHandler()
    })

    // Buttons
    $('#add-policy').on('click', function() {
        addPolicy()
    })
    $('#clear-config').on('click', function() {
        window.location.replace('/load')
    })
    $('#check-config').on('click', function() {
        checkConfig()
    })
    $('#deploy-config').on('click', function() {
        deployConfig()
    })
    $('#edit-yaml').on('click', function() {
        editYaml()
    })

    $('#output-close').on('click', function() {
        $('#output-modal').modal('toggle')
    })

    $('[data-toggle="tooltip"]').tooltip()

})


function objectSearchHandler(htmlObj) {
    var objtype = htmlObj.id.split("_", 3).pop()

    resetSearch(htmlObj)

    if (objtype === 'address' || objtype === 'addrset') {
        const objectSearchAddrObj = new ObjectSearchAddrObj(htmlObj)
        if (objectSearchAddrObj.validate_policy_logic() === true) {
            objectSearchAddrObj.ajax_add_address_to_policy_yaml()
            objectSearchAddrObj.blend_in_zone()
            objectSearchAddrObj.add_object_to_list()
        } else {
            return;
        }
    } else if (objtype === 'application' || objtype === 'appset') {
        const objectSearchAppObj = new ObjectSearchAppObj(htmlObj)
        if (objectSearchAppObj.validate_application_use() === true) {
            objectSearchAppObj.ajax_add_application_to_policy_yaml()
            objectSearchAppObj.add_object_to_list()
        } else {
            return;
        }
    }
}


class ObjectSearchAddrObj {
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
            var objUsed = currentObj.from.includes(this.name)
        } else if (this.direction === 'to') {
            var otherZone = $('#added-zone-body-from').html()
            var objUsed = currentObj.to.includes(this.name)
        }

        if (this.zone === otherZone) {
            swal(errorZone)
        } else if (!thisZoneContainerCard.hasClass('d-none') &&
                  (this.zone != presentZone)) {
            swal(errorDifferent)
        } else if (objUsed === true) {
            swal(errorUsed)
        } else {
            return true;
        }
    }

    blend_in_zone() {
        var zoneContainerCard = $('#added-zone-'+this.direction)
        var zoneBody = $('#added-zone-body-'+this.direction)

        if (zoneContainerCard.hasClass('d-none')) {
            zoneContainerCard.removeClass('d-none').show()
            zoneBody.html(this.zone)
        } else {
            return;
        }
    }

    ajax_add_address_to_policy_yaml() {
        $.post('/ajax/policy-add-address/', {
            policyid: currentObj.policyid,
            direction: this.direction,
            objname: this.name,
            zone: this.zone,
        })
        .done(function(response) {
            check_response_backend_error(response)
            updateYaml(response.yamlconfig)
        })
        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    add_object_to_list() {
        var addedObj = {
            obj: this,
            container: $('#added-obj-'+this.direction),
            list: $('#added-list-'+this.direction),
            id: this.direction+'_'+this.objectid+'_'+this.objtype+'_added',
            zone: this.zone,
        }

        objectlist_append_html(addedObj)

        if (this.direction === 'from') {
            currentObj.from.push(this.name)
        } else if (this.direction === 'to') {
            currentObj.to.push(this.name)
        }
    }
}

class ObjectSearchAppObj {
    constructor(search_result_item) {
        this.objtype = search_result_item.id.split("_", 3).pop()
        this.objectid = search_result_item.id.split("_", 2).pop()
        this.name = $(search_result_item).find('.obj-name').html()
        this.val = $(search_result_item).find('.obj-val').html()
    }

    validate_application_use() {
        if (currentObj.app.includes(this.name)) {
            swal("Object already in use!")
        } else {
            return true;
        }
    }

    ajax_add_application_to_policy_yaml() {
        $.post('/ajax/policy-add-application/', {
            policyid: currentObj.policyid,
            objname: this.name,
        })
        .done(function(response) {
            check_response_backend_error(response)
            updateYaml(response.yamlconfig)
        })
        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    add_object_to_list() {
        var addedObj = {
            obj: this,
            container: $('#added-obj-app'),
            list: $('#added-list-app'),
            id: 'app_'+this.objectid+'_'+this.objtype+'_added',
        }

        objectlist_append_html(addedObj)
        currentObj.app.push(this.name)
    }
}


function listObjectHandler(htmlObj) {
    var objtype = htmlObj.id.split('_', 3).pop()

    if (objtype === 'address' || objtype === 'addrset') {
        const listAddrObj = new ListAddrObj(htmlObj)
        listAddrObj.ajax_delete_address_from_policy_yaml()
        listAddrObj.delete_object_from_list()
    } else if (objtype === 'application' || objtype === 'appset') {
        const listAppObj = new ListAppObj(htmlObj)
        listAppObj.ajax_delete_application_from_policy_yaml()
        listAppObj.delete_object_from_list()
    }
}


class ListAddrObj {
    constructor(list_item) {
        this.obj = list_item
        this.direction = list_item.id.split('_').shift()
        this.name = $(list_item).find('.lgi-name').html()
        this.zone = $(list_item).find('.lgi-zone').html()
    }

    ajax_delete_address_from_policy_yaml() {
        $.post('/ajax/policy-delete-address/', {
            policyid: currentObj.policyid,
            direction: this.direction,
            objname: this.name,
            zone: this.zone,
        })
        .done(function(response) {
            check_response_backend_error(response)
            updateYaml(response.yamlconfig)
        })
        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    delete_object_from_list() {
        var zoneContainerCard = $('#added-zone-'+this.direction)
        var objectContainer = $('#added-obj-'+this.direction)
        var objectList = $('#added-list-'+this.direction)

        $('#'+this.obj.id).remove()

        if (!objectList.has('li').length) {
            objectContainer.addClass('d-none')
            zoneContainerCard.fadeOut('fast')
            setTimeout(function(){
                zoneContainerCard.addClass('d-none')
            }, 200)
        }

        if (this.direction === 'from') {
            var index = currentObj.from.indexOf(this.name)
            if (index > -1) {
                currentObj.from.splice(index, 1)
            }
        } else if (this.direction === 'to') {
            var index = currentObj.to.indexOf(this.name)
            if (index > -1) {
                currentObj.to.splice(index, 1)
            }
        }
    }
}


class ListAppObj {
    constructor(list_item) {
        this.obj = list_item
        this.objectid = list_item.id.split('_', 2).pop()
        this.name = $(list_item).find('.lgi-name').html()
    }

    ajax_delete_application_from_policy_yaml() {
        $.post('/ajax/policy-delete-application/', {
            policyid: currentObj.policyid,
            direction: this.direction,
            objname: this.name,
            zone: this.zone,
        })
        .done(function(response) {
            check_response_backend_error(response)
            updateYaml(response.yamlconfig)
        })
        .fail(function(errorThrown) {
            console.log(errorThrown.toString())
        })
    }

    delete_object_from_list() {
        $('#'+this.obj.id).remove()
        if (!$('#added-list-app').has('li').length) {
            $('#added-obj-app').addClass('d-none')
        }

        var index = currentObj.app.indexOf(this.name);
        if (index > -1) {
            currentObj.app.splice(index, 1);
        }
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
    if (addedObj.zone !== null) {
        $('#'+addedObj.id).find('.lgi-icon-close').after(
            `<div class="d-none lgi-zone">${addedObj.zone}</div>`
        )
    }
    $('#'+addedObj.id).hide().fadeIn('fast')
}


function check_response_backend_error(response) {
    if (response.error != null) {
        alert('Policy update failed because of the following error:\n\n'
            + JSON.parse(response.error)
        )
    }
}


function updateYaml(yamlconfig) {
    $('#yamlcontainer').html(yamlconfig)
    $('#yamlcard').removeClass('d-none')
    if (currentObjIsEmpty(currentObj)) {
        $('#yamlcard').addClass('d-none');
    }
}


function filterObjects(zoneselector) {
    var selectedzone = $(zoneselector).val()

    $.get({
        url: '/ajax/filterobjects/',
        data: { selectedzone: selectedzone },
    })
    .done(function(response) {
        if (response === null) {
            return;
        }
        if (Array.isArray(response.addresses) === true) {
            $('#adrset-form-control-objects').html('')
            $.each(response.addresses, function(key, value) {
                $('#adrset-form-control-objects')
                    .append($('<option class="small">', { value : key })
                    .text(value))
            })
        } else {
            $('#adrset-form-control-objects').html(
                `<option class="small">${ response.addresses }</option>`
            )
        }
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}


function showCreateObjectForm(dropdown) {
    var selectedObj = $(dropdown).text();

    $('#form-container').find('form').addClass('d-none')

    if (selectedObj === 'Address') {
        $('#address-form').removeClass('d-none')
    } else if (selectedObj === 'Address Set') {
        $('#adrset-form').removeClass('d-none')
    } else if (selectedObj === 'Application') {
        $('#application-form').removeClass('d-none')
    } else if (selectedObj === 'Application Set') {
        $('#appset-form').removeClass('d-none')
    }
}


function createObjectHandler() {
    var formContainer = document.getElementById('form-container')
    var forms = formContainer.querySelectorAll('.form-class')
    var formType
    forms.forEach(function(element) {
        if (element.classList.contains('d-none') == false) {
            formType = element.id
        }
    })
    if (formType === 'address-form') {
        createAddress()
    } else if (formType === 'adrset-form') {
        createAddrset()
    } else if (formType === 'application-form') {
        createApplication()
    } else if (formType === 'appset-form') {
        createAppset()
    }
}


function createAddress() {
    var zone = $("select#address-form-control-zone").val()
    var name = $("input#address-form-control-name").val()
    var value = $("input#address-form-control-ip").val()

    if (zone === 'Choose Zone...' || name === '' || value === '') {
        showCreateFormError($('#address-form-alert'))
        return false;
    }
    hideModalAndFadeInSpinner()
    $.post({
        url: '/ajax/object/create/address/',
        data: {
            zone: zone,
            name: name,
            value: value,
        }
    })
    .done(function(response) {
        reloadAndFadeOutSpinner()
        updateYaml(response.yamlconfig)
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}


function createAddrset() {
    var zone = $("select#adrset-form-control-zone").val()
    var name = $("input#adrset-form-control-name").val()
    var valuelist = $("#adrset-form-control-objects").val()

    if (zone === 'Choose Zone...' || name === '' || valuelist === '') {
        showCreateFormError($('#addrset-form-alert'))
        return false;
    }
    hideModalAndFadeInSpinner()
    $.post({
        url: '/ajax/object/create/addrset/',
        data: {
            zone: zone,
            name: name,
            valuelist: valuelist,
        }
    })
    .done(function(response) {
        reloadAndFadeOutSpinner()
        updateYaml(response.yamlconfig)
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}


function createApplication() {
    var name = $("input#application-form-control-name").val()
    var port = $("input#application-form-control-port").val()
    var protocol = $("select#application-form-control-protocol").val()

    if (protocol === 'Protocol' || name === '' || port === '') {
        showCreateFormError($('#application-form-alert'))
        return false;
    }
    hideModalAndFadeInSpinner()
    $.post({
        url: '/ajax/object/create/application/',
        data: {
            name: name,
            port: port,
            protocol: protocol,
        }
    })
    .done(function(response) {
        reloadAndFadeOutSpinner()
        updateYaml(response.yamlconfig)
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}


function createAppset() {
    var name = $("input#appset-form-control-name").val()
    var valuelist = $("#appset-form-control-objects").val()

    if (name === '' || valuelist === '') {
        showCreateFormError($('#appset-form-alert'))
        return false;
    }
    hideModalAndFadeInSpinner()
    $.post({
        url: '/ajax/object/create/appset/',
        data: {
            name: name,
            valuelist: valuelist,
        }
    })
    .done(function(response) {
        reloadAndFadeOutSpinner()
        updateYaml(response.yamlconfig)
    })
    .fail(function(errorThrown) {
        console.log(errorThrown.toString())
    })
}


function hideModalAndFadeInSpinner() {
    $('#create-object-modal').modal('toggle')
    $('.spinner-container').fadeIn('fast')
}

function reloadAndFadeOutSpinner() {
    // reload only specific div of index.html
    $('#search-forms').load('/?param=reloadforms #search-forms');
    $('.spinner-container').fadeOut('fast')
}

function showCreateFormError(element) {
    var temp = document.getElementsByTagName('template')[0]
    var clone = temp.content.cloneNode(true)
    element.append(clone)
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


function objectSearch(e) {
    var input, filter, ul, li, a, a0, a1, i;
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


function generateId() {
    return Math.random().toString(36).substr(2, 9).toUpperCase()
}

/* Check if arrays inside object are empty helper function */
function currentObjIsEmpty(obj) {
    var i = obj.from.length + obj.to.length + obj.app.length
    if (i === 0) {
        return true;
    } else {
        return false;
    }
}