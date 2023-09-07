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
  var input = document.getElementById("search-input").value.toUpperCase();
  var table = document.getElementsByTagName("table")[0];
  var tr = table.getElementsByTagName("tr");

  // Get the state of each checkbox
  var filterAll = document.getElementById("all-checkbox").checked;
  var filterLabel = document.getElementById("label-checkbox").checked;
  var filterTimestamp = document.getElementById("timestamp-checkbox").checked;
  var filterFirstName = document.getElementById("firstname-checkbox").checked;
  var filterEmail = document.getElementById("email-checkbox").checked;
  var filterPhone = document.getElementById("phone-checkbox").checked;
  var filterOzip = document.getElementById("ozip-checkbox").checked;
  var filterDzip = document.getElementById("dzip-checkbox").checked;
  var filterDcity = document.getElementById("dcity-checkbox").checked;
  var filterDstate = document.getElementById("dstate-checkbox").checked;
  var filterMovesize = document.getElementById("movesize-checkbox").checked;
  var filterMovedate = document.getElementById("movedate-checkbox").checked;
  var filterConversion = document.getElementById("conversion-checkbox").checked;
  var filterValidation = document.getElementById("validation-checkbox").checked;
  var filterNotes = document.getElementById("notes-checkbox").checked;
  var filterGronat = document.getElementById("gronat-checkbox").checked;
  var filterSheets = document.getElementById("sheets-checkbox").checked;
  var filterDuplicate = document.getElementById("duplicate-checkbox").checked;

  // Create array to store unique phone numbers and emails
  var uniqueValues = [];

  for (var i = 0; i < tr.length; i++) {
      var td = tr[i].getElementsByTagName("td");
      if (td.length > 0) {
          var match = false;

          // Filter based on the "All" checkbox
          if (filterAll) {
              for (var j = 0; j < td.length; j++) {
                  if (td[j].textContent.toUpperCase().indexOf(input) > -1) {
                      match = true;
                      break;
                  }
              }
          } else {
              // Filter based on individual checkboxes
              if (filterLabel) match = match || (td[0].textContent.toUpperCase().indexOf(input) > -1);
              if (filterTimestamp) match = match || (td[1].textContent.toUpperCase().indexOf(input) > -1);
              if (filterFirstName) match = match || (td[2].textContent.toUpperCase().indexOf(input) > -1);
              if (filterEmail) match = match || (td[3].textContent.toUpperCase().indexOf(input) > -1);
              if (filterPhone) match = match || (td[4].textContent.toUpperCase().indexOf(input) > -1);
              if (filterOzip) match = match || (td[5].textContent.toUpperCase().indexOf(input) > -1);
              if (filterDzip) match = match || (td[6].textContent.toUpperCase().indexOf(input) > -1);
              if (filterDcity) match = match || (td[7].textContent.toUpperCase().indexOf(input) > -1);
              if (filterDstate) match = match || (td[8].textContent.toUpperCase().indexOf(input) > -1);
              if (filterMovesize) match = match || (td[9].textContent.toUpperCase().indexOf(input) > -1);
              if (filterMovedate) match = match || (td[10].textContent.toUpperCase().indexOf(input) > -1);
              if (filterConversion) match = match || (td[11].textContent.toUpperCase().indexOf(input) > -1);
              if (filterValidation) match = match || (td[12].textContent.toUpperCase().indexOf(input) > -1);
              if (filterNotes) match = match || (td[13].textContent.toUpperCase().indexOf(input) > -1);
              if (filterGronat) match = match || (td[14].textContent.toUpperCase().indexOf(input) > -1);
              if (filterSheets) match = match || (td[15].textContent.toUpperCase().indexOf(input) > -1);
          }

          // Check if duplicate filtering is enabled and filter out duplicates
          if (filterDuplicate) {
              var phone = td[4].textContent;
              var email = td[3].textContent;
              var value = phone || email; // Use either phone or email as the value

              if (value && uniqueValues.includes(value)) {
                  match = false;
              } else {
                  if (value) uniqueValues.push(value);
              }
          }

          if (match) {
              tr[i].style.display = "";
          } else {
              tr[i].style.display = "none";
          }
      }
  }
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