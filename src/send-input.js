const config = await fetch("/config.json").then((res) => res.json());

const socket = new WebSocket(
  `ws://${config.network.host}:${config.network.remote_port}`
);
const inputBox = document.getElementById("input-box");
const keyboardInput = document.getElementById("keyboard-input");
const throttleMs = config.settings.throttle_ms;
const moveThreshold = 5;

inputBox.focus();

function sendMessage(data) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  }
}

let isTouching = false;
let startX = null;
let startY = null;
let lastX = null;
let lastY = null;
let moved = false;
let lastSent = 0;

socket.onopen = () => console.log("WebSocket connected");
socket.onerror = (err) => console.error("WebSocket error", err);

document.getElementById("show-keyboard").addEventListener("click", () => {
  keyboardInput.focus();
});

keyboardInput.addEventListener("keydown", (event) => {
  sendMessage({ type: "key", key: event.key });
});

keyboardInput.addEventListener("blur", () => {
  inputBox.focus();
});

inputBox.addEventListener("touchstart", (event) => {
  isTouching = true;
  moved = false;
  const touch = event.touches[0];
  startX = lastX = touch.clientX;
  startY = lastY = touch.clientY;
});

inputBox.addEventListener("touchend", () => {
  if (!moved) {
    sendMessage({ type: "press" });
  }
  isTouching = false;
  startX = null;
  startY = null;
  lastX = null;
  lastY = null;
  moved = false;
});

inputBox.addEventListener("touchcancel", () => {
  isTouching = false;
  startX = null;
  startY = null;
  lastX = null;
  lastY = null;
  moved = false;
});

inputBox.addEventListener("keydown", (event) => {
  sendMessage({ type: "key", key: event.key });
});

inputBox.addEventListener(
  "touchmove",
  (event) => {
    if (!isTouching || !event.touches.length) return;

    const now = Date.now();
    if (now - lastSent < throttleMs) return;
    lastSent = now;

    const touch = event.touches[0];
    const dx = touch.clientX - lastX;
    const dy = touch.clientY - lastY;
    if (
      Math.abs(touch.clientX - startX) > moveThreshold ||
      Math.abs(touch.clientY - startY) > moveThreshold
    ) {
      moved = true;
    }
    lastX = touch.clientX;
    lastY = touch.clientY;

    sendMessage({ type: "move", dx, dy });
  },
  { passive: false }
);
