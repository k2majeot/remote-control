const config = await fetch("/config.json").then((res) => res.json());

const socket = new WebSocket(
  `ws://${config.network.host}:${config.network.remote_port}`
);
const inputBox = document.getElementById("input-box");
const keyboardInput = document.getElementById("keyboard-input");
const scrollBar = document.getElementById("scroll-bar");
const throttleMs = config.settings.throttle_ms;
const scrollBarSensitivity = config.settings.scrollbar_sensitivity || 1;
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
let dragging = false;
let lastSent = 0;
let touchCount = 0;
let isScrolling = false;
let scrollLastY = null;
let lastScrollSent = 0;

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
  touchCount = event.touches.length;
  const touch = event.touches[0];
  startX = lastX = touch.clientX;
  startY = lastY = touch.clientY;
  if (touchCount >= 2) {
    sendMessage({ type: "down" });
    dragging = true;
  } else {
    dragging = false;
  }
});

inputBox.addEventListener("touchend", (event) => {
  if (event.touches.length < 2 && dragging) {
    sendMessage({ type: "up" });
    dragging = false;
  }
  if (event.touches.length === 0) {
    if (!moved) {
      sendMessage({ type: "press" });
    }
    isTouching = false;
    startX = null;
    startY = null;
    lastX = null;
    lastY = null;
    moved = false;
  }
});

inputBox.addEventListener("touchcancel", (event) => {
  if (dragging) {
    sendMessage({ type: "up" });
  }
  isTouching = false;
  startX = null;
  startY = null;
  lastX = null;
  lastY = null;
  moved = false;
  dragging = false;
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

    if (event.touches.length >= 2 && !dragging) {
      sendMessage({ type: "down" });
      dragging = true;
    } else if (event.touches.length < 2 && dragging) {
      sendMessage({ type: "up" });
      dragging = false;
    }
    lastX = touch.clientX;
    lastY = touch.clientY;

    sendMessage({ type: "move", dx, dy });
  },
  { passive: false }
);

scrollBar.addEventListener("touchstart", (event) => {
  isScrolling = true;
  const touch = event.touches[0];
  scrollLastY = touch.clientY;
});

scrollBar.addEventListener(
  "touchmove",
  (event) => {
    if (!isScrolling || !event.touches.length) return;

    const now = Date.now();
    if (now - lastScrollSent < throttleMs) return;
    lastScrollSent = now;

    const touch = event.touches[0];
    const dy = (touch.clientY - scrollLastY) * scrollBarSensitivity;
    scrollLastY = touch.clientY;

    sendMessage({ type: "scroll", dy });
  },
  { passive: false }
);

scrollBar.addEventListener("touchend", () => {
  isScrolling = false;
  scrollLastY = null;
});

scrollBar.addEventListener("touchcancel", () => {
  isScrolling = false;
  scrollLastY = null;
});
