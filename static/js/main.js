function makeHttpRequest(url) {

    const Http = new XMLHttpRequest();

    Http.open("GET", url);
    Http.send();

    Http.onreadystatechange = (e) => {
        console.log(Http.responseText);
        window.location.reload();
    }
}


function makeHttpRequestForProximity(url) {

    let proximityValue = !$('#proximityToggle')[0].checked;
    const Http = new XMLHttpRequest();

    Http.open("POST", url);
    Http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    if(proximityValue === true) Http.send("proximity=True");
    else Http.send("proximity=False");
}


function makeHttpRequestAndRedirect(url, urlToRedirect) {

    const Http = new XMLHttpRequest();

    Http.open("GET", url);
    Http.send();

    Http.onreadystatechange = (e) => {
        console.log(Http.responseText);
        window.location.replace(urlToRedirect)
    }
}


let count_checkboxes = 0;

function showShareBtn(id) {

    let secondDevice = $('#secondDevice');
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
    else if(shareBtn.hasClass("invisible") && count_checkboxes >= 1 && secondDevice.hasClass("connected")) shareBtn.removeClass("invisible");

    console.log(count_checkboxes);
}


function shareFolders() {

    let allFolders = $(".checkbox_share");
    let selectedFolders = "";

    for (let i=0; i<allFolders.length; i++) {
        let folderEl = allFolders[i];
        let checkbox = $('#' + folderEl.htmlFor)[0];

        if (checkbox.checked) selectedFolders += folderEl.innerText + ",";

    }

    makeHttpRequest("/share-folders-list?list=" + selectedFolders);
}