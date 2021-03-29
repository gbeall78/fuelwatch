var radius = 5;

function showPosition(position) {

    $.ajax({
        type: "get",
        url: $SCRIPT_ROOT + '/get_location',
        data: {
            lng: position.coords.longitude,
            lat: position.coords.latitude,
            radius: radius
        },
        success: function(response) {
            displayLocationData(response);
        }
    });
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }

}

function displayLocationData(data) {
    $("#todayData").html(data['today']);
    $("#tomorrow").html(data['tomorrow']);
    $("#userSuburb").html(data['suburb']);
}

function updateRadius(e) {
    radius = e.target.value;
    getLocation();
}
