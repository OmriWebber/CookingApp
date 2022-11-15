mobiscroll.setOptions({
    theme: 'ios',
    themeVariant: 'light'
});

$(function () {
    var calendar;
    var popup;
    var oldMeal;
    var tempMeal;
    var deleteMeal;
    var formatDate = mobiscroll.util.datetime.formatDate;
    var $name = $('#meal-name-input');
    var $notes = $('#meal-notes-input');
    var $deleteButton = $('#meal-delete');
    var $types = $('#meal-type-segmented');
    var $addRecipe = $('#addRecipeDiv');
    var $viewRecipe = $('#viewRecipe');

    var types = [{
        id: 1,
        name: 'Breakfast',
        color: '#e20f0f',
        icon: '🍳'
    }, {
        id: 2,
        name: 'Lunch',
        color: '#32a6de',
        icon: '🍜'
    }, {
        id: 3,
        name: 'Dinner',
        color: '#e29d1d',
        icon: '🥙'
    }, {
        id: 4,
        name: 'Snack',
        color: '#68169c',
        icon: '🥨'
    }];

    function addMealPopup() {
        // hide delete button inside add popup
        $deleteButton.hide();
        $addRecipe.show();
        deleteMeal = true;
        restoreMeal = false;

        $viewRecipe.hide();
        // set popup header text and buttons for adding
        popup.setOptions({
            headerText: '<div>Search for Recipe</div><div class="md-meal-type">' +
                formatDate('DDDD, DD MMMM YYYY', new Date(tempMeal.start)) + '</div>',
            buttons: [
                'cancel',
                {
                    text: 'Add',
                    keyCode: 'enter',
                    handler: function () {
                        calendar.updateEvent(tempMeal);

                        deleteMeal = false;
                        popup.close();
                    },
                    cssClass: 'mbsc-popup-button-primary'
                }
            ]
        });


        $('.meal-planner-type').each(function (i, elm) {
            $(elm).mobiscroll('getInst').checked = +elm.value == tempMeal.resource;
        });

        popup.open();
    }

    function editMealPopup(args) {
        var ev = args.event;
        var resource = types.find(function (obj) { return obj.id === ev.resource });

        $addRecipe.show();
        // show delete button inside edit popup
        $deleteButton.show();
        $viewRecipe.hide();

        if(tempMeal.notes) {
            $viewRecipe.show();
            $viewRecipe.attr('href', '/showRecipe/' + tempMeal.notes);
        }

        deleteMeal = false;
        restoreMeal = true;

        // // set popup header text and buttons for editing
        popup.setOptions({
            headerText: '<div>' + resource.name + '</div><div class="md-meal-type">' +
                formatDate('DDDD, DD MMMM YYYY', new Date(ev.start)) + '</div>',
            buttons: [
                'cancel',
                {
                    text: 'Save',
                    keyCode: 'enter',
                    handler: function () {
                        // update event with the new properties on save button click
                        calendar.updateEvent({
                            id: ev.id,
                            title: tempMeal.title,
                            notes: tempMeal.notes,
                            start: ev.start,
                            end: ev.end,
                            resource: tempMeal.resource,
                            allDay: true,
                        });

                        restoreMeal = false;
                        popup.close();
                    },
                    cssClass: 'mbsc-popup-button-primary'
                }
            ]
        });

        // fill popup with the selected event data
        $name.mobiscroll('getInst').value = ev.title || '';
        $notes.mobiscroll('getInst').value = ev.notes || '';

        $('.meal-planner-type').each(function (i, elm) {
            $(elm).mobiscroll('getInst').checked = +elm.value == tempMeal.resource;
        });

        popup.open();
    }

    var calendar = $('#demo-meal-planner').mobiscroll().eventcalendar({
        view: {
            timeline: {
                type: 'week',
                eventList: true
            }
        },
        resources: types,
        dragToCreate: false,
        dragToResize: false,
        dragToMove: true,
        clickToCreate: true,
        extendDefaultEvent: function (ev) {
            return {
                title: 'New Recipe',
                allDay: true
            };
        },
        onEventCreate: function (args, inst) {
            // store temporary event
            tempMeal = args.event;
            setTimeout(function () {
                addMealPopup();
            }, 100);
        },
        onEventClick: function (args, inst) {
            oldMeal = $.extend({}, args.event);
            tempMeal = args.event;

            if (!popup.isVisible()) {
                editMealPopup(args);
            }
        },
        renderResource: function (resource) {
            return '<div class="md-meal-planner-cont">' +
                '<div class="md-meal-planner-title" style="color:' + resource.color + '">' +
                '<span class="md-meal-planner-icon">' + resource.icon + '</span>' + resource.name + '</div>' +
                '</div>';
        },
        renderScheduleEventContent: function (args) {
            var event = args.original;
            return '<div class="md-meal-planner-event">' +
                '<div class="md-meal-planner-event-title">' + event.title + '</div>' +
                '</div>';
        },
    }).mobiscroll('getInst');

    $.getJSON('https://trial.mobiscroll.com/meal-planner/?callback=?', function (events) {
        calendar.setEvents(events);
    }, 'jsonp');


    var popup = $('#meal-planner-popup').mobiscroll().popup({
        display: 'bottom',
        contentPadding: false,
        fullScreen: true,
        onClose: function () {
            if (deleteMeal) {
                calendar.removeEvent(tempMeal);
            } else if (restoreMeal) {
                calendar.updateEvent(oldMeal);
            }
        },
        responsive: {
            medium: {
                display: 'center',
                width: 400,
                fullScreen: false,
                touchUi: false,
                showOverlay: false
            }
        }
    }).mobiscroll('getInst');

    function getTypes() {
        var data = [];

        for (var i = 0; i < types.length; ++i) {
            var type = types[i];
            data.push({
                text: type.name,
                value: type.id
            })
        }
        return data;
    }

    function appendTypes() {
        var segmented = '<div mbsc-segmented-group>';

        for (var i = 0; i < types.length; ++i) {
            var type = types[i];
            segmented += '<label>' + type.name + '<input type="radio" mbsc-segmented name="meal-planner-type" value="' +
                type.id + '" class="meal-planner-type" ' + '/></label>';
        }

        segmented += '</div>';
        $types.append(segmented);
        mobiscroll.enhance($types[0]);
    }

    appendTypes();

    $('.meal-planner-type').on('change', function (ev) {
        tempMeal.resource = +ev.target.value;
    });

    $name.on('change', function (ev) {
        tempMeal.title = ev.target.value;
    });


    $notes.on('change', function (ev) {
        tempMeal.notes = ev.target.value;
    });

    $deleteButton.on('click', function () {
        // delete current event on button click
        calendar.removeEvent(tempMeal);

        // save a local reference to the deleted event
        var deletedMeal = tempMeal;

        popup.close();

        mobiscroll.snackbar({
            button: {
                action: function () {
                    calendar.addEvent(deletedMeal);
                },
                text: 'Undo'
            },
            duration: 10000,
            message: 'Meal deleted'
        });
    });
    
    $(".recipe").click(function(){
        $('#searchResults').find('.row').removeClass('checked');
        $(this).addClass('checked');
        
        var text = $(this).find('p').html();
        $('#meal-name-input')[0].value = text;
        var recipeID = $(this).find('.recipeIdTitle').find('span').text();
        $notes.value = recipeID;

        tempMeal.title = text;
        tempMeal.notes = recipeID;
      });

    $('#meal-name-input').keyup(function(){
        var input,filter,searchResults,searchResultsItems,recipeTitle;
        input = $('#meal-name-input');
        console.log(input[0].value);
        searchResults = document.getElementById("searchResults");
        searchResultsItems = searchResults.getElementsByClassName("recipe");
        filter = input[0].value.toUpperCase();

        for(let i = 0; i < searchResultsItems.length; i++) {
            recipeTitle = searchResultsItems[i].getElementsByClassName("recipeTitle")[0];
            if(recipeTitle.innerHTML.toUpperCase().indexOf(filter) > -1) {
                $(searchResultsItems[i]).show();
            } else {
                $(searchResultsItems[i]).hide();
            }
        }
    });
    
});

