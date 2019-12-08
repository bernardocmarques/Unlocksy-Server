$(document).ready(function(){

    // ===============================================
    //                  ALERT TYPES
    // ===============================================

    // -> alert-primary (blue)
    // -> alert-secondary (grey)
    // -> alert-success (green)
    // -> alert-danger (red)
    // -> alert-warning (yellow)
    // -> alert-info (turquoise)
    // -> alert-light (light)
    // -> alert-dark (dark)


    function triggerAlert(alertType, text) {
        let div = document.createElement("div");
        div.classList.add("alert");
        div.classList.add(alertType);
        div.classList.add("alert-dismissible");

        let a = document.createElement("a");
        a.href = "#";
        a.classList.add("close");
        a.setAttribute("data-dismiss", "alert");
        a.setAttribute("aria-label", "close");
        a.innerHTML = "&times;";

        let textNode = document.createTextNode(text);

        div.appendChild(a);
        div.appendChild(textNode);
        document.body.appendChild(div);
    }

    // Trigger alerts here

});