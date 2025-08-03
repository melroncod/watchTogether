// client/web/app.js

// 1) WebSocket
const protocol = location.protocol === "https:" ? "wss" : "ws";
const ws       = new WebSocket(`${protocol}://${location.host}/ws`);

// DOM-элементы
const video       = document.getElementById("video");
const ytContainer = document.getElementById("ytPlayer");
const mediaList   = document.getElementById("mediaList");
const urlInput    = document.getElementById("urlInput");
const loadBtn     = document.getElementById("load");
const playBtn     = document.getElementById("play");
const pauseBtn    = document.getElementById("pause");
const syncBtn     = document.getElementById("sync");
const messagesEl  = document.getElementById("messages");
const chatUser    = document.getElementById("chatUser");
const chatText    = document.getElementById("chatText");
const chatSend    = document.getElementById("chatSend");

let ytPlayer = null;
let ytPoll   = null;

// 2) Загрузка списка локальных видео
fetch("/media/list")
  .then(r => r.json())
  .then(files => {
    mediaList.innerHTML = `<option value="" selected>— введите или выберите —</option>`;
    if (files.length === 0) {
      mediaList.innerHTML += `<option disabled>Нет файлов</option>`;
    } else {
      files.forEach(fn => {
        const o = document.createElement("option");
        o.value = o.textContent = fn;
        mediaList.append(o);
      });
    }
  })
  .catch(e => {
    console.error("media/list failed:", e);
    mediaList.innerHTML = `<option disabled>Ошибка</option>`;
  });

// 3) YouTube-хелперы
function extractYTId(url) {
  const m = url.match(/(?:youtu\.be\/|youtube\.com\/.*v=)([\w-]{11})/);
  return m ? m[1] : null;
}
function cleanupPlayers() {
  // Локальный плеер
  video.pause();
  video.removeAttribute("src");
  video.load();
  // YouTube
  if (ytPlayer) {
    ytPlayer.destroy();
    ytPlayer = null;
  }
  if (ytPoll) {
    clearInterval(ytPoll);
    ytPoll = null;
  }
}
function createYT(id) {
  ytContainer.innerHTML = "";
  return new YT.Player("ytPlayer", {
    height: "450", width: "800", videoId: id,
    playerVars: { autoplay: 0, controls: 1 },
    events: {
      onReady: e => {
        // polling для seek
        let last = e.target.getCurrentTime();
        ytPoll = setInterval(() => {
          const now = e.target.getCurrentTime();
          if (Math.abs(now - last) > 1) {
            ws.send(JSON.stringify({ type: "seek", time: now }));
          }
          last = now;
        }, 500);
      },
      onStateChange: e => {
        if (e.data === YT.PlayerState.PLAYING) {
          ws.send(JSON.stringify({ type: "play" }));
        }
        if (e.data === YT.PlayerState.PAUSED) {
          ws.send(JSON.stringify({ type: "pause" }));
        }
      }
    }
  });
}

// 4) Load
loadBtn.addEventListener("click", () => {
  const custom    = urlInput.value.trim();
  const selection = mediaList.value;
  let url = "";
  if (custom) url = custom;
  else if (selection) url = selection;
  else return;
  ws.send(JSON.stringify({ type: "load", url }));
});

// 5) Play / Pause
playBtn.addEventListener("click",  () => ws.send(JSON.stringify({ type: "play" })));
pauseBtn.addEventListener("click", () => ws.send(JSON.stringify({ type: "pause" })));

// 6) Sync
syncBtn.addEventListener("click", () => {
  const t = ytPlayer ? ytPlayer.getCurrentTime() : video.currentTime;
  ws.send(JSON.stringify({ type: "sync", time: t }));
});

// 7) Local video timeupdate
video.addEventListener("timeupdate", () => {
  ws.send(JSON.stringify({ type: "time_update", time: video.currentTime }));
});

// 8) Chat send
chatSend.addEventListener("click", () => {
  const user = chatUser.value.trim() || "Anon";
  const text = chatText.value.trim();
  if (!text) return;
  ws.send(JSON.stringify({ type: "chat", user, text }));
  chatText.value = "";
});

// 9) Обработка входящих сообщений
ws.addEventListener("message", evt => {
  const msg = JSON.parse(evt.data);
  switch (msg.type) {
    case "load":
      cleanupPlayers();
      const ytId = extractYTId(msg.url);
      if (ytId) {
        video.style.display       = "none";
        ytContainer.style.display = "block";
        ytPlayer = createYT(ytId);
      } else {
        ytContainer.style.display = "none";
        video.style.display       = "block";
        video.src = msg.url.startsWith("http")
          ? msg.url
          : `/media/${msg.url}`;
      }
      break;
    case "play":
      if (ytPlayer) ytPlayer.playVideo();
      else video.play();
      break;
    case "pause":
      if (ytPlayer) ytPlayer.pauseVideo();
      else video.pause();
      break;
    case "sync":
      if (ytPlayer) ytPlayer.seekTo(msg.time, true);
      else video.currentTime = msg.time;
      break;
    case "time_update":
      if (!ytPlayer && Math.abs(video.currentTime - msg.time) > 0.5) {
        video.currentTime = msg.time;
      }
      break;
    case "seek":
      if (ytPlayer) ytPlayer.seekTo(msg.time, true);
      else video.currentTime = msg.time;
      break;
    case "chat":
      const div = document.createElement("div");
      div.className = "msg";
      div.textContent = `${msg.user}: ${msg.text}`;
      messagesEl.append(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      break;
  }
});

// 10) Логи WebSocket
ws.addEventListener("error", e => console.error("WS Error:", e));
ws.addEventListener("close", () => console.warn("WS Closed"));
