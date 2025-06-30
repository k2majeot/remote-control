const config = await fetch("/config.json").then((res) => res.json());
console.log("Config loaded:", config);
const socket = new WebSocket(
  `ws://${config.network.host}:${config.network.remote_port}`
);
const inputBox = document.getElementById("input-box");
const throttleMs = config.settings.throttle_ms;

let isTouching = false;
let lastX = null;
let lastY = null;
let lastSent = 0;

socket.onopen = () => console.log("WebSocket connected");
socket.onerror = (err) => console.error("WebSocket error", err);

inputBox.addEventListener("touchstart", (event) => {
  isTouching = true;
  const touch = event.touches[0];
  lastX = touch.clientX;
  lastY = touch.clientY;
});

inputBox.addEventListener("touchend", () => {
  isTouching = false;
  lastX = null;
  lastY = null;
});

inputBox.addEventListener("touchcancel", () => {
  isTouching = false;
  lastX = null;
  lastY = null;
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
    lastX = touch.clientX;
    lastY = touch.clientY;

    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ dx, dy }));
    }
  },
  { passive: false }
);
