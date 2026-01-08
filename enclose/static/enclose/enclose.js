const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const PUZZLE = typeof window.PUZZLE === "string"
  ? JSON.parse(window.PUZZLE)
  : window.PUZZLE;

const SAVED_WALLS = window.SAVED_WALLS || [];
const GAME_LOCKED = window.GAME_LOCKED;


const GRID_SIZE = PUZZLE.size;   // ex: 8
const CELL = 60;
const PADDING = 20;

const walls = new Set();
let gameLocked = false;

const submitBtn = document.getElementById("submit-btn");

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

  if (GAME_LOCKED) {
  feedback.textContent = "Solution déjà validée ✔️";
  }
  
  resizeCanvas();
  draw();
  updateUI();
}

function drawGrid() {
  ctx.strokeStyle = "#444";
  ctx.lineWidth = 1;

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

function drawTerrain() {
  for (let y = 0; y < GRID_SIZE; y++) {
    for (let x = 0; x < GRID_SIZE; x++) {
      if (PUZZLE.grid[y][x] !== "W") continue;

      const px = PADDING + x * CELL;
      const py = PADDING + y * CELL;

      ctx.fillStyle = "#6caed6"; // eau
      ctx.fillRect(px, py, CELL, CELL);
    }
  }
}

function drawHorse() {
  const [hx, hy] = HORSE_POS;
  const cx = PADDING + hx * CELL + CELL / 2;
  const cy = PADDING + hy * CELL + CELL / 2;

  ctx.fillStyle = "#111";
  ctx.beginPath();
  ctx.arc(cx, cy, CELL * 0.25, 0, Math.PI * 2);
  ctx.fill();
}

function drawWalls() {
  for (const key of walls) {
    const [x, y] = key.split(",").map(Number);
    const px = PADDING + x * CELL;
    const py = PADDING + y * CELL;

    ctx.fillStyle = "#000";
    ctx.fillRect(px, py, CELL, CELL);
  }
}

function getCellFromMouse(event) {
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left - PADDING;
  const y = event.clientY - rect.top - PADDING;

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
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawArea();
  drawTerrain();
  drawWalls();
  drawGrid();
  drawHorse();
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

  const res = await fetch("/enclose/submit/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  lockGame();

  document.getElementById("feedback").textContent =
    `Score enregistré – rang : ${data.rank}`;
  console.log("test");
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
  document.getElementById("feedback").classList.add("locked");

  canvas.classList.add("locked");
}

function disableCanvasInteraction() {
  canvas.style.cursor = "default";

  canvas.removeEventListener("click", onCanvasClick);
  //canvas.removeEventListener("mousemove", onCanvasHover);

}

function resizeCanvas() {
  const wrapper = document.querySelector(".board-wrapper");
  const size = PUZZLE.size;

  const available = wrapper.clientWidth;

  const cellSize = Math.floor(available / size);
  const canvasSize = cellSize * size;

  canvas.width = canvasSize;
  canvas.height = canvasSize;
}

window.addEventListener("resize", () => {
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

  if (entry.area === 1) {
    li.appendChild(
    document.createTextNode(
      `${entry.username} - ${entry.area} point (${entry.walls} murs) `
    )
  );
  } 
  else {
    li.appendChild(
      document.createTextNode(
        `${entry.username} - ${entry.area} points (${entry.walls} murs) `
      )
  );
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
    `/enclose/api/puzzles/?current_date=${PUZZLE.date}`
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

document.addEventListener("DOMContentLoaded", () => {
  initGame();
  initLeaderboard();
  initPuzzleMenu();
});
