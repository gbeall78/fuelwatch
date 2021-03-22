function search(e) {
    e.preventDefault();
    console.log('e', e);
    var formdata = new FormData(document.getElementById("searchForm"));
    $.ajax({
        method: "POST",
        url: `${$SCRIPT_ROOT}/search`,
        processData: false,
        contentType: false,
        data: formdata,
        success: function(response){
            $("#searchResult").html(response);
        }
    });
}