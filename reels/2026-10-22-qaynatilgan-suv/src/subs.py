from timeline import new, CUTS
P = [(2.36,3.60,"Choynakdan bug' chiqdimi?"),(4.22,5.69,"Shoshmang, suv hali qaynamagan."),
(6.55,9.07,"Bug' suv qaynashdan oldin ham chiqishi mumkin."),(10.06,12.90,"Aslida suv qaynashi uchun biqir-biqir etib qaynashi kerak."),
(13.94,17.04,"Ya'ni shu holatda kamida bir daqiqa davomida qaynashi kerak."),(17.38,22.03,"Agar siz yuqori hududda, ya'ni tog'li balandlikda yashasangiz,"),
(22.60,23.97,"unda uch daqiqa kerak bo'ladi."),(24.26,27.13,"Chunki u yerda bosim pastligi uchun suv pastroq haroratda qaynaydi."),
(27.60,29.28,"Lekin qaynatish"),(30.23,31.60,"kimyoviy moddalardan tozalamaydi."),
(32.87,35.46,"O'tgan postimizda ko'rganimizdek,"),(35.98,38.48,"oq qatlam, ya'ni choynak tubidagi oq qatlam,"),
(38.83,41.59,"bu mineral qoldiqlari, ya'ni kalsiy va magniy."),(42.43,45.58,"Bu jarayonda, ya'ni qaynash jarayonida suvdan ajralib cho'kadi."),
(45.97,48.43,"Agar siz suvni yaxshi qaynatmasangiz,"),(48.98,51.58,"unda og'ir metallar va boshqa tuzlar"),
(52.23,54.53,"suvda aralashgan holda turaverishi mumkin."),(54.78,56.94,"Suv haqida yana qanday ma'lumotlarni bilishni xohlaysiz?"),
(57.43,61.96,"Kommentlarda yozing, biz keyingi videolarni shunga qarab tayyorlaymiz."),(62.25,65.37,"Bizni kuzatishda davom eting, suv haqida suvyektiv fikrlaymiz!")]
MAX = 22
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
ev=[]
for a,b,txt in P:
    A,B=new(a),new(b); words=txt.split()
    lines=[];cur=[]
    for w in words:
        if cur and len(" ".join(cur+[w]))>MAX: lines.append(cur);cur=[]
        cur.append(w)
    lines.append(cur)
    tot=sum(len(w)+1 for w in words); t=A
    for ln in lines:
        dur=(B-A)*sum(len(w)+1 for w in ln)/tot; t0,t1=t,t+dur; t=t1
        y = 1180 if (t0 < CUTS[0] - 0.05 or t0 >= CUTS[5] - 0.05) else 905
        k="".join(f"{{\\kf{max(1,round(100*(t1-t0)*(len(w)+1)/sum(len(x)+1 for x in ln)))}}}{w} " for w in ln).rstrip()
        ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},K,,0,0,0,,{{\\an5\\pos(540,{y})\\fad(60,40)}}{k}")
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: K,Inter ExtraBold,72,&H00FDD284,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open("subs.ass","w").write(hdr+"\n".join(ev)+"\n")
print(len(ev))
