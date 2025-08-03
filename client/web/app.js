// Устанавливаем WebSocket-соединение
const ws = new WebSocket(`ws://${location.host}/ws`);

// Элементы страницы
const video     = document.getElementById("video");
const mediaList = document.getElementById("mediaList");
const loadBtn   = document.getElementById("load");
const playBtn   = document.getElementById("play");
const pauseBtn  = document.getElementById("pause");

// 1) При загрузке страницы получаем список файлов из /media/list
fetch("/media/list")
  .then(resp => resp.json())
  .then(files => {
    files.forEach(fn => {
      const opt = document.createElement("option");
      opt.value = fn;
      opt.textContent = fn;
      mediaList.appendChild(opt);
    });
  })
  .catch(err => console.error("Не удалось загрузить список медиа:", err));

// 2) Обработка входящих WebSocket-сообщений
ws.onmessage = evt => {
  const msg = JSON.parse(evt.data);
  switch (msg.type) {
    case "load":
      // Устанавливаем источник видео
      video.src = msg.url.startsWith("http")
        ? msg.url
        : `/media/${msg.url}`;
      break;
    case "play":
      video.play();
      break;
    case "pause":
      video.pause();
      break;
    case "time_update":
      // Если рассинхрон больше 0.5 с, подгоняем
      if (Math.abs(video.currentTime - msg.time) > 0.5) {
        video.currentTime = msg.time;
      }
      break;
    case "seek":
      video.currentTime = msg.time;
      break;
    default:
      console.warn("Неизвестный тип сообщения:", msg.type);
  }
};

// 3) Отправка команд при нажатии кнопок
loadBtn.onclick = () => {
  const fn = mediaList.value;
  if (!fn) return;
  ws.send(JSON.stringify({ type: "load", url: fn }));
};

playBtn.onclick = () => {
  ws.send(JSON.stringify({ type: "play" }));
};

pauseBtn.onclick = () => {
  ws.send(JSON.stringify({ type: "pause" }));
};

// 4) При изменении времени воспроизведения отправляем обновление на сервер
video.ontimeupdate = () => {
  ws.send(JSON.stringify({
    type: "time_update",
    time: video.currentTime
  }));
};

// 5) Обработка ошибок соединения
ws.onerror = err => console.error("WebSocket error:", err);
ws.onclose = () => console.warn("WebSocket закрыт");
