"""High contrast weather pictograms using HKO's documented condition codes."""
import math
from PIL import Image, ImageDraw
LABELS = {50:'晴',51:'间有阳光',52:'短暂阳光',53:'阳光及几阵骤雨',54:'短暂阳光及骤雨',60:'多云',61:'密云',62:'微雨',63:'雨',64:'大雨',65:'雷暴',**{n:'夜间晴' for n in range(70,76)},76:'夜间多云',77:'夜间大致晴',80:'大风',81:'干燥',82:'潮湿',83:'雾',84:'薄雾',85:'烟霞',90:'热',91:'暖',92:'凉',93:'冷'}
def symbol(code, size=30):
    im=Image.new('L',(64,64),255);d=ImageDraw.Draw(im)
    def sun():
        d.ellipse((19,15,41,37),outline=0,width=3)
        for a in range(0,360,45):
            r=math.radians(a);d.line((30+16*math.cos(r),26+16*math.sin(r),30+23*math.cos(r),26+23*math.sin(r)),fill=0,width=3)
    def cloud():
        d.ellipse((9,28,31,49),fill=255,outline=0,width=3)
        d.ellipse((22,19,48,48),fill=255,outline=0,width=3)
        d.ellipse((38,30,58,49),fill=255,outline=0,width=3)
        d.rectangle((19,35,48,48),fill=255);d.line((19,48,48,48),fill=0,width=3)
    if code in (50,51,52,53,54): sun()
    if code in (51,52,53,54,60,61,62,63,64,65,76): cloud()
    if code in (53,54,62,63,64):
        for x in (20,33,46):d.line((x,53,x-4,61),fill=0,width=3 if code==64 else 2)
    if code==65:d.polygon([(35,39),(27,52),(35,52),(30,63),(45,47),(36,47)],fill=0)
    if code in range(70,76) or code==77:
        d.ellipse((14,8,51,47),fill=0);d.ellipse((26,4,57,37),fill=255)
    if code in (80,83,84,85):
        for y,x in ((18,8),(30,16),(42,8)):d.line((x,y,55,y),fill=0,width=3)
    if code in (81,82):
        d.polygon([(32,7),(15,34),(15,43),(24,53),(40,53),(49,43),(49,34)],outline=0,width=3)
        if code==81:d.line((12,55,52,9),fill=0,width=4)
    if code in (90,91,92,93):
        d.rounded_rectangle((26,8,38,44),radius=5,outline=0,width=3);d.ellipse((21,36,43,58),outline=0,width=3)
        d.line((32,18 if code<92 else 34,32,46),fill=0,width=4)
    return im.resize((size,size),Image.Resampling.LANCZOS).point(lambda p:255 if p>160 else 0)
