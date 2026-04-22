async function addTask() {
const input = document.getElementById("taskInput");
const task = input.value;

if (!task) return;

const response = await fetch("/add", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ task: task })
});

const data = await response.json();

const list = document.getElementById("taskList");
const li = document.createElement("li");
li.textContent = data.task;
list.appendChild(li);

input.value = "";
}
