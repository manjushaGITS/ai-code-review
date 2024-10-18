function GREETMASTERFirst(name) {
  var greeting = "Hello, " + name + "!";
  return greeting;
}
GREETMASTERFirst();

function renderButton() {
  const buttonElement = document.createElement('button');
  buttonElement.textContent = "click here";
  document.body.appendChild(buttonElement);
}
