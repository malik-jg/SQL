// var coll = document.getElementsByClassName("collapsible");
// var i;

// for (i = 0; i < coll.length; i++) {
//     coll[i].addEventListener("click", function () {
//         this.classList.toggle("active");
//         var content = this.nextElementSibling;
//         if (content.style.display === "none") {
//             content.style.display = "block";
//         } else {
//             content.style.display = "none";
//         }
//     });
// }

setTimeout(function () {
    $('.flash-messages').fadeOut('fast');
}, 3000);

var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var content = this.nextElementSibling;

        if (content.style.maxHeight) {
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = 0 + "px";
        }
    });
}



// Add event listeners to checkboxes and radio buttons
document.addEventListener("DOMContentLoaded", function () {
    toggleSections();

    var msCheckbox = document.querySelector('input[name="SoughtOptions"][value="MS"]');
    var phdCheckbox = document.querySelector('input[name="SoughtOptions"][value="PHD"]');

    if (msCheckbox) {
        msCheckbox.addEventListener("change", toggleSections);
    }
    if (phdCheckbox) {
        phdCheckbox.addEventListener("change", toggleSections);
    }
});


function toggleSections() {
    var msCheckbox = document.querySelector('input[name="SoughtOptions"][value="MS"]');
    var phdCheckbox = document.querySelector('input[name="SoughtOptions"][value="PHD"]');
    var bachelorSection = document.querySelector('input[name="BS"]');
    var masterSection = document.querySelector('.academicinfodiv4');

    var bachelorPriorDegreeSection = document.querySelector('.academicinfodiv2');

    if (msCheckbox && phdCheckbox && bachelorSection && masterSection && bachelorPriorDegreeSection) {
        if (msCheckbox.checked) {
            bachelorPriorDegreeSection.style.display = 'block';
            // Hide Master Program section in Prior Degrees
            masterSection.style.display = 'none';
        } else if (phdCheckbox.checked) {
            bachelorPriorDegreeSection.style.display = 'block';
            // Show Master Program section in Prior Degrees
            masterSection.style.display = 'block';
        } else {
            bachelorPriorDegreeSection.style.display = 'none';
            // Hide Master Program section in Prior Degrees
            masterSection.style.display = 'none';
        }
    }
}


