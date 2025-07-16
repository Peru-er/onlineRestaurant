
window.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    flash.style.opacity = '1';
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-10px)';
      setTimeout(() => flash.remove(), 1000);
    }, 4000);
  });
});



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

