#!/usr/bin/env python3
"""Port of the colour derivation used by the KDE Oxygen style.

Used to calibrate the GTK colour expressions in src/_oxygen.scss (oxy-light,
oxy-dark, oxy-shadow, oxy-mid). It reimplements:
  * KColorUtils HCY colour space and shade()                (kcolorutils.cpp)
  * KColorScheme::shade()                                   (kcolorscheme.cpp)
  * Oxygen::Helper::calcLightColor / calcDarkColor / calcShadowColor
    (liboxygen/oxygenhelper.cpp) and StyleHelper::calcMidColor
with Oxygen's default contrast of 0.4. Run it to print the colours Oxygen would
derive for a few sample surfaces, then compare with the SCSS functions.
"""
G=2.2
def gamma(x): return x**G
def igamma(x): return max(0.0,min(1.0,x))**(1/G)
YC=(0.299,0.587,0.114)
def luma(c):
    r,g,b=[gamma(v/255) for v in c]; return r*YC[0]+g*YC[1]+b*YC[2]
def to_hcy(c):
    r,g,b=[gamma(v/255) for v in c]
    y=r*YC[0]+g*YC[1]+b*YC[2]
    p=max(r,g,b); n=min(r,g,b); d=6.0*(p-n)
    if n==p: h=0.0
    elif r==p: h=((g-b)/d)%1.0
    elif g==p: h=((b-r)/d)+1/3
    else: h=((r-g)/d)+2/3
    h%=1.0
    c_=0.0 if (y==0.0 or y==1.0) else max((y-n)/y,(p-y)/(1-y))
    return h,c_,y
def from_hcy(h,c,y):
    h=h%1.0; c=max(0,min(1,c)); y=max(0,min(1,y))
    hs=h*6.0
    if hs<1: th=hs; tm=YC[0]+YC[1]*th
    elif hs<2: th=2-hs; tm=YC[1]+YC[0]*th
    elif hs<3: th=hs-2; tm=YC[1]+YC[2]*th
    elif hs<4: th=4-hs; tm=YC[2]+YC[1]*th
    elif hs<5: th=hs-4; tm=YC[2]+YC[0]*th
    else: th=6-hs; tm=YC[0]+YC[2]*th
    if tm>=y:
        tp=y+y*c*(1-tm)/tm; to=y+y*c*(th-tm)/tm; tn=y-(y*c)
    else:
        tp=y+(1-y)*c; to=y+(1-y)*c*(th-tm)/(1-tm); tn=y-(1-y)*c*tm/(1-tm)
    if hs<1: rgb=(tp,to,tn)
    elif hs<2: rgb=(to,tp,tn)
    elif hs<3: rgb=(tn,tp,to)
    elif hs<4: rgb=(tn,to,tp)
    elif hs<5: rgb=(to,tn,tp)
    else: rgb=(tp,tn,to)
    return tuple(round(255*igamma(v)) for v in rgb)
def kshade(c,ky,kc=0.0):
    h,ch,y=to_hcy(c); return from_hcy(h,ch+kc,y+ky)
def mix(a,b,t): return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))   # KColorUtils::mix(a,b,bias): bias weight of b
def darken(c,amount=0.1,chroma=1.0):
    h,ch,y=to_hcy(c); return from_hcy(h,ch*chroma,y*(1-amount))
def scheme_shade(c,role,contrast,chroma=0.0):
    contrast=max(-1,min(1,contrast)); y=luma(c); yi=1-y
    if y<0.006:
        return {'L':kshade(c,0.05+0.95*contrast,chroma),'M':kshade(c,0.01+0.20*contrast,chroma),'D':kshade(c,0.02+0.40*contrast,chroma)}.get(role,kshade(c,0.03+0.60*contrast,chroma))
    if y>0.93:
        if role=='ML': return kshade(c,-0.02-0.20*contrast,chroma)
        if role=='D': return kshade(c,-0.06-0.60*contrast,chroma)
        if role=='S': return kshade(c,-0.10-0.90*contrast,chroma)
        return kshade(c,-0.04-0.40*contrast,chroma)
    la=(0.05+y*0.55)*(0.25+contrast*0.75); da=(-y)*(0.55+contrast*0.45)
    if role=='L': return kshade(c,la,chroma)
    if role=='ML': return kshade(c,(0.15+0.35*yi)*la,chroma)
    if role=='M': return kshade(c,(0.35+0.15*y)*da,chroma)
    if role=='D': return kshade(c,da,chroma)
    return darken(kshade(c,da,chroma),0.5+0.3*y)
CONTRAST=0.4
def low(c):  return luma(scheme_shade(c,'M',0.5))>luma(c)
def high(c): return luma(scheme_shade(c,'L',0.5))<luma(c)
def light(c): return c if high(c) else scheme_shade(c,'L',CONTRAST)
def dark(c):  return mix(light(c),c,0.3+0.7*CONTRAST) if low(c) else scheme_shade(c,'M',CONTRAST)
def shadow(c):
    return c if False else (mix((0,0,0),c,1.0) if low(c) else scheme_shade(mix((0,0,0),c,1.0),'S',CONTRAST))
if __name__=='__main__':
    for name,base in (('Oxygen window',(224,223,222)),('Oxygen button',(223,220,217)),('observed window',(214,210,207)),('Breeze dark window',(49,54,59)),('Zion-like dark',(36,36,36))):
        print(name,base,'light',light(base),'dark',dark(base),'shadow',shadow(base),'low',low(base),'high',high(base))
