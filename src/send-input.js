const config = await fetch("/config.json").then((res) => res.json());

const socket = new WebSocket(
  `ws://${config.network.host}:${config.network.remote_port}`
);
const inputBox = document.getElementById("input-box");
const keyboardInput = document.getElementById("keyboard-input");
const throttleMs = config.settings.throttle_ms;
const scrollSensitivity = config.settings.scroll_sensitivity || 1;
const pressThreshold = config.settings.press_threshold_ms || 500;
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
let longPressTimer = null;
let lastSent = 0;
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

function getAverageY(touches) {
  let sum = 0;
  for (let i = 0; i < touches.length; i++) sum += touches[i].clientY;
  return sum / touches.length;
}

inputBox.addEventListener("touchstart", (event) => {
  isTouching = true;
  moved = false;
  const touch = event.touches[0];
  startX = lastX = touch.clientX;
  startY = lastY = touch.clientY;
  if (event.touches.length >= 2) {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
    isScrolling = true;
    scrollLastY = getAverageY(event.touches);
  } else {
    isScrolling = false;
    scrollLastY = null;
    longPressTimer = setTimeout(() => {
      sendMessage({ type: "down" });
      dragging = true;
    }, pressThreshold);
  }
});

inputBox.addEventListener("touchend", (event) => {
  if (longPressTimer) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }

  if (isScrolling && event.touches.length < 2) {
    isScrolling = false;
    scrollLastY = null;
  }

  if (!event.touches.length) {
    if (dragging) {
      sendMessage({ type: "up" });
      dragging = false;
    } else if (!moved) {
      sendMessage({ type: "press" });
    }
    isTouching = false;
    startX = startY = lastX = lastY = null;
    moved = false;
  }
});

inputBox.addEventListener("touchcancel", () => {
  if (dragging) {
    sendMessage({ type: "up" });
  }
  if (longPressTimer) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }
  isTouching = false;
  dragging = false;
  isScrolling = false;
  startX = startY = lastX = lastY = null;
  scrollLastY = null;
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

    if (
      Math.abs(touch.clientX - startX) > moveThreshold ||
      Math.abs(touch.clientY - startY) > moveThreshold
    ) {
      moved = true;
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        longPressTimer = null;
      }
    }

    if (!dragging && (isScrolling || event.touches.length >= 2)) {
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        longPressTimer = null;
      }
      isScrolling = true;
      const avgY = getAverageY(event.touches);
      const dy = (avgY - (scrollLastY ?? avgY)) * scrollSensitivity;
      scrollLastY = avgY;
      lastScrollSent = now;
      sendMessage({ type: "scroll", dy });
      return;
    }

    const dx = touch.clientX - lastX;
    const dy = touch.clientY - lastY;
    lastX = touch.clientX;
    lastY = touch.clientY;

    sendMessage({ type: "move", dx, dy });
  },
  { passive: false }
);


