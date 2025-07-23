
window.onload = function () {
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

    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        const lat = document.getElementById("latitude").value;
        const lon = document.getElementById("longitude").value;

        if (!lat || !lon) {
            event.preventDefault();
            alert("Location not available. Please allow geolocation to make a reservation.");
        }
    });
};
