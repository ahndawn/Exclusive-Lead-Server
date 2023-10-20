$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});

// Table search

function showAllEntries() {
  // Show all entries by removing any applied filters or pagination
  // Redirect to the /table route with the "show_all" query parameter
  window.location.href = "/table?show_all=true";
}


function showTitle(element) {
  alert(element.getAttribute('title'));
}


  function toggleFilterOptions() {
      var filterOptions = document.getElementById("filter-options");
      if (filterOptions.style.display === "none") {
          filterOptions.style.display = "block";
      } else {
          filterOptions.style.display = "none";
      }
  }
  

  function filterTable() {
    var input = document.getElementById("search-input").value;

    var filterCriteria;
    if (document.getElementById("label-checkbox").checked) filterCriteria = "label";
    else if (document.getElementById("timestamp-checkbox").checked) filterCriteria = "timestamp";
    else if (document.getElementById("firstname-checkbox").checked) filterCriteria = "firstname";
    else if (document.getElementById("email-checkbox").checked) filterCriteria = "email";
    else if (document.getElementById("phone-checkbox").checked) filterCriteria = "phone1";
    else if (document.getElementById("ozip-checkbox").checked) filterCriteria = "ozip";
    else if (document.getElementById("dzip-checkbox").checked) filterCriteria = "dzip";
    else if (document.getElementById("dcity-checkbox").checked) filterCriteria = "dcity";
    else if (document.getElementById("dstate-checkbox").checked) filterCriteria = "dstate";
    else if (document.getElementById("movesize-checkbox").checked) filterCriteria = "movesize";
    else if (document.getElementById("movedate-checkbox").checked) filterCriteria = "movedte";
    else if (document.getElementById("conversion-checkbox").checked) filterCriteria = "conversion";
    else if (document.getElementById("validation-checkbox").checked) filterCriteria = "validation";
    else if (document.getElementById("notes-checkbox").checked) filterCriteria = "notes";
    else if (document.getElementById("gronat-checkbox").checked) filterCriteria = "sent_to_gronat";
    else if (document.getElementById("sheets-checkbox").checked) filterCriteria = "sent_to_sheets";
    else if (document.getElementById("moverref-checkbox").checked) filterCriteria = "moverref";

    // Redirect with the filter criteria and input as parameters
    var url = `/table?filter=${filterCriteria}&filter_value=${input}`;
    window.location.href = url;
}

function filterLocalTable() {
    var input = document.getElementById("search-input").value;

    var filterCriteria;
    if (document.getElementById("label-checkbox").checked) filterCriteria = "label";
    else if (document.getElementById("timestamp-checkbox").checked) filterCriteria = "timestamp";
    else if (document.getElementById("firstname-checkbox").checked) filterCriteria = "firstname";
    else if (document.getElementById("email-checkbox").checked) filterCriteria = "email";
    else if (document.getElementById("phone-checkbox").checked) filterCriteria = "phone1";
    else if (document.getElementById("ozip-checkbox").checked) filterCriteria = "ozip";
    else if (document.getElementById("dzip-checkbox").checked) filterCriteria = "dzip";
    else if (document.getElementById("dcity-checkbox").checked) filterCriteria = "dcity";
    else if (document.getElementById("dstate-checkbox").checked) filterCriteria = "dstate";
    else if (document.getElementById("movesize-checkbox").checked) filterCriteria = "movesize";
    else if (document.getElementById("movedate-checkbox").checked) filterCriteria = "movedte";
    else if (document.getElementById("conversion-checkbox").checked) filterCriteria = "conversion";
    else if (document.getElementById("validation-checkbox").checked) filterCriteria = "validation";
    else if (document.getElementById("notes-checkbox").checked) filterCriteria = "notes";
    else if (document.getElementById("gronat-checkbox").checked) filterCriteria = "sent_to_gronat";
    else if (document.getElementById("sheets-checkbox").checked) filterCriteria = "sent_to_sheets";
    else if (document.getElementById("moverref-checkbox").checked) filterCriteria = "moverref";

    // Redirect with the filter criteria and input as parameters
    var url = `/local-table?filter=${filterCriteria}&filter_value=${input}`;
    window.location.href = url;
}


// END TABLE SEARCH


// DOMAINS SETTINGS

var modal = $("#settingsModal");

// Iterate over the settings buttons and add click event listeners
$(".settings-button").click(function() {
    var label = $(this).attr("data-label");

    // Get current domain info from the server
    $.get('/get_domain_info/' + label, function(domainInfo) {
        console.log("Received domain info:", domainInfo);
        // Set the values in the modal form
        $("#labelInput").val(domainInfo.label);
        $("#leadCostInput").val(domainInfo.lead_cost);
        $("#domainInput").val(domainInfo.domain);
        $("#phoneInput").val(domainInfo.d_phone_number);
        $("#sheetInput").val(domainInfo.sheet_id);
        $("#rangeInput").val(domainInfo.sheet_range);
        $("#sendToLeadsAPI").prop('checked', domainInfo.send_to_leads_api == "1");
        $("#sendToGoogleSheet").prop('checked', domainInfo.send_to_google_sheet == "1");
        $("#twilioNumberValidation").prop('checked', domainInfo.twilio_number_validation == "1");
        $("#moverref").val(domainInfo.moverref);
        $("#smsTexting").prop('checked', domainInfo.sms_texting == "1");
        $("#changeMoverRefInput").prop('checked', domainInfo.change_moverref == 1);
    });

    modal.modal('show');
});

$("#settingsForm").submit(function(event) {
    event.preventDefault();

    // Retrieve the form field values
    var label = $("#labelInput").val();
    var domain = $("#domainInput").val();
    var phone = $("#phoneInput").val();
    var sheet_id = $("#sheetInput").val();
    var sheet_range = $("#rangeInput").val();
    var sendToLeadsAPI = $("#sendToLeadsAPI").is(':checked');
    var sendToGoogleSheet = $("#sendToGoogleSheet").is(':checked');
    var twilioNumberValidation = $("#twilioNumberValidation").is(':checked');
    var smsTexting = $("#smsTexting").is(':checked');
    var leadCost = $("#leadCostInput").val();
    var changeMoverRef = $("#changeMoverRefInput").is(':checked');
    var moverref = $("#moverref").val();

    // Perform an AJAX request to update the domain properties on the server
    $.ajax({
        type: "POST",
        url: "/update_domain/" + label,
        data: {
            original_label: label,
            label: label,
            domain: domain,
            phone_number: phone,
            sheet_id: sheet_id,
            sheet_range: sheet_range,
            send_to_leads_api: sendToLeadsAPI ? "1" : "0",
            send_to_google_sheet: sendToGoogleSheet ? "1" : "0",
            twilio_number_validation: twilioNumberValidation ? "1" : "0",
            moverref: moverref,
            sms_texting: smsTexting ? "1" : "0",
            lead_cost: leadCost,
            change_moverref: changeMoverRef ? "1" : "0"
        },
        success: function(response) {
            console.log("Domain settings updated successfully");
            modal.modal('hide');
        },
        error: function(xhr, status, error) {
            console.error("Error updating domain settings:", error);
        }
    });
});

$("#addDomainButton").click(function() {
    $(this).hide();
    $("#addDomainForm").show();
});

$("#cancelButton").click(function() {
    $("#addDomainButton").show();
    $("#addDomainForm").hide();
});

// password reset link popup
$(document).ready(function() {
    $("#reset-link").click(function(e) {
        e.preventDefault();
        $("#forgot-password-form").toggle();
        $("#reset-link").toggle();
        $("#forgot-password-link").toggle();
        $("#loginForm").toggle();
    });
});