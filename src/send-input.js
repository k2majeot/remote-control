const config = await fetch("/config.json").then((res) => res.json());

const socket = new WebSocket(
  `ws://${config.network.host}:${config.network.remote_port}`
);
const inputBox = document.getElementById("input-box");
const scrollBar = document.getElementById("scroll-bar");
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
let twoFingerTap = false;
let twoFingerPositions = [];

let scrollBarActive = false;
let scrollBarLastY = null;

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

scrollBar.addEventListener("touchstart", (event) => {
  scrollBarActive = true;
  scrollBarLastY = event.touches[0].clientY;
  event.preventDefault();
});

scrollBar.addEventListener("touchmove", (event) => {
  if (!scrollBarActive) return;
  const touch = event.touches[0];
  const dy = (touch.clientY - scrollBarLastY) * scrollSensitivity;
  scrollBarLastY = touch.clientY;
  sendMessage({ type: "scroll", dy });
  event.preventDefault();
});

scrollBar.addEventListener("touchend", () => {
  scrollBarActive = false;
  scrollBarLastY = null;
});

scrollBar.addEventListener("touchcancel", () => {
  scrollBarActive = false;
  scrollBarLastY = null;
});

scrollBar.addEventListener("mousedown", (event) => {
  scrollBarActive = true;
  scrollBarLastY = event.clientY;
  event.preventDefault();
});

document.addEventListener("mousemove", (event) => {
  if (!scrollBarActive) return;
  const dy = (event.clientY - scrollBarLastY) * scrollSensitivity;
  scrollBarLastY = event.clientY;
  sendMessage({ type: "scroll", dy });
});

document.addEventListener("mouseup", () => {
  scrollBarActive = false;
  scrollBarLastY = null;
});

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
    twoFingerTap = true;
    twoFingerPositions = Array.from(event.touches).slice(0, 2).map((t) => ({
      x: t.clientX,
      y: t.clientY,
    }));
  } else {
    twoFingerTap = false;
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

  if (twoFingerTap && event.touches.length === 0) {
    sendMessage({ type: "right_press" });
    twoFingerTap = false;
    isTouching = false;
    startX = startY = lastX = lastY = null;
    moved = false;
    return;
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
  twoFingerTap = false;
  startX = startY = lastX = lastY = null;
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

    if (twoFingerTap && event.touches.length >= 2) {
      const t1 = event.touches[0];
      const t2 = event.touches[1];
      if (
        Math.abs(t1.clientX - twoFingerPositions[0].x) > moveThreshold ||
        Math.abs(t1.clientY - twoFingerPositions[0].y) > moveThreshold ||
        Math.abs(t2.clientX - twoFingerPositions[1].x) > moveThreshold ||
        Math.abs(t2.clientY - twoFingerPositions[1].y) > moveThreshold
      ) {
        twoFingerTap = false;
      }
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


