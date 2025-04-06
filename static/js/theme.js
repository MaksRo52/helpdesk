document.addEventListener("DOMContentLoaded", function () {
const themeToggle = document.getElementById("themeToggle");

if (localStorage.getItem("theme") === "light") {
  document.body.classList.add("light-theme");
  themeToggle.checked = true;
}

themeToggle.addEventListener("change", function () {
  if (this.checked) {
    document.body.classList.add("light-theme");
    localStorage.setItem("theme", "light");
  } else {
    document.body.classList.remove("light-theme");
    localStorage.setItem("theme", "dark");
  }
});
});

