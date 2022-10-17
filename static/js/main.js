function searchFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchContact");
    filter = input.value.toUpperCase();
    table = document.getElementById("table-tbody");
    tr = table.getElementsByTagName("tr");
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }

$(document).on("click", ".delete-contact-button", function () {
    var contactfName = $(this).data('fname');
    var contactlName = $(this).data('lname');
    var contactID = $(this).data('id');
    document.getElementById("contactName").innerHTML = contactfName + " " + contactlName;
    document.getElementById("confirm-delete-button").setAttribute("href", "/deleteContact/" + contactID);
});

function generateNewPasscode(){
    var val = Math.floor(1000 + Math.random() * 9000);
    var seq = (Math.floor(Math.random() * 10000) + 10000).toString().substring(1);
    document.getElementById("passcode").value = seq;
}

const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
    v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

document.querySelectorAll('th').forEach(th => th.addEventListener('click', (() => {
    const table = th.closest('table');
    Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
        .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
        .forEach(tr => table.appendChild(tr) );
})));

$( document ).ready(function() {
    user_name = $('.user-name').text().slice(1,2);
    $('.user-letter').text(user_name.toUpperCase());
});