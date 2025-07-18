
const fileInput = document.getElementById("img-upload");
const fileNameDisplay = document.getElementById("file-name");

fileInput.addEventListener("change", function () {
if (this.files.length > 0) {
  fileNameDisplay.textContent = `Selected: ${this.files[0].name}`;
} else {
  fileNameDisplay.textContent = "No file chosen";
}
});
