// var $ = jQuery;


// 'use strict';
// $(document).ready(function(){
//
//     // ===============================================
//     //                  ALERT TYPES
//     // ===============================================
//
//     const ALERT_BLUE = "alert-primary";
//     const ALERT_GREY = "alert-secondary";
//     const ALERT_GREEN = "alert-success";
//     const ALERT_RED = "alert-danger";
//     const ALERT_YELLOW = "alert-warning";
//     const ALERT_TURQUOISE = "alert-info";
//     const ALERT_LIGHT = "alert-light";
//     const ALERT_DARK = "alert-dark";
//
//
//     function triggerAlert(alertType, text) {
//         let div = document.createElement("div");
//         div.classList.add("alert");
//         div.classList.add(alertType);
//         div.classList.add("alert-dismissible");
//
//         let a = document.createElement("a");
//         a.href = "#";
//         a.classList.add("close");
//         a.setAttribute("data-dismiss", "alert");
//         a.setAttribute("aria-label", "close");
//         a.innerHTML = "&times;";
//
//         let textNode = document.createTextNode(text);
//
//         div.appendChild(a);
//         div.appendChild(textNode);
//         document.getElementById("alert-container").appendChild(div);
//     }
//
//     // Trigger alerts here
// });

function makeHttpRequest(url) {

        const Http = new XMLHttpRequest();

        Http.open("GET", url);
        Http.send();

        Http.onreadystatechange = (e) => {
            console.log(Http.responseText);
            window.location.reload();
        }
}

let count_checkboxes = 0;

function showShareBtn(id) {

    let shareBtn = $('#share');
    let checkbox = $('#' + id);

    if(checkbox.hasClass("checked")) {
        checkbox.removeClass("checked");
        count_checkboxes--;
    } else {
        checkbox.addClass("checked");
        count_checkboxes++
    }

    if(count_checkboxes === 0) shareBtn.addClass("invisible");
    else if(count_checkboxes === 1) shareBtn.removeClass("invisible");

    console.log(count_checkboxes);
}