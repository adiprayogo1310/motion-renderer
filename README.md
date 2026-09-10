# motion-renderer

Render motion graphics (Bang Motion style, single `video/index.html`) ke MP4 via GitHub Actions. VPS cuma trigger.

## Alur

1. Edit `video/index.html` (timeline deterministik, `?t=<detik>` untuk preview frame)
2. (Opsional) upload VO ke `vo/` — wav/mp3/m4a/ogg
3. Trigger: `gh workflow run render -R adiprayogo1310/motion-renderer`
4. Hasil: `out.mp4` di-commit ke root repo oleh actions-bot

## Variabel workflow_dispatch

- `fps` (default 30)
- `mux_vo` — mux audio bila ada di `vo/`
- `retime` — stretch timeline 40s ke durasi VO

## Preview lokal (tanpa render)

Buka `video/index.html?t=3.5` di browser = frame di detik 3.5.
