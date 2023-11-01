// Handle edit Pizza groups
document.body.addEventListener('click', function(e) {
    if (e.target.classList.contains('editMain')) {
        // Capture the pizzaID from the button's data-id attribute
        const pizzaID = e.target.getAttribute('data-id');
        const pizzaName = e.target.getAttribute('data-name');
        const pizzaDescription = e.target.getAttribute('data-description');

        // Set the values in the modal
        document.querySelector('#pizzaName').value = pizzaName;
        document.querySelector('#pizzaDescription').value = pizzaDescription;
        // Set the hidden input field's value to the captured pizzaName
        document.querySelector('#pizzaOriginalName').value = pizzaName;

        // Set the hidden input field's value to the captured pizzaID
        document.querySelector('#editPizzaId').value = pizzaID;

        $('#editPizzaModal').modal('show');
    }
});


// handle edit size button
document.body.addEventListener('click', function(e) {
    if (e.target.classList.contains('editSize')) {
        const pizzaID = e.target.getAttribute('data-id');
        const pizzaSize = e.target.getAttribute('data-size');
        const pizzaPrice = e.target.getAttribute('data-price');
        const pizzaPrepTime = e.target.getAttribute('data-preparetime');
        
        document.querySelector('#pizzaID').value = pizzaID;
        document.querySelector('#pizzaSize').value = pizzaSize;
        document.querySelector('#pizzaSizePrice').value = pizzaPrice;
        document.querySelector('#pizzaSizePrepTime').value = pizzaPrepTime;

        $('#editSizeModal').modal('show');
    }
});


// handle edit side offering button
$(document).ready(function() {
    $(".editButtonSO").click(function() {
        // fetch data from table
        let id = $(this).data('id');
        let name = $(this).data('name');
        let description = $(this).data('description');
        let price = $(this).data('price');
        let preparetime = $(this).data('preparetime');
        
        // set data to modal
        $("#editSideOfferingId").val(id);
        $("#editOfferingName").val(name);
        $("#editDescription").val(description);
        $("#editPrice").val(price);
        $("#editPrepareTime").val(preparetime);
        
        // show modal
        $("#editSideOfferingModal").modal('show');
    });
});

// handle delete side offering button
$(document).ready(function() {
    $(".deleteButtonSO").click(function(e) {
        e.preventDefault(); 

        let sideOfferingId = $(this).data('id');
        
        // Using the confirm function to ask the user
        if(confirm("Are you sure you want to delete this side offering?")) {
            // If user clicks "OK", send request to the server to soft delete the sideOffering
            $.post("/deleteSideOffering", { id: sideOfferingId }, function(data) {
                if(data.success) {
                    // Hide or visually alter the sideOffering on success without reloading the page
                    $(`[data-id="${sideOfferingId}"]`).closest('.col-md-3').fadeOut();
                } else {
                    alert("Failed to delete the side offering. Please try again.");
                }
            });
        }
    });
});

// handle edit drink button
$(document).ready(function() {
    $(".editButtonDrink").click(function() {
        // fetch data from table
        let id = $(this).data('id');
        let name = $(this).data('name');
        let description = $(this).data('description');
        let price = $(this).data('price');
        let preparetime = $(this).data('preparetime');
        
        // set data to modal
        $("#editDrinkId").val(id);
        $("#editDrinkName").val(name);
        $("#editDrinkDescription").val(description);
        $("#editDrinkPrice").val(price);
        $("#editDrinkPrepareTime").val(preparetime);
        
        // show modal
        $("#editDrinkModal").modal('show');
    });
});


// handle delete drink button
$(document).ready(function() {
    $(".deleteButtonDrink").click(function(e) {
        e.preventDefault(); 

        let drinkId = $(this).data('id');
        
        if(confirm("Are you sure you want to delete this drink?")) {
            $.post("/deleteDrink", { id: drinkId }, function(data) {
                if(data.success) {
                    $(`[data-id="${drinkId}"]`).closest('.col-md-2').fadeOut();
                } else {
                    alert("Failed to delete the drink. Please try again.");
                }
            });
        }
    });
});


// handle edit topping button
$(document).ready(function() {
    // When clicking the Edit button, display the modal with prefilled values
    $(".editButtonTopping").click(function() {
        let id = $(this).data('id');
        let name = $(this).data('name');
        let description = $(this).data('description');
        let price = $(this).data('price');

        $("#editToppingId").val(id);
        $("#editToppingName").val(name);
        $("#editToppingDescription").val(description);
        $("#editToppingPrice").val(price);

        $("#editToppingModal").modal('show');
    });

    // When submitting the Edit form, send the AJAX request
    $("#editToppingForm").submit(function(e) {
        e.preventDefault();

        let formData = new FormData(this);

        $.ajax({
            type: "POST",
            url: "/editTopping",
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if(response.success) {
                    // Instead of reloading the whole page, just update the card's content
                    let card = $("#topping-" + formData.get('toppingId'));
                    $(".card-title", card).text(formData.get('toppingName'));
                    $(".card-text:eq(0)", card).text(formData.get('description'));
                    $(".card-text:eq(1)", card).text("Price: $" + formData.get('price'));

                    // Close the modal
                    $("#editToppingModal").modal('hide');
                } else {
                    alert("Failed to edit the topping. Please try again.");
                }
            }
        });
    });
});


// handle delete topping button
$(document).ready(function() {
    $(".deleteButtonTopping").click(function(e) {
        e.preventDefault(); 

        let toppingId = $(this).data('id');

        if(confirm("Are you sure you want to delete this topping?")) {
            $.post("/deleteTopping", { id: toppingId }, function(data) {
                if(data.success) {
                    $(`[data-id="${toppingId}"]`).closest('.col-md-2').fadeOut();
                } else {
                    alert("Failed to delete the topping. Please try again.");
                }
            });
        }
    });
});


// Add a event listener to the "Delete selected" button
document.querySelectorAll('.selectPizza, .selectPizzaGroup').forEach(function(checkbox) {
    checkbox.addEventListener('change', checkIfAnyCheckboxIsChecked);
});


// check if any checkbox is checked
function checkIfAnyCheckboxIsChecked() {
    let btn = document.getElementById('deleteSelectedBtn');
    let selectedPizzas = document.querySelectorAll('.selectPizza:checked');
    let selectedPizzaGroups = document.querySelectorAll('.selectPizzaGroup:checked');
    
    // if any checkbox is checked, change the button's style to btn-danger and enable it
    if (selectedPizzas.length > 0 || selectedPizzaGroups.length > 0) {
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-danger');
        btn.removeAttribute('disabled');
    } else {
        // if no checkbox is checked, change the button's style to btn-secondary and disable it
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-secondary');
        btn.setAttribute('disabled', 'disabled');
    }
};

// check if any checkbox is checked when the page is loaded
document.addEventListener('DOMContentLoaded', checkIfAnyCheckboxIsChecked);


document.getElementById('deleteSelectedBtn').addEventListener('click', function() {
    // fetch all selected pizza groups
    let selectedPizzaGroups = document.querySelectorAll('.selectPizzaGroup:checked');
    let pizzaNames = [];
    selectedPizzaGroups.forEach(function(checkbox) {
        pizzaNames.push(checkbox.getAttribute('data-pizza-name'));
    });

    // fetch all selected pizzas
    let selectedPizzas = document.querySelectorAll('.selectPizza:checked');
    let pizzaIds = [];
    selectedPizzas.forEach(function(checkbox) {
        pizzaIds.push(checkbox.getAttribute('data-pizza-id'));
    });

    // send request to server
    fetch('/deletePizzas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pizzaNames: pizzaNames,
            pizzaIds: pizzaIds
        }),
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            // update the page
            location.reload();
        } else {
            // show error message
            alert('Error: ' + data.error);
        }
    });
});


document.querySelectorAll('.selectPizzaGroup').forEach(function(groupCheckbox) {
    groupCheckbox.addEventListener('change', function() {
        let pizzaName = this.getAttribute('data-pizza-name');
        let relatedPizzaCheckboxes = document.querySelectorAll('.selectPizza[data-pizza-name="' + pizzaName + '"]');

        relatedPizzaCheckboxes.forEach(function(pizzaCheckbox) {
            pizzaCheckbox.checked = groupCheckbox.checked; // Set the pizzaCheckbox to the same state as the groupCheckbox
        });

        checkIfAnyCheckboxIsChecked(); // Ensure the delete button state is updated
    });
});


$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});

