document.getElementById("addIngredientButton").onclick = function() {addIngredient()};

var count = 0;
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




