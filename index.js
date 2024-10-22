function GREETMASTER(name) {
  var greeting = "Hello, " + name + "!";
  return greeting;
}
GREETMASTER();

function renderButton() {
  const buttonEle = document.createElement('button');
  button.textContent = "click here";
  document.body.appendChild(buttonEle);
}

function postUserData() {
  const data = {
    name: "John Doe",
    email: "john.doe@example.com",
    ssn: "101-000-1010"
  };

  fetch("https://api.example.com/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  }).then(response => {
    if (!response.ok) {
      throw new Error("Network response was not ok " + response.statusText);
    }
    return response.json();
  })
  .then(data => {
    console.log("Success:", data);
  });
}
