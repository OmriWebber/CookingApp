function searchFunction() {
    // Declare variables
    var input, filter, i, recipeTitleValue, recipeCategoryValue, recipeTitle, recipeGrid, recipeGridCards, recipeCategory;
    input = document.getElementById("searchRecipes");
    filter = input.value.toUpperCase();
    recipeGrid = document.getElementById("recipeGrid");
    recipeGridCards = recipeGrid.getElementsByClassName('col-md-4');

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < recipeGridCards.length; i++) {
      recipeTitle = recipeGridCards[i].getElementsByClassName("recipeTitle")[0];
      recipeCategory = recipeGridCards[i].getElementsByClassName("recipeCategory")[0];
      console.log(recipeTitle,recipeCategory);
      if (recipeTitle || recipeCategory) {
        recipeTitleValue = recipeTitle.textContent || recipeTitle.innerText;
        recipeCategoryValue = recipeCategory.textContent || recipeCategory.innerText;
        if (recipeTitleValue.toUpperCase().indexOf(filter) > -1 || recipeCategoryValue.toUpperCase().indexOf(filter) > -1) {
          recipeGridCards[i].style.display = "";
        } else {
          recipeGridCards[i].style.display = "none";
        }
      }
    }
  }

$(document).on("click", ".delete-recipe-button", function () {
    var recipeTitle = $(this).data('title');
    var recipeID = $(this).data('id');
    document.getElementById("recipeTitle").innerHTML = recipeTitle;
    document.getElementById("confirm-delete-button").setAttribute("href", "/deleteRecipe/" + recipeID);
});

// Global Sorting of Tables
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

setTimeout(function() {
  $('#alert').hide();
}, 5000); // <-- time in milliseconds

