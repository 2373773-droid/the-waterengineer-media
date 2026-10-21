"""Light, warm lo-fi bed (92 BPM): soft kick, brushed hat, e-piano chords, sub bass. No samples."""
import numpy as np, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR=48000; DUR=float(sys.argv[1]); BPM=92; beat=60/BPM
n=int(SR*DUR); out=np.zeros((2,n)); rng=np.random.default_rng(5)
def midi(m): return 440*2**((m-69)/12)
def add(sig,start,pan=0.0,g=1.0):
    i=int(start*SR); 
    if i>=n: return
    s=sig[:n-i]*g; out[0,i:i+len(s)]+=s*(1-pan)/1; out[1,i:i+len(s)]+=s*(1+pan)/1
def ep(f,d):  # electric-piano-ish tone
    t=np.arange(int(SR*d))/SR; env=np.exp(-t*2.2)*(1-np.exp(-t*80))
    return env*(np.sin(2*np.pi*f*t+0.8*np.exp(-t*4)*np.sin(2*np.pi*f*2*t))+0.25*np.sin(2*np.pi*f*3*t)*np.exp(-t*6))
def kick():
    t=np.arange(int(SR*0.35))/SR; f=50+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat():
    x=rng.standard_normal(int(SR*0.06)); x=sosfilt(butter(4,7000,'hp',fs=SR,output='sos'),x)
    return x*np.exp(-np.arange(len(x))/SR*70)
def bass(f,d):
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*t)*np.minimum(1,t*30)*np.exp(-t*1.2)
CH=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]   # Fmaj7 Em7 Dm7 Cmaj7
BS=[41,40,38,36]
bar=4*beat; nb=int(DUR/bar)+1
for b in range(nb):
    c=CH[b%4]; t0=b*bar
    for k,m in enumerate(c): add(ep(midi(m),bar*1.1),t0+0.012*k,pan=(k-1.5)*0.15,g=0.10)
    for k,m in enumerate([c[3]+12,c[2]+12]): add(ep(midi(m),beat*1.5),t0+beat*2.5+k*beat*0.5,pan=0.3,g=0.05)
    add(bass(midi(BS[b%4]),bar),t0,g=0.22)
    for q in range(4):
        if q in (0,2) or (q==3 and b%2): add(kick(),t0+q*beat+(0.5*beat if q==3 else 0),g=0.35)
        for e in range(2): add(hat(),t0+q*beat+e*beat/2+(0.02 if e else 0),pan=-0.3,g=0.06 if e else 0.10)
# warmth: lowpass + gentle tape wobble noise
for ch in range(2): out[ch]=sosfilt(butter(2,5200,'lp',fs=SR,output='sos'),out[ch])
out+=0.002*sosfilt(butter(2,[300,3000],'bp',fs=SR,output='sos'),rng.standard_normal(n))
t=np.arange(n)/SR; out*=np.clip(t/1.0,0,1)*np.clip((DUR-t)/1.5,0,1)
out/=np.abs(out).max()*1.12
wavfile.write("music.wav",SR,(out.T*32767).astype(np.int16)); print("ok")
