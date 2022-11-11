document.getElementById("addIngredientButton").onclick = function() {addIngredient()};

var count = document.getElementById("numOfIngredients").value;
function addIngredient(){
    count++;
    document.getElementById("numOfIngredients").value = count;
    $('form').submit(function(e) {
        e.preventDefault();
    });
    $('#ingredientsList').append('<li class="ingredientItem">' + 
                                    '<input type="text" name="ingredient-' + count + '" placeholder="Enter ingredient..."></input>' + 
                                    '<a class="deleteIngredientButton btn btn-light">' + 
                                        '<i class="fa fa-times" aria-hidden="true"></i>' + 
                                    '</a>' + 
                                  '</li>');
    
}

function submitForm(form){
    form.submit();
}

$(document).on("click", ".deleteIngredientButton", function () {
    const item = this.closest('li');
    count--;
    document.getElementById("numOfIngredients").value = count;
    item.remove();
});




