function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }

}

function showPosition(position) {
    $.ajax({
        type: "get",
        url: $SCRIPT_ROOT + '/get_location',
        data: {
            lng: position.coords.longitude,
            lat: position.coords.latitude
        },
        success: function(response) {
            console.log(response);
        }
    });
}