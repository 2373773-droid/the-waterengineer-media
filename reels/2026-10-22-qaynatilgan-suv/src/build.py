import subprocess, sys
from timeline import new, CUTS, TOTAL
XF = 0.4
T0 = CUTS[0] - XF / 2
px = "px/"
# top-panel clips: (file, source offset, speed factor, chip)
mid5 = new(48.85)  # 'og'ir metallar' starts -> ion formulas panel
bounds = [0, new(9.9) - T0, CUTS[1] - T0, CUTS[2] - T0, CUTS[3] - T0, mid5 - T0, CUTS[5] - T0]
bounds[0] = 0
# (file, offset, speed, chip, crop-x fraction)
clips = [("B0.mp4", 2.0, 1.0, "g_c1.png", .5), ("BB2.mp4", 0.0, 1.0, "g_c2.png", .5), ("M3.mp4", 0.0, 1.0, "g_c3.png", .5),
         ("Y5.mp4", 6.0, 1.0, "g_c4.png", .2), ("E0.mp4", 3.0, 1.0, "g_c5.png", .5),
         ("IONS.mp4", 0.0, 1.0, None, 0)]

inputs = ["-i", "edited.mov", "-i", "steam.mkv", "-loop", "1", "-i", "g_rec.png", "-loop", "1", "-i", "g_dot.png"]
idx = 4
fc = []
# person + steam
fc.append("[1:v]format=gray,setpts=PTS-STARTPTS[sa];color=white:s=1080x1920:r=30:d=10.1,format=rgb24[sw];[sw][sa]alphamerge[st]")
fc.append("[0:v][st]overlay=format=auto:eof_action=pass,format=yuv420p,split[pf][pc]")
# full-screen B&W "camera" section
fdur = CUTS[0] + XF / 2
fc.append(f"[pf]trim=0:{fdur:.3f},setpts=PTS-STARTPTS,hue=s=0,eq=contrast=1.12:brightness=-0.02,noise=alls=14:allf=t,vignette=PI/4.5,split[fs][fz];[fz]gblur=sigma=28[fbl];[fs][fbl]blend=all_expr='A*(1-clip((0.75-T)/0.45\\,0\\,1))+B*clip((0.75-T)/0.45\\,0\\,1)+0*(B-A)*between(T\\,0.82\\,0.9)'[fb]")
fc.append(f"[2:v]trim=0:{fdur:.3f},setpts=PTS-STARTPTS,format=rgba[rec];[3:v]trim=0:{fdur:.3f},setpts=PTS-STARTPTS,format=rgba[dot]")
fc.append("[fb][rec]overlay=format=auto[f1];[f1][dot]overlay=format=auto:enable='lt(mod(t\\,1)\\,0.6)'[f2]")
fc.append("[f2]drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-SemiBold.otf:text='00\\:00\\:0%{eif\\:t\\:d}\\:%{eif\\:mod(n\\,30)\\:d\\:2}':x=(w-tw)/2:y=165:fontsize=44:fontcolor=white,format=yuv420p,fps=30[FULL]")
# bottom panel
fc.append(f"[pc]trim=start={T0:.3f},setpts=PTS-STARTPTS,crop=1080:1020:0:700[BOT]")
# top panel clips
labels = []
def chip_out(i):
    return f",fade=out:st={CUTS[4]-CUTS[3]-0.3:.3f}:d=0.3:alpha=1" if i == 4 else ""
for i, (f, off, sp, ch, cx) in enumerate(clips):
    L = bounds[i + 1] - bounds[i] + XF
    if f == "BRAND":
        inputs += ["-loop", "1", "-i", "g_brand.png"]
        fc.append(f"[{idx}:v]scale=1188:990,zoompan=z='1+0.0004*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x900:fps=30,trim=0:{L:.3f},setpts=PTS-STARTPTS,format=yuv420p[t{i}]")
        idx += 1
    else:
        inputs += ["-ss", str(off), "-i", px + f]
        fc.append(f"[{idx}:v]setpts={sp}*(PTS-STARTPTS),fps=30,scale=-2:900:flags=lanczos,crop=1080:900:(iw-1080)*{cx}:0,setsar=1,trim=0:{L:.3f},setpts=PTS-STARTPTS,format=yuv420p[r{i}]")
        idx += 1
        if ch:
            inputs += ["-loop", "1", "-i", ch]
            fc.append(f"[{idx}:v]trim=0:{L:.3f},setpts=PTS-STARTPTS,format=rgba,fade=in:st=0.5:d=0.35:alpha=1{chip_out(i)}[c{i}];[r{i}][c{i}]overlay=format=auto,format=yuv420p[t{i}]")
            idx += 1
        else:
            fc.append(f"[r{i}]null[t{i}]")
# xfade chain
cur = "t0"
for i in range(1, len(clips)):
    fc.append(f"[{cur}][t{i}]xfade=transition=fade:duration={XF}:offset={bounds[i]:.3f}[x{i}]")
    cur = f"x{i}"
fc.append(f"[{cur}][BOT]vstack=shortest=1,fps=30[CC]")
# end: full-screen Javohir (colour) with a glass name badge
E0t = CUTS[5] - XF / 2
inputs += ["-loop", "1", "-i", "g_badge_mask.png", "-loop", "1", "-i", "g_badge.png", "-ss", f"{E0t:.3f}", "-i", "edited.mov"]
fc.append(f"[{idx+2}:v]setpts=PTS-STARTPTS,split[e1][e2];[e2]crop=760:260:160:250,gblur=sigma=16,format=rgba[eb];[{idx}:v]format=gray[em];[eb][em]alphamerge[ebm];[e1][ebm]overlay=160:250:shortest=1[e3];[{idx+1}:v]format=rgba,fade=in:st=0.5:d=0.4:alpha=1[bd];[e3][bd]overlay=160:250:shortest=1,format=yuv420p,fps=30,settb=1/30[END]")
idx += 3
fc.append(f"[FULL][CC]xfade=transition=fade:duration={XF}:offset={CUTS[0]-XF/2:.3f}[M1]")
fc.append(f"[M1][END]xfade=transition=fade:duration={XF}:offset={CUTS[5]-XF/2:.3f},ass=subs.ass:fontsdir=/usr/share/fonts/opentype/inter,format=yuv420p[V]")
# audio
inputs += ["-i", "music.wav"]
inputs += ["-f", "lavfi", "-i", "sine=f=2700:d=0.07:sample_rate=48000", "-f", "lavfi", "-i", "sine=f=2700:d=0.07:sample_rate=48000"]
fc.append(f"[{idx+1}:a]afade=t=out:st=0.05:d=0.02,volume=-17dB,adelay=760|760,aformat=channel_layouts=stereo[bp1];[{idx+2}:a]afade=t=out:st=0.05:d=0.02,volume=-17dB,adelay=880|880,aformat=channel_layouts=stereo[bp2]")
fc.append("[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit[voice][sc]")
fc.append(f"[{idx}:a]volume=-21dB,atrim=0:{TOTAL:.3f}[mus];[mus][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=400[duck]")
fc.append("[voice][duck][bp1][bp2]amix=inputs=4:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[A]")
open("graph.txt", "w").write(";\n".join(fc))
cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[V]", "-map", "[A]",
       "-t", f"{TOTAL:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", sys.argv[1] if len(sys.argv) > 1 else "reel.mp4"]
subprocess.run(cmd, check=True)
