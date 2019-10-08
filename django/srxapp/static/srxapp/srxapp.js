var currentPolicy = {
  policyname: [],
  from: [],
  to: [],
  app: [],
}

/*
 * Run on page load
 */
$(window).on("load", function() {
  var url = new URL(window.location.href)

  if (url.search === "") {
    var hostVarFilePath = $("#host-var-file-path").text()
    if (hostVarFilePath === "None") {
      swal("No host_vars file found", "Please configure the file path in the" +
        " settings", "error")
    } else {
      generateNewPolicyName()
      cloneGitRepo()
      createConfigSession()
    }
  } else if (url.search === "?loadpolicy") {
    getExistingPolicyDetails()
    getYamlConfig()
  } else if (url.search === "?addpolicy") {
    generateNewPolicyName()
    getYamlConfig()
  }
})

/*
 * Event listeners etc. - run once DOM is ready
 */
$(function() {
  // Search Forms - use .on 'click' with parent selected to recognize
  // events also on dynamically added items
  $("#search-forms").on("click", ".search-results-item", function() {
    addObjPreBuild(this)
  })
  $(".list-group").on("click", ".lgi-icon-close", function() {
    var list_item = this.parentNode.parentNode
    listObjectHandler(list_item)
  })

  $('#create-object-modal').on('show.bs.modal', function(){
    var modalContentDiv = $("#create-object-modal").find(".modal-content")
    $(modalContentDiv).load("loadcontent/createmodal", function(status, xhr ) {
      if (status === "error") {
        console.log(xhr.status + " " + xhr.statusText)
      }
    })
  })
  $("#create-object-modal").on("click", "#create-object-dropdown a", function() {
    showCreateObjectForm(this)
  })
  $("#create-object-modal").on("click", "#adrset-form-control-zone", function() {
    filterObjects(this)
  })
  $("#create-object-modal").on("click", "button#create-object-save", function() {
    createObjectHandler()
  })

  // Rename Policy Modal
  $("button#rename-policy-save").on("click", function() {
    renamePolicy()
  })
  // Buttons
  $("#rename-policy").on("click", function() {
    renamePolicyFormSetup()
  })
  $("#add-policy").on("click", function() {
    window.location.replace("/srx/?addpolicy")
  })
  $("#clear-config").on("click", function() {
    resetConfigSession()
  })
  $("#write-config").on("click", function() {
    writeYamlConfig(this)
  })
  $("#commit-config").on("click", function() {
    commitConfig(this)
  })
})

function cloneGitRepo() {
  $("#write-config").prop("disabled", true)
  console.log("Cloning Ansible Git repository...")

  $.get("/git/clonerepo/")
    .done(function(response) {
      $("#write-config").prop("disabled", false)
      if (response === "success") {
        console.log("Git clone succeeded")
        getCommitHash()
      } else {
        console.log(response.error)
        swal("Git clone failed", "Please try reloading the window. If the " +
          "problem persists, check the application logs for more information.",
          "error")
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function getCommitHash() {
  var filePath = $("#host-var-file-path").text()
  $.get("/git/commithash/", {
    "file_path": filePath,
  })
    .done(function(response) {
      console.log("Latest commit hash of " + filePath + ": " + response)
      validateCache(response)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function validateCache(srcfile_commithash) {
  $.get("/srx/validatecache/", {
    srcfile_commithash: srcfile_commithash,
  })
    .done(function(response) {
      if (response === "cache_invalid") {
        console.log("Cache is invalid, update needed")
        swal("Cache Update", "Updating cache to latest configuration \
          revision...", "info")
        importObjects(srcfile_commithash)
      } else if (response === "cache_valid") {
        console.log("Cache is up to date")
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function importObjects(srcfile_commithash = null) {
  console.log("Importing config data from YAML...")
  $(".spinner-container").fadeIn()

  $.get("/srx/importobjects/", {
    srcfile_commithash: srcfile_commithash,
  })
    .done(function(response) {
      $(".spinner-container").fadeOut()
      if (response === "success") {
        console.log("Finished importing config data from YAML")
      }
      if (response.error != null) {
        alert(
          "YAML import failed because of the following error:\n\n" +
            JSON.parse(response.error)
        )
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function createConfigSession() {
  $.post("/srx/createconfigsession/")
    .done(function(response) {
      if (response === "cache_loaded") {
        console.log("Config workingset loaded from cache")
      } else if (response === "cache_empty") {
        console.log("Cache is empty, wait for git clone")
        swal("Cache empty, please wait for git clone to finish")
      } else if (response === "config_session_exists") {
        getYamlConfig()
      } else if (response.error != null) {
        alert(JSON.parse(response.error))
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function getYamlConfig() {
  $.get("/srx/getyamlconfig/")
    .done(function(response) {
      check_response_backend_error(response)
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function resetConfigSession() {
  $.post("/srx/resetconfigsession/")
    .done(function(response) {
      console.log(response)
      if (response === 0) {
        window.location.replace("/srx/")
      } else if (response.error != null) {
        alert(JSON.parse(response.error))
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function getExistingPolicyDetails() {
  $.post("/srx/loadpolicy/")
    .done(function(response) {
      loadExistingPolicy(response)
      console.log(response)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function loadExistingPolicy(pe_detail) {
  function addObjFromExistingPolicy(pd, objtype, direction = null) {
    for (var i = 0; i < pd.length; i++) {
      var obj = pd[i]
      obj.type = objtype
      if (direction !== null) {
        obj.direction = direction
      }
      if (Array.isArray(obj.val) === true) {
        obj.val = obj.val.join("<br>")
      }
      addObjExisting(obj)
    }
  }
  addObjFromExistingPolicy(pe_detail.srcaddresses, "address", "from")
  addObjFromExistingPolicy(pe_detail.srcaddrsets, "addrset", "from")
  addObjFromExistingPolicy(pe_detail.destaddresses, "address", "to")
  addObjFromExistingPolicy(pe_detail.destaddrsets, "addrset", "to")
  addObjFromExistingPolicy(pe_detail.applications, "application")
  addObjFromExistingPolicy(pe_detail.appsets, "appset")
  currentPolicy.policyname = pe_detail.pname
}

function addObjExisting(obj) {
  if (obj.type === "address" || obj.type === "addrset") {
    const addrObj = new AddrObj(obj)
    addrObj.blend_in_zone()
    addrObj.add_object_to_list()
  } else if (obj.type === "application" || obj.type === "appset") {
    const appObj = new AppObj(obj)
    appObj.add_object_to_list()
  }
}

function addObjPreBuild(searchResultElement) {
  var searchResultObj = {
    type: searchResultElement.id.split("_", 3).pop(),
    oid: searchResultElement.id.split("_", 2).pop(),
    direction: searchResultElement.id.split("_").shift(),
    name: $(searchResultElement)
      .find(".obj-name")
      .html(),
    val: $(searchResultElement)
      .find(".obj-val")
      .html(),
    zone: $(searchResultElement)
      .find(".obj-zone")
      .html(),
  }

  resetSearch(searchResultElement)
  addObj(searchResultObj, true)
}

function addObj(obj) {
  if (obj.type === "address" || obj.type === "addrset") {
    const addrObj = new AddrObj(obj)
    if (addrObj.validate_policy_logic() === true) {
      addrObj.ajax_add_address_to_policy_yaml()
    }
  } else if (obj.type === "application" || obj.type === "appset") {
    const appObj = new AppObj(obj)
    if (appObj.validate_application_use() === true) {
      appObj.ajax_add_application_to_policy_yaml()
    }
  }
  $("#rename-policy, #add-policy").prop("disabled", false)
}

class AddrObj {
  constructor(obj) {
    this.obj = obj
  }

  validate_policy_logic() {
    var errorDifferent = "Can't use objects from different zones!"
    var errorZone = "Can't use the same zone for source and destination!"
    var errorUsed = "Object already in use!"

    var presentZone = $("#added-zone-body-" + this.obj.direction).html()
    var thisZoneContainerCard = $("#added-zone-" + this.obj.direction)

    if (this.obj.direction === "from") {
      var otherZone = $("#added-zone-body-to").html()
      var objUsed = currentPolicy.from.includes(this.obj.name)
    } else if (this.obj.direction === "to") {
      var otherZone = $("#added-zone-body-from").html()
      var objUsed = currentPolicy.to.includes(this.obj.name)
    }

    if (this.obj.zone === otherZone) {
      swal(errorZone)
    } else if (
      !thisZoneContainerCard.hasClass("d-none") &&
      this.obj.zone != presentZone
    ) {
      swal(errorDifferent)
    } else if (objUsed === true) {
      swal(errorUsed)
    } else {
      return true
    }
  }

  ajax_add_address_to_policy_yaml() {
    var thisParent = this

    $.post("/srx/policy/add/address/", {
      policyname: currentPolicy.policyname,
      direction: this.obj.direction,
      objname: this.obj.name,
      zone: this.obj.zone,
    })
      .done(function(response) {
        if (response !== "p_exists") {
          thisParent.blend_in_zone()
          thisParent.add_object_to_list()
          check_response_backend_error(response)
          updateYamlContainer(response.yamlconfig)
        } else {
          swal({
            title: "Policy already exists",
            text: "Loading the existing policy for editing...",
            icon: "warning",
          }).then(() => {
            window.location.replace("/srx/?loadpolicy")
          })
        }
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  blend_in_zone() {
    var zoneContainerCard = $("#added-zone-" + this.obj.direction)
    var zoneBody = $("#added-zone-body-" + this.obj.direction)

    if (zoneContainerCard.hasClass("d-none")) {
      zoneContainerCard.removeClass("d-none").show()
      zoneBody.html(this.obj.zone)
    } else {
      return
    }
  }

  add_object_to_list() {
    var addedObj = {
      obj: this.obj,
      container: $("#added-obj-" + this.obj.direction),
      list: $("#added-list-" + this.obj.direction),
      id:
        this.obj.direction +
        "_" +
        this.obj.oid +
        "_" +
        this.obj.type +
        "_added",
      zone: this.obj.zone,
    }

    objectlist_append_html(addedObj)

    if (this.obj.direction === "from") {
      currentPolicy.from.push(this.obj.name)
    } else if (this.obj.direction === "to") {
      currentPolicy.to.push(this.obj.name)
    }
  }
}

class AppObj {
  constructor(obj) {
    this.obj = obj
  }

  validate_application_use() {
    if (currentPolicy.app.includes(this.obj.name)) {
      swal("Object already in use!")
    } else {
      return true
    }
  }

  ajax_add_application_to_policy_yaml() {
    var thisParent = this
    $.post("/srx/policy/add/application/", {
      policyname: currentPolicy.policyname,
      objname: this.obj.name,
    })
      .done(function(response) {
        thisParent.add_object_to_list()
        check_response_backend_error(response)
        updateYamlContainer(response.yamlconfig)
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  add_object_to_list() {
    var addedObj = {
      obj: this.obj,
      container: $("#added-obj-app"),
      list: $("#added-list-app"),
      id: "app_" + this.obj.oid + "_" + this.obj.type + "_added",
    }

    objectlist_append_html(addedObj)
    currentPolicy.app.push(this.obj.name)
  }
}

function listObjectHandler(htmlObj) {
  var objtype = htmlObj.id.split("_", 3).pop()

  if (objtype === "address" || objtype === "addrset") {
    const listAddrObj = new ListAddrObj(htmlObj)
    listAddrObj.ajax_delete_address_from_policy_yaml()
    listAddrObj.delete_object_from_list()
  } else if (objtype === "application" || objtype === "appset") {
    const listAppObj = new ListAppObj(htmlObj)
    listAppObj.ajax_delete_application_from_policy_yaml()
    listAppObj.delete_object_from_list()
  }
}

class ListAddrObj {
  constructor(list_item) {
    this.obj = list_item
    this.direction = list_item.id.split("_").shift()
    this.name = $(list_item)
      .find(".lgi-name")
      .html()
    this.zone = $(list_item)
      .find(".lgi-zone")
      .html()
  }

  ajax_delete_address_from_policy_yaml() {
    $.post("/srx/policy/delete/address/", {
      policyname: currentPolicy.policyname,
      direction: this.direction,
      objname: this.name,
      zone: this.zone,
    })
      .done(function(response) {
        check_response_backend_error(response)
        updateYamlContainer(response.yamlconfig)
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  delete_object_from_list() {
    var zoneContainerCard = $("#added-zone-" + this.direction)
    var zoneBody = $("#added-zone-body-" + this.direction)
    var objectContainer = $("#added-obj-" + this.direction)
    var objectList = $("#added-list-" + this.direction)

    $("#" + this.obj.id).remove()

    if (!objectList.has("li").length) {
      objectContainer.addClass("d-none")
      zoneContainerCard.fadeOut("fast")
      setTimeout(function() {
        zoneContainerCard.addClass("d-none")
        zoneBody.html("")
      }, 200)
    }

    if (this.direction === "from") {
      var index = currentPolicy.from.indexOf(this.name)
      if (index > -1) {
        currentPolicy.from.splice(index, 1)
      }
    } else if (this.direction === "to") {
      var index = currentPolicy.to.indexOf(this.name)
      if (index > -1) {
        currentPolicy.to.splice(index, 1)
      }
    }
  }
}

class ListAppObj {
  constructor(list_item) {
    this.obj = list_item
    this.objectid = list_item.id.split("_", 2).pop()
    this.name = $(list_item)
      .find(".lgi-name")
      .html()
  }

  ajax_delete_application_from_policy_yaml() {
    $.post("/srx/policy/delete/application/", {
      policyname: currentPolicy.policyname,
      objname: this.name,
    })
      .done(function(response) {
        check_response_backend_error(response)
        updateYamlContainer(response.yamlconfig)
      })
      .fail(function(errorThrown) {
        console.log(errorThrown.toString())
      })
  }

  delete_object_from_list() {
    $("#" + this.obj.id).remove()
    if (!$("#added-list-app").has("li").length) {
      $("#added-obj-app").addClass("d-none")
    }

    var index = currentPolicy.app.indexOf(this.name)
    if (index > -1) {
      currentPolicy.app.splice(index, 1)
    }
  }
}

function objectlist_append_html(addedObj) {
  addedObj.container.removeClass("d-none")
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
    $("#" + addedObj.id)
      .find(".lgi-icon-close")
      .after(`<div class="d-none lgi-zone">${addedObj.zone}</div>`)
  }
  $("#" + addedObj.id)
    .hide()
    .fadeIn("fast")
}

function check_response_backend_error(response) {
  if (response.error != null) {
    alert(
      "Policy update failed because of the following error:\n\n" +
        JSON.parse(response.error)
    )
  }
}

function updateYamlContainer(yamlconfig) {
  $("#yamlcontainer").html(yamlconfig)
  $("#yamlcard").removeClass("d-none")
  if (yamlconfig === "{}\n") {
    $("#yamlcard").addClass("d-none")
  }
  $("#yamlcard-tab").tab("show")
  $("#diffcard").addClass("d-none")
  $("#commit-config").prop("disabled", true)
}

function updateGitDiff() {
  $.get("/git/diff/")
  .done(function(response) {
    $("#diffcontainer").html("")
    var lines = response.split("\n")
    lines.splice(0, 2)

    for (i = 0; i < lines.length; i++) {
      var el = $("<div>" + lines[i] + "\n" + "</div>")

      $("#diffcontainer").append(el)
      if (lines[i].startsWith("+ ")) {
        el.addClass("custom-diffgreen")
      } else {
        el.addClass("custom-diffgrey")
      }
    }

    $("#diffcard").removeClass("d-none")
    $("#diffcard-tab").tab("show")
  })
  .fail(function(errorThrown) {
    console.log(errorThrown.toString())
  })
}

function filterObjects(zoneselector) {
  var selectedzone = $(zoneselector).val()

  $.get({
    url: "/srx/filterobjects/",
    data: { selectedzone: selectedzone },
  })
    .done(function(response) {
      if (response === null) {
        return
      }
      if (Array.isArray(response.addresses) === true) {
        $("#adrset-form-control-objects").html("")
        $.each(response.addresses, function(key, value) {
          $("#adrset-form-control-objects").append(
            $('<option class="small">', { value: key }).text(value)
          )
        })
      } else {
        $("#adrset-form-control-objects").html(
          `<option class="small">${response.addresses}</option>`
        )
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function showCreateObjectForm(dropdown) {
  var selectedObj = $(dropdown).text()

  $("#create-form-container")
    .find("form")
    .addClass("d-none")

  if (selectedObj === "Address") {
    $("#address-form").removeClass("d-none")
  } else if (selectedObj === "Address Set") {
    $("#adrset-form").removeClass("d-none")
  } else if (selectedObj === "Application") {
    $("#application-form").removeClass("d-none")
  } else if (selectedObj === "Application Set") {
    $("#appset-form").removeClass("d-none")
  }
}

function createObjectHandler() {
  var formContainer = document.getElementById("create-form-container")
  var forms = formContainer.querySelectorAll(".form-class")
  var formType
  forms.forEach(function(element) {
    if (element.classList.contains("d-none") == false) {
      formType = element.id
    }
  })
  if (formType === "address-form") {
    createAddress()
  } else if (formType === "adrset-form") {
    createAddrset()
  } else if (formType === "application-form") {
    createApplication()
  } else if (formType === "appset-form") {
    createAppset()
  }
}

function createAddress() {
  var zone = $("select#address-form-control-zone").val()
  var name = $("input#address-form-control-name").val()
  var value = $("input#address-form-control-ip").val()

  if (zone === "Choose Zone..." || name === "" || value === "") {
    showCreateFormError("address-form-alert", 0)
    return false
  }
  $("#create-object-modal").modal("toggle")
  $.post({
    url: "/srx/object/create/address/",
    data: {
      zone: zone,
      name: name,
      value: value,
    },
  })
    .done(function(response) {
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function createAddrset() {
  var zone = $("select#adrset-form-control-zone").val()
  var name = $("input#adrset-form-control-name").val()
  var valuelist = $("#adrset-form-control-objects").val()

  if (zone === "Choose Zone..." || name === "" || valuelist === "") {
    showCreateFormError("addrset-form-alert", 0)
    return false
  }
  $("#create-object-modal").modal("toggle")
  $.post({
    url: "/srx/object/create/addrset/",
    data: {
      zone: zone,
      name: name,
      valuelist: valuelist,
    },
  })
    .done(function(response) {
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function createApplication() {
  var name = $("input#application-form-control-name").val()
  var port = $("input#application-form-control-port").val()
  var protocol = $("select#application-form-control-protocol").val()

  if (protocol === "Protocol" || name === "" || port === "") {
    showCreateFormError("application-form-alert", 0)
    return false
  }
  $("#create-object-modal").modal("toggle")
  $.post({
    url: "/srx/object/create/application/",
    data: {
      name: name,
      port: port,
      protocol: protocol,
    },
  })
    .done(function(response) {
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function createAppset() {
  var name = $("input#appset-form-control-name").val()
  var valuelist = $("#appset-form-control-objects").val()

  if (name === "" || valuelist === "") {
    showCreateFormError("appset-form-alert", 0)
    return false
  }
  $("#create-object-modal").modal("toggle")
  $.post({
    url: "/srx/object/create/appset/",
    data: {
      name: name,
      valuelist: valuelist,
    },
  })
    .done(function(response) {
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function renamePolicyFormSetup() {
  var policyNameInput = $("#input-policy-name")
  var policyNameModal = $("#rename-policy-modal")

  policyNameInput.val(currentPolicy.policyname)
  policyNameModal.on("shown.bs.modal", function() {
    policyNameInput.focus()
  })
}

function renamePolicy() {
  var previousName = currentPolicy.policyname
  currentPolicy.policyname = $("#input-policy-name").val()
  $("#rename-policy-modal").modal("toggle")

  $.post("/srx/policy/rename/", {
    previousname: previousName,
    policyname: currentPolicy.policyname,
  })
    .done(function(response) {
      check_response_backend_error(response)
      updateYamlContainer(response.yamlconfig)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function writeYamlConfig(writeButton) {
  $(writeButton).prop("disabled", true)
  $(writeButton).html(`<i class="spinner-border spinner-border-sm"></i>`)

  $.post("/srx/writeconfig/")
    .done(function(response) {
      $(writeButton).html(`<i class="fas fa-check"></i>`)
      $(writeButton).prop("disabled", false)
      if (response === "success") {
        updateGitDiff()
        enableCommitButton()
      } else {
        alert(response.error)
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function commitConfig(commitButton) {
  var hostVarFilePath = $("#host-var-file-path").html()

  $(commitButton).prop("disabled", true)
  $(commitButton).html(`<i class="spinner-border spinner-border-sm"></i>`)

  $.post("/git/commitconfig/", {
    host_var_file_path: hostVarFilePath,
  })
    .done(function(response) {
      if (response === "success") {
        $("#diffcard").addClass("d-none")
        $("#yamlcard-tab").tab("show")
        swal({
          title: "Success",
          text: "Configuration has been committed to Git",
          icon: "success",
        }).then(() => {
          window.location.replace("/srx/")
        })
      } else if (response === "unauthorized") {
        swal("Unauthorized", "Please verify your Git token", "error")
      } else {
        alert(
          "Git commit failed because of the following error:\n\n" +
            JSON.parse(response.error)
        )
      }
      $(commitButton).prop("disabled", false)
      $(commitButton).html(`<i class="fas fa-angle-double-right"></i>`)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function enableCommitButton() {
  $.post("/checktoken/gogs/")
    .done(function(response) {
      if (response === true) {
        $("#commit-config").prop("disabled", false)
      } else {
        swal("To commit the change, please set your Git token first")
      }
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}

function showCreateFormError(elementName, templateNumber) {
  var tmplt = document.getElementsByTagName("template")[templateNumber]
  var clone = tmplt.content.cloneNode(true)
  var elementToAppendTo = $("#" + elementName)

  var appendedItems = $("#" + elementName + " div").length
  if (appendedItems === 0) {
    elementToAppendTo.append(clone)
  }
}

function policyObjectSearch(e) {
  var inputEl = document.getElementById(e.id)
  var input = inputEl.value.toUpperCase()
  var ul = document.getElementById(e.id + "-ul")

  var searchType = e.id.split("-").pop()
  var listElement = $("#search-" + searchType + "-ul")

  if (input.length < 1) {
    listElement.html("")
    ul.classList.add("d-none")
    return
  }

  objectSearch(input, searchType, policyObjectSearchCallback)

  function policyObjectSearchCallback(searchResult) {
    listElement.html("")
    ul.classList.remove("d-none")

    for (var i = 0; i < searchResult.length; i++) {
      var obj = searchResult[i]
      var val = obj.val

      if (searchType === "from" || searchType === "to") {
        var addrType = "address"

        if (Array.isArray(val)) {
          addrType = "addrset"
          val = val.join("<br>")
        }
        listElement.append(
         `<li class="search-results-item" id="${ searchType }_${ obj.id }_${ addrType }">
            <div class="row">
              <div class="col-auto mr-auto lgi-name"><a href="#" class="obj-name">${ obj.name }</a></div>
              <div class="d-none obj-zone">${ obj.zone }</div>
              <div class="w-100"></div>
              <div class="col-auto mr-auto lgi-name"><small><a href="#" class="text-black-50 obj-val">${ val }</a></small></div>
            </div>
          </li>`
        )
      } else if (searchType === "app") {
        var applType = "application"

        if (Array.isArray(val)) {
          applType = "appset"
          val = val.join("<br>")
        }
        listElement.append(
         `<li class="search-results-item" id="app_${ obj.id }_${ applType }">
           <div class="row">
             <div class="col-auto mr-auto lgi-name"><a href="#" class="obj-name">${ obj.name }</a></div>
             <div class="w-100"></div>
             <div class="col-auto mr-auto lgi-name"><small><a href="#" class="text-black-50 obj-val">${ val }</a></small></div>
           </div>
         </li>`
         )
       }
    }
  }
}


function objectSearch(input, searchType, callbackFunc) {
  $.get({
    url: "/srx/search/object/",
    data: {
      input: input,
      searchtype: searchType,
    },
  })
    .done(function(response) {
      callbackFunc(response)
    })
    .fail(function(errorThrown) {
      console.log(errorThrown.toString())
    })
}


function resetSearch(item) {
  var searchForm = item.closest(".col-sm").querySelector(".searchform")
  var resultList = item.closest(".list-inline")

  resultList.classList.add("d-none")
  searchForm.value = ""
}

function generateId() {
  return Math.random()
    .toString(36)
    .substr(2, 9)
    .toUpperCase()
}

function generateNewPolicyName() {
  var nameId = generateId()
  currentPolicy.policyname = "allow-" + nameId + "-to-" + nameId
}
