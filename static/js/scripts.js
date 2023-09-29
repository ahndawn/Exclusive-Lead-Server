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

    // Redirect with the filter criteria and input as parameters
    var url = `/table?filter=${filterCriteria}&filter_value=${input}`;
    window.location.href = url;
}


// END TABLE SEARCH


// DOMAINS SETTINGS
 // Get the modal
 var modal = document.getElementById("settingsModal");

 // Get the <span> element that closes the modal
 var closeBtn = document.getElementsByClassName("close")[0];

 // Get the form element
 var form = document.getElementById("settingsForm");

 // Iterate over the settings buttons and add click event listeners
 var settingsButtons = document.querySelectorAll(".settings-button");
 settingsButtons.forEach(function (button) {
     button.addEventListener("click", function () {
         var label = this.getAttribute("data-label");

         // Get current domain info from the server
         $.get('/get_domain_info/' + label, function (domainInfo) {
             console.log("Received domain info:", domainInfo);
             // Set the values in the modal form
             document.getElementById("labelInput").value = domainInfo.label;
             document.getElementById("leadCostInput").value = domainInfo.lead_cost;
             document.getElementById("domainInput").value = domainInfo.domain;
             document.getElementById("phoneInput").value = domainInfo.d_phone_number;
             document.getElementById("sendToLeadsAPI").checked = (domainInfo.send_to_leads_api == "1");
             document.getElementById("sendToGoogleSheet").checked = (domainInfo.send_to_google_sheet == "1");
             document.getElementById("twilioNumberValidation").checked = (domainInfo.twilio_number_validation == "1");
             document.getElementById("moverref").value = domainInfo.moverref;
             document.getElementById("smsTexting").checked = (domainInfo.sms_texting == "1");
             document.getElementById("changeMoverRefInput").checked = domainInfo.change_moverref == 1;
         });

         modal.style.display = "block";
     });
 });

 // Close the modal when the close button is clicked
 closeBtn.addEventListener("click", function () {
     modal.style.display = "none";
 });

 // Close the modal when the user clicks outside the modal content
 window.addEventListener("click", function (event) {
     if (event.target == modal) {
         modal.style.display = "none";
     }
 });

 form.addEventListener("submit", function (event) {
    event.preventDefault();

    // Retrieve the form field values
    var label = document.getElementById("labelInput").value;
    var domain = document.getElementById("domainInput").value;
    var phone = document.getElementById("phoneInput").value;
    var sendToLeadsAPI = document.getElementById("sendToLeadsAPI").checked;
    var sendToGoogleSheet = document.getElementById("sendToGoogleSheet").checked;
    var twilioNumberValidation = document.getElementById("twilioNumberValidation").checked;
    var smsTexting = document.getElementById("smsTexting").checked;
    var leadCost = document.getElementById("leadCostInput").value;
    var changeMoverRef = document.getElementById("changeMoverRefInput").checked;
    var moverref = document.getElementById("moverref").value; // Add this line to get the moverref value

    // Perform an AJAX request to update the domain properties on the server
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_domain/" + label, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            // Handle the response if needed
            console.log("Domain settings updated successfully");
            modal.style.display = "none";
        }
    };
    var params =
        "original_label=" +
        encodeURIComponent(label) +
        "&label=" +
        encodeURIComponent(label) +
        "&domain=" +
        encodeURIComponent(domain) +
        "&phone_number=" +
        encodeURIComponent(phone) +
        "&send_to_leads_api=" +
        (sendToLeadsAPI ? "1" : "0") +
        "&send_to_google_sheet=" +
        (sendToGoogleSheet ? "1" : "0") +
        "&twilio_number_validation=" +
        (twilioNumberValidation ? "1" : "0") +
        "&moverref=" + encodeURIComponent(moverref) +
        "&sms_texting=" +
        (smsTexting ? "1" : "0") +
        "&lead_cost=" + 
        encodeURIComponent(leadCost) + 
        "&change_moverref=" + 
        (changeMoverRef ? "1" : "0");
    xhr.send(params);
});

 document.getElementById("addDomainButton").addEventListener("click", function() {
   this.style.display = "none";
   document.getElementById("addDomainForm").style.display = "block";
 });
 document.getElementById("cancelButton").addEventListener("click", function() {
   document.getElementById("addDomainButton").style.display = "block";
   document.getElementById("addDomainForm").style.display = "none";
 });
// END DOMAIN SETTINGS

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