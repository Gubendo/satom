const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const PUZZLE = typeof window.PUZZLE === "string"
  ? JSON.parse(window.PUZZLE)
  : window.PUZZLE;

const SAVED_WALLS = window.SAVED_WALLS || [];
const GAME_LOCKED = window.GAME_LOCKED;


const GRID_SIZE = PUZZLE.size;   // ex: 8
let CELL = 60;
const PADDING = 20;

const walls = new Set();
let gameLocked = false;

let viewScale = 1;
let viewOffsetX = 0;
let viewOffsetY = 0;

const MIN_ZOOM = 1;
const MAX_ZOOM = 3;

let pointers = new Map();

let pinchStartDist = null;
let pinchStartScale = null;

let lastPanX = null;
let lastPanY = null;

let pinchStartX = null;
let pinchStartY = null;

const submitBtn = document.getElementById("submit-btn");

const horseImg = new Image();
horseImg.src = window.HORSE_SPRITE_URL;

let horseLoaded = false;

horseImg.onload = () => {
  horseLoaded = true;
  draw();
};

const tileImages = {
  grass: new Image(),
  water: new Image(),
  field: new Image(),
  wall: new Image(),
};

tileImages.grass.src = window.TILES.grass;
tileImages.water.src = window.TILES.water;
tileImages.field.src = window.TILES.field;
tileImages.wall.src = window.TILES.wall;

let tilesLoaded = false;
let loadedCount = 0;

const burger = document.getElementById("burger-btn");

burger.addEventListener("touchstart", (e) => {
  e.preventDefault();
  burger.click();
});

Object.values(tileImages).forEach(img => {
  img.onload = () => {
    loadedCount++;
    if (loadedCount === 3) {
      tilesLoaded = true;
      draw();
    }
  };
});

function findHorse() {
  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {
      if (PUZZLE.grid[y][x] === "H") return [x, y];
    }
  }
  throw new Error("Cheval introuvable");
}

const HORSE_POS = findHorse();

function initGame() {
  canvas.width = GRID_SIZE * CELL + PADDING * 2;
  canvas.height = GRID_SIZE * CELL + PADDING * 2;

  for (const [x, y] of SAVED_WALLS || []) {
    walls.add(`${x},${y}`);
  }

  if (GAME_LOCKED) {
    lockGame();
  }
  
  updateTouchAction();

  resizeCanvas();
  draw();
  updateUI();
  ctx.imageSmoothingEnabled = false;
}

function drawGrid() {
  ctx.strokeStyle = "#e6e9ed";
  ctx.lineWidth = 0.5;

  for (let i = 0; i <= GRID_SIZE; i++) {
    const p = PADDING + i * CELL;

    ctx.beginPath();
    ctx.moveTo(PADDING, p);
    ctx.lineTo(PADDING + GRID_SIZE * CELL, p);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(p, PADDING);
    ctx.lineTo(p, PADDING + GRID_SIZE * CELL);
    ctx.stroke();
  }
}

function drawWater() {
  if (!tilesLoaded) return;

  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {
      if (PUZZLE.grid[y][x] !== "W") continue;

      const px = PADDING + x * CELL;
      const py = PADDING + y * CELL;

      ctx.drawImage(tileImages.water, px, py, CELL, CELL);
    }
  }
}

function drawHorse() {
  if (!horseLoaded) return;

  const [hx, hy] = HORSE_POS;

  const px = PADDING + hx * CELL;
  const py = PADDING + hy * CELL;

  const margin = CELL * 0.1;
  const size = CELL - margin * 2;

  ctx.drawImage(
    horseImg,
    px + margin,
    py + margin,
    size,
    size
  );
}

function drawField() {
  if (!tilesLoaded) return;

  const areaCells = computeAreaJS();
  if (!areaCells) return;

  for (const [x, y] of areaCells) {
    const px = PADDING + x * CELL;
    const py = PADDING + y * CELL;

    ctx.drawImage(tileImages.field, px, py, CELL, CELL);
  }
}

function drawGrass() {
  if (!tilesLoaded) return;

  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {

      const px = PADDING + x * CELL;
      const py = PADDING + y * CELL;

      ctx.drawImage(tileImages.grass, px, py, CELL, CELL);
    }
  }
}

function drawWalls() {
  for (const key of walls) {
    const [x, y] = key.split(",").map(Number);
    const px = PADDING + x * CELL;
    const py = PADDING + y * CELL;

    if (tileImages.wall.complete) {
      ctx.drawImage(tileImages.wall, px, py, CELL, CELL);
    } else {
      ctx.fillStyle = "#4a3218";
      ctx.fillRect(px, py, CELL, CELL);
    }
  }
}

function getCellFromMouse(event) {
  const rect = canvas.getBoundingClientRect();

  let x = event.clientX - rect.left;
  let y = event.clientY - rect.top;

  x -= viewOffsetX;
  y -= viewOffsetY;

  x /= viewScale;
  y /= viewScale;

  x -= PADDING;
  y -= PADDING;

  if (x < 0 || y < 0) return null;

  const cx = Math.floor(x / CELL);
  const cy = Math.floor(y / CELL);

  if (cx < 0 || cy < 0 || cx >= GRID_SIZE || cy >= GRID_SIZE) {
    return null;
  }

  return [cx, cy];
}

function drawArea() {
  const areaCells = computeAreaJS();
  if (!areaCells) return;  // pas de zone valide → rien

  //ctx.fillStyle = areaCells.length > 10 ? "rgba(50,200,50,0.4)" : "rgba(200,50,50,0.3)";
  ctx.fillStyle = "rgba(50,200,50,0.4)";

  for (const [x, y] of areaCells) {
    const px = PADDING + x * CELL;
    const py = PADDING + y * CELL;
    ctx.fillRect(px, py, CELL, CELL);
  }
}

function draw() {
  ctx.save();

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.translate(viewOffsetX, viewOffsetY);
  ctx.scale(viewScale, viewScale);

  drawGrass();
  drawWater();
  drawField();
  drawWalls();
  drawGrid();
  drawHorse();

  ctx.restore();
}

draw();

function onCanvasClick(e) {
  if (GAME_LOCKED) return;

  const cell = getCellFromMouse(e);
  if (!cell) return;

  const [x, y] = cell;
  const key = `${x},${y}`;

  // cases non modifiables
  const terrain = PUZZLE.grid[y][x];
  if (terrain !== ".") return;

  // pas sur le cheval
  if (x === HORSE_POS[0] && y === HORSE_POS[1]) return;

  if (walls.has(key)) {
    walls.delete(key);
  } else {
    if (walls.size >= PUZZLE.max_walls) return;
    walls.add(key);
  }

  draw();
  updateUI();
}

canvas.addEventListener("click", onCanvasClick);

function computeAreaJS() {
  const size = GRID_SIZE;
  const grid = PUZZLE.grid;
  const [hx, hy] = HORSE_POS;

  const visited = new Set();
  const stack = [[hx, hy]];
  let enclosed = true;

  const key = (x, y) => `${x},${y}`;

  while (stack.length) {
    const [x, y] = stack.pop();
    const k = key(x, y);
    if (visited.has(k)) continue;
    visited.add(k);

    // si on touche le bord, ce n’est pas fermé
    if (x === 0 || y === 0 || x === size - 1 || y === size - 1) {
      enclosed = false;
    }

    for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1]]) {
      const nx = x + dx;
      const ny = y + dy;
      if (nx < 0 || ny < 0 || nx >= size || ny >= size) continue;
      if (grid[ny][nx] === "W") continue;
      if (walls.has(key(nx, ny))) continue;

      stack.push([nx, ny]);
    }
  }

  if (!enclosed) return null;          // N/A
  return Array.from(visited).map(k => k.split(",").map(Number));
}

function updateAreaDisplay() {
  const areaSpan = document.getElementById("area");
  const areaCells = computeAreaJS();

  if (!areaCells) {
    areaSpan.textContent = "N/A";
  } else {
    areaSpan.textContent = areaCells.length;
  }
}

function updateUI() {
  const areaCells = computeAreaJS();
  updateAreaDisplay();
  const areaSpan = document.getElementById("area");

  if (!areaCells) {
    areaSpan.textContent = "N/A";
    submitBtn.disabled = true;
  } else {
    areaSpan.textContent = areaCells.length;
    submitBtn.disabled = false || GAME_LOCKED;
  }

  submitBtn.classList.toggle("disabled", submitBtn.disabled);

  document.getElementById("walls-left").textContent =
    PUZZLE.max_walls - walls.size;
}

submitBtn.onclick = async () => {
  if (GAME_LOCKED) return;

  updateUI();
  const areaCells = computeAreaJS();
  if (!areaCells) return;

  const payload = {
    puzzle_id: PUZZLE.id,
    area: areaCells.length,
    walls: Array.from(walls).map(k => k.split(",").map(Number))
  };

  const res = await fetch("/paturage/submit/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  lockGame();

  updateLeaderboard(data.leaderboard_json);
};

function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    ?.split("=")[1];
}

function lockGame() {
  gameLocked = true;

  disableCanvasInteraction();

  submitBtn.disabled = true;

  canvas.classList.add("locked");
}

function disableCanvasInteraction() {
  canvas.style.cursor = "default";

  canvas.removeEventListener("click", onCanvasClick);
  //canvas.removeEventListener("mousemove", onCanvasHover);

}

function resizeCanvas() {
  const ratio = window.devicePixelRatio || 1;

  const wrapper = document.querySelector(".board-wrapper");
  const n = PUZZLE.size;

  const available = wrapper.clientWidth;

  CELL = Math.floor(available / n);

  const sizeCSS = CELL * n + PADDING * 2;

  canvas.width = sizeCSS * ratio;
  canvas.height = sizeCSS * ratio;

  canvas.style.width = sizeCSS + "px";
  canvas.style.height = sizeCSS + "px";

  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  updateTouchAction();

}

window.addEventListener("resize", () => {
  resizeCanvas();
  draw();
});

window.addEventListener("load", () => {
  resizeCanvas();
  draw();
});

function updateLeaderboard(entries) {

  // 🔹 convertir si nécessaire
  if (typeof entries === "string") {
    try {
      entries = JSON.parse(entries);
    } catch (e) {
      console.error("Leaderboard JSON invalide :", entries);
      entries = [];
    }
  }

  if (!Array.isArray(entries)) {
    console.error("Leaderboard n'est pas une liste :", entries);
    return;
  }

  const list = document.getElementById("classement");
  const noScoreMsg = document.getElementById("no-score-message");
  if (!list || !noScoreMsg) return;

  // 🔹 aucun score
  if (entries.length === 0) {
    noScoreMsg.classList.remove("hidden", "fade-out");
    list.classList.add("hidden");
    list.innerHTML = "";
    return;
  }

  // 🔹 il y a des scores
  noScoreMsg.classList.add("fade-out");
  setTimeout(() => {
    noScoreMsg.classList.add("hidden");
    list.classList.remove("hidden");
  }, 300);

  list.innerHTML = "";

  entries.forEach((entry, index) => {
  const li = document.createElement("li");

  if (gameLocked) {

    if (entry.area === 1) {
      li.textContent = `${entry.username} - ${entry.area} point (${entry.walls} murs)`;
    } else {
      li.textContent = `${entry.username} - ${entry.area} points (${entry.walls} murs)`;
    }

  } else {

    li.textContent = `${entry.username} - ??? points`;

  }

  if (entry.first_finisher) {
    const badge = document.createElement("span");
    badge.textContent = "⚡";
    badge.classList.add("badge-first");
    li.appendChild(badge);
    li.appendChild(document.createTextNode(" "));
  }

  if (entry.me) li.classList.add("me", "animate-in");

  list.appendChild(li);
});
}

function initPuzzleMenu() {

  const btn = document.getElementById("burger-btn");
  const drawer = document.getElementById("puzzle-drawer");

  btn.addEventListener("click", () => {
    drawer.classList.toggle("open");
  });

  loadPuzzleList();
  document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        drawer.classList.remove("open");
      }
    });

    document.addEventListener("click", (e) => {
      if (!drawer.contains(e.target) && e.target !== btn) {
        drawer.classList.remove("open");
      }
    });
}

async function loadPuzzleList() {
  const ul = document.getElementById("puzzle-list");

  const response = await fetch(
    `/paturage/api/puzzles/?current_date=${PUZZLE.date}`
  );
  const puzzles = await response.json();

  ul.innerHTML = "";

  puzzles.forEach(p => {
    const li = document.createElement("li");
    li.textContent = p.name + " (" + p.formatted_date + ") " + (p.locked ? " ✅" : "");

    if (p.current) li.classList.add("current-puzzle");
    if (p.locked) li.classList.add("locked-puzzle");

    li.addEventListener("click", () => {
      window.location.search = "?date=" + p.date;
    });

    ul.appendChild(li);
  });
}

function initLeaderboard() {
  const entries = window.LEADERBOARD || [];
  updateLeaderboard(entries);
}


canvas.addEventListener("pointerdown", e => {
  canvas.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId, e);

  if (pointers.size === 1) {
    lastPanX = e.clientX;
    lastPanY = e.clientY;
  }
});

canvas.addEventListener("pointerup", e => {
  pointers.delete(e.pointerId);
  pinchStartDist = null;
  pinchStartScale = null;
  lastPanX = null;
  lastPanY = null;
});

canvas.addEventListener("pointercancel", e => {
  pointers.delete(e.pointerId);
  pinchStartDist = null;
  pinchStartScale = null;
  lastPanX = null;
  lastPanY = null;
});

function handlePan(e) {
  if (lastPanX === null) return;

  const dx = e.clientX - lastPanX;
  const dy = e.clientY - lastPanY;

  viewOffsetX += dx;
  viewOffsetY += dy;

  lastPanX = e.clientX;
  lastPanY = e.clientY;

  clampPan();
  draw();
}

function handlePinch() {
  const arr = [...pointers.values()];
  const p1 = arr[0];
  const p2 = arr[1];

  const dx = p1.clientX - p2.clientX;
  const dy = p1.clientY - p2.clientY;
  const dist = Math.hypot(dx, dy);

  const pinchX = (p1.clientX + p2.clientX) / 2;
  const pinchY = (p1.clientY + p2.clientY) / 2;

  const rect = canvas.getBoundingClientRect();
  const cx = pinchX - rect.left;
  const cy = pinchY - rect.top;

  if (!pinchStartDist) {
    pinchStartDist = dist;
    pinchStartScale = viewScale;
    pinchStartX = cx;
    pinchStartY = cy;
    return;
  }

  const factor = dist / pinchStartDist;
  const newScale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, pinchStartScale * factor));

  const worldX = (cx - viewOffsetX) / viewScale;
  const worldY = (cy - viewOffsetY) / viewScale;

  viewScale = newScale;

  viewOffsetX = cx - worldX * viewScale;
  viewOffsetY = cy - worldY * viewScale;

  clampPan();
  updateTouchAction();
  draw();
}

function clampPan() {
  const wrapper = document.querySelector(".board-wrapper");
  const n = PUZZLE.size;

  const gridSize = CELL * n;

  const scaled = gridSize * viewScale;

  const visible = canvas.clientWidth;

  const maxOffset = 0;
  const minOffset = visible - scaled;

  viewOffsetX = Math.min(maxOffset, Math.max(minOffset, viewOffsetX));
  viewOffsetY = Math.min(maxOffset, Math.max(minOffset, viewOffsetY));
}

canvas.addEventListener("pointermove", e => {
  if (!pointers.has(e.pointerId)) return;

  pointers.set(e.pointerId, e);

  if (pointers.size === 1) {
    handlePan(e);
  }

  if (pointers.size === 2) {
    handlePinch();
  }
});

function updateTouchAction() {
  if (viewScale === 1) {
    canvas.style.touchAction = "pan-y";
  } else {
    canvas.style.touchAction = "none";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initGame();
  initLeaderboard();
  initPuzzleMenu();
});
