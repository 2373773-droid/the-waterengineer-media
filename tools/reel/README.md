# Reel pipeline (Suv tozalash usullari)

1. `timing.py` — put measured phrase start/end times (ffmpeg `silencedetect`) and the spoken text; writes `data.js` (word + caption timings).
2. `reel.html` — canvas animation; scenes in `SCENES`, palette in `P` (part 3 = lavender accent on the teal underwater world).
3. `music.py` — generates a soft ambient pad (`music.wav`), no samples.
4. `frames.py stills <t...>` for preview, `frames.py video silent.mp4` to render (needs `node_modules/@fontsource/inter` next to it and Playwright Chromium).
5. Mix: voice + music with sidechain ducking, `loudnorm=I=-14:TP=-1.5` (see the ffmpeg command in the part 3 commit message).
