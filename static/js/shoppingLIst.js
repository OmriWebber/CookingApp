$( document ).ready(function() {

    $(document).on("click", ".markDone", function () {
        if (!$(this).closest('li').hasClass('shoppingListChecked')) {
            $(this).closest('li').addClass('shoppingListChecked');
            $(this).removeClass('btn-light');
            $(this).addClass('btn-success');
        } else {
            $(this).closest('li').removeClass('shoppingListChecked');
            $(this).addClass('btn-light');
            $(this).removeClass('btn-success');
        }
    });

});