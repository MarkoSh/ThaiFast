# ThaiFast

Тайский с нуля для русскоязычных: звуки, тоны, алфавит, фразы, тренажёры. Сайт — один `index.html` (Tailwind CDN + lucide), работает офлайн. https://thai.dateonymous.com/

ThaiFast — **движок** семейства *Fast: EngFast и SumerFast собираются из его `index.html`, а общие инструменты (офлайн, иконки) лежат здесь, в `tools/`.

## Семейство

| Сайт | Репозиторий | Папка на сервере | Как устроен |
|---|---|---|---|
| ThaiFast | `~/Documents/ThaiFast` | `thai` | исходник движка |
| EngFast | `~/Documents/EngFast` | `eng` | генерируется: `EngFast/tools/build.py` |
| SumerFast | `~/Documents/SumerFast` | `sumer` | генерируется: `SumerFast/tools/gen.py` → `build.py` |
| BrainFast | `~/Documents/BrainFast` | `brain` | самостоятельный `index.html` |
| Meditat.io | `~/Documents/Meditat.io` | `meditatio` | самостоятельный `index.html` |

Домены: `<папка>.dateonymous.com`. Все сайты показывают друг друга в блоке «Другие курсы» (`SITES` в каждом `index.html`; иконки карточек — `GLYPH` или lucide).

## Файлы

```
index.html          весь сайт: разметка, тексты (T), данные, код
audio/<m|f>/*.mp3   озвучка; имя = fnv1a(текст), m — мужской голос, f — женский
favicon*, apple-touch-icon.png   иконки (tools/icons.py)
offline.json, sw.js офлайн-кэш (tools/offline.py), руками не править
tools/
  texts.js          печатает все тайские строки, которые сайт умеет озвучить
  gen_audio.py      озвучка через edge-tts (th-TH Niwat / Premwadee), пропускает готовые файлы; то, что движок читает неверно (ๆ, цифры), подменяет в `tts_text()`
  offline.py        offline.json + копия sw.js для любого сайта семейства
  sw.js             шаблон service worker для всех сайтов — править только здесь
  icons.py          иконки Thai/Eng/Sumer/BrainFast из их глифа или иконки lucide (у Meditat.io своя, ручная)
```

## Как работать

1. Правка движка или дизайна — в `ThaiFast/index.html`, затем пересобрать сестёр:
   `python3 ../EngFast/tools/build.py` и `cd ../SumerFast/tools && python3 gen.py && python3 build.py`.
   `build.py` проверяет каждую точку патча: если правка в ThaiFast сломала якорь, он упадёт — поправьте якорь в `build.py`.
2. Новые фразы — озвучить: `node tools/texts.js > /tmp/t.json && python3 tools/gen_audio.py /tmp/t.json` (нужен `pip install edge-tts`).
3. Перед коммитом: `python3 tools/offline.py .` (EngFast/SumerFast делают это сами при сборке).
4. Коммит в `master`. Выкладка всех сайтов разом — `fastdeploy` (`~/.local/bin`): обновляет offline.json, пушит, делает `git pull` на сервере.

Иконки: `python3 tools/icons.py` (нужны fonttools и ImageMagick). После смены иконки установленное PWA нужно переустановить.

## Контент

Фразы — живой тайский из тайских источников, не учебник для иностранцев; вежливый регистр с ครับ/ค่ะ. Частота идиом — редакторская оценка (это сказано на странице).
