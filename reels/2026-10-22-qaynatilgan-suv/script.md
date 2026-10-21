# Qaynatilgan suv hamma narsadan tozami?

Planned publish: Thursday 2026-10-22, 12:00 Tashkent (16:00 Seoul), Reel + YouTube Short.
Target length: ~50 s (~115 words). Standalone reel (no series/parts, Javohir's decision 2026-10-18).

## Format C — talking head + B-roll on top (decided 2026-10-20)

Javohir is on camera for the whole video.

Layout (1080x1920):
- Top panel, y 0–900: B-roll (Pixabay) + graphics, changes with each sentence.
- Caption band, y ~960–1180: karaoke subtitles on the divider line (CAP_Y 1180 or a bit higher).
- Bottom panel, y 900–1920: Javohir, cropped so his face sits at ~y 1000–1280, which keeps it clear of the YouTube Shorts / Reels bottom UI (y > ~1290). Chest/shoulders under the UI are fine.
- Cover (first frame): full-screen Javohir with "QAYNATILGAN SUV · hamma narsadan tozami?"

### Filming notes for Javohir
- Phone vertical, at eye level, ~1 m away; face + shoulders + a little of the table in frame.
- Leave some headroom above the head; Claude crops it into the bottom panel.
- Hold a glass of water or the kettle (props: kettle, glass).
- Window light in front of the face, plain background.
- DJI Mic Mini via USB-C (Camera → Pro Video → mic icon → USB).
- One take per paragraph is fine; pause 1–2 s between paragraphs (pauses get cut).
- Send the video + the text as actually spoken.

## Narration (for camera) — FINAL (Javohir, 2026-10-21)

[1 · hook, kettle in hand, steam coming out]
Choynakdan bug' chiqdimi? Shoshmang, suv hali qaynamagan.

[2 · real boiling + microbes]
Bug' suv to'liq qaynamasdan oldin ham chiqadi. Haqiqiy qaynash bu suv biqir-biqir qaynaganda bo'ladi. Shu holatda kamida bir daqiqa qaynasa, bakteriya, virus, hatto parazitlar ham nobud bo'ladi. Yaxshi qaynamagan suv ich ketishi va oshqozon-ichak kasalliklariga sabab bo'lishi mumkin. Agar siz ma'lum balandlikda bo'lsangiz, masalan tog'da, uch daqiqa kerak, chunki u yerda suv pastroq haroratda qaynaydi.

[3 · chemicals, glass in hand]
Ammo qaynatish kimyoviy moddalarni yo'qotmaydi. Choynak tubidagi oq qatlam esingizdami? U qaynatish paytida cho'kadi, lekin bu zararsiz kalsiy va magniy minerallari. Og'ir metallar, ko'plab tuzlar va boshqa kimyoviy ifloslar esa qaynatilgan suvda ham qolaveradi.

[4 · CTA]
Siz suv haqida yana qanday faktlarni bilishni xohlaysiz? Kommentda yozing, keyingi videolarimizda bular haqida ma'lumot berib o'tamiz. Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!
(Subtitle spells it "suvyektiv" — pun on the account name @suvyektiv; spoken the same as "subyektiv".)

## Top panel per paragraph

0. Cover: full-screen Javohir with kettle — "BUG' CHIQDI = QAYNADI?"
1. B-roll: steam from a kettle spout, close-up. Stamp "HALI QAYNAMAGAN!"
2. Side-by-side: small bubbles/steam ✕ vs big rolling bubbles ✓. Timer ring "1 daqiqa"; graphic lens: bacteria / virus / parasite cyst fade out. Mountain silhouette "2 000 m dan baland → 3 daqiqa", thermometer 100 °C → ~93 °C.
3. B-roll: limescale inside a kettle → label "Ca, Mg — zararsiz". Graphic lens: metal ions (Pb, As) and salts still floating — "kimyo qolaveradi".
4. CTA card: "Qaysi faktni bilmoqchisiz?" + @the.waterengineer.

Accent: warm amber on the dark-navy base.

## Caption draft (new info, not in the video)

Qaynatilgan suv hamma narsadan tozami? 💧

Oʻylab qarasam, qaynatilgan suvning taʼmi nega "boʻsh" boʻlishini hammamiz ham bilmas ekanmiz. Qaynaganda suvdagi erigan havo chiqib ketadi, shuning uchun u biroz "jonsiz" tuyuladi. Taʼmini qaytarish uchun suvni bir toza idishdan ikkinchisiga bir necha marta quyib chiqish kifoya, havo yana aralashadi.

Yana bir gap: qaynatilgan suvni ochiq idishda uzoq qoldirsangiz, mikroblar unga qaytadan tushishi mumkin. Shuning uchun uni yopiq, toza idishda saqlagan maʼqul.

Siz suv haqida qanday gapni eshitgansiz? Kommentda yozing, birga tekshirib koʻramiz.

Manba: US CDC (water treatment); US EPA, Emergency Disinfection of Drinking Water

#suv #foydalimalumotlar #bilasizmi #qiziqarlimalumotlar #uzbekistan #ilmfan #sogliq

## Sources
- CDC, Water treatment when hiking/camping/traveling: boiling kills all types of germs (viruses, bacteria, parasites incl. Cryptosporidium, Giardia); rolling boil 1 minute; above 6,500 ft (~2 000 m) 3 minutes; water with harmful chemicals cannot be made safe by boiling or disinfecting.
- US EPA, Emergency Disinfection of Drinking Water: boiling will not destroy heavy metals, salts and most other chemicals; improve flat taste by pouring between clean containers several times (WHO 2015 cited).
- Limescale forms on heating (see 2026-10-15 carousel, WHO Hardness in Drinking-water 2011).

## As filmed / edited (2026-10-21)
- Javohir's take differed from the script; subtitles follow the spoken text (src/subs.py). Lab setting (format C, B&W "REC" hook with focus-pull + beep, procedural steam from the pot).
- Section changes at Javohir's points (sec:frame, raw take): 03:29 colour + C layout, 17:03 mountains, 27:18 chemicals (foam river), 32:26 kettle pour (Ca, Mg), ~48.9 s ion-formula panel (Pb²⁺ Hg²⁺ Cd²⁺ As / Na⁺ Cl⁻ NO₃⁻ SO₄²⁻), 54:21 full-screen end with glass badge "Doktor H₂O · @suvyektiv".
- B-roll: Pixabay, real footage only (no AI-tagged clips): 267, 123988, 140030, 282048, 23955. Music: generated lo-fi (src/music_lofi.py).
- Rebuild: src/build.py (needs raw take, Pixabay clips in px/, edited.mov from timeline.py).
