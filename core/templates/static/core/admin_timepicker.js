document.addEventListener("DOMContentLoaded", () => {
  const timeInputs = document.querySelectorAll("input.vTimeField");
  timeInputs.forEach((input) => {
    input.setAttribute("type", "time");
    input.step = 1;
  });
});
