
window.onload = function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                document.getElementById("latitude").value = position.coords.latitude;
                document.getElementById("longitude").value = position.coords.longitude;
            },
            function (error) {
                console.error("Geolocation could not be obtained:", error);
            }
        );
    } else {
        console.warn("Geolocation is not supported in your browser.");
    }
};
