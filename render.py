"""600x800 Chinese calendar for DayPane. Public HKO data only."""
import calendar, hashlib, json, os, time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont
from weather_symbols import LABELS, symbol

OUT=Path(os.environ.get('OUTPUT_DIR','public')); OUT.mkdir(exist_ok=True)
TZ=ZoneInfo('Asia/Hong_Kong')
FONT=os.environ.get('FONT_PATH','/System/Library/Fonts/STHeiti Medium.ttc')
def fetch(kind):
    url='https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType='+kind+'&lang=sc'
    return fetch_url(url)

def fetch_url(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={'User-Agent':'KindleCalendar/1.0'}),timeout=25) as r:return json.load(r)
        except Exception:
            if attempt==2:raise
            time.sleep(3)

def render(now,current,forecast,lunar=None):
    im=Image.new('L',(600,800),255); d=ImageDraw.Draw(im)
    def text(x,y,s,size=22,fill=0,align='left',width=None):
        s=str(s)
        while True:
            f=ImageFont.truetype(FONT,size)
            if width is None or d.textlength(s,font=f)<=width or size<=12:break
            size-=1
        box=d.textbbox((0,0),s,font=f)
        if align=='right':x-=d.textlength(s,font=f)
        elif align=='center':x-=d.textlength(s,font=f)/2
        d.text((x-box[0],y-box[1]),s,font=f,fill=fill)
    def rule(y):d.line((38,y,562,y),fill=0,width=1)

    text(38,32,'香港  /  屯门',20)
    text(562,34,now.strftime('%Y  /  %m'),19,align='right')
    rule(66)
    text(32,91,f'{now.day:02}',142)
    text(290,103,'星期'+'一二三四五六日'[now.weekday()],34)
    lunar_date=(lunar or {}).get('LunarDate','').replace('閏','闰').replace('臘','腊')
    lunar_year=(lunar or {}).get('LunarYear','').split('，')[0]
    text(292,160,'农历  '+lunar_year if lunar_date else '农历暂不可用',17)
    if lunar_date:text(292,190,lunar_date,24)
    rule(237)

    temps=current.get('temperature',{}).get('data',[])
    station=next((x for x in temps if x.get('place') in ('屯门','屯門')),None)
    updated=current.get('temperature',{}).get('recordTime',current.get('updateTime','')) or ''
    observed=updated[11:16] if updated[:10]==now.strftime('%Y-%m-%d') else updated[:16].replace('T',' ')
    text(38,255,'屯门实测'+('  /  '+observed if observed else '  /  暂无数据'),16,width=280)
    codes=[code for code in (current.get('icon') or []) if code in LABELS]
    if codes:im.paste(symbol(codes[0],60),(32,281))
    text(108 if codes else 38,286,f"{station['value']}°C" if station else '暂无数据',48 if station else 26,width=180)
    condition=' / '.join(LABELS[code] for code in codes) if codes else '天气暂无数据'
    text(562,287,condition,25,align='right',width=260)
    text(562,322,'全港天气概况',15,align='right')

    days=[x for x in forecast.get('weatherForecast',[]) if x['forecastDate']>=now.strftime('%Y%m%d')][:2]
    rule(359)
    for i in range(2):
        x=38+i*278
        if i>=len(days):
            text(x,382,'预报暂无数据',18);continue
        day=days[i];dt=datetime.strptime(day['forecastDate'],'%Y%m%d')
        text(x,378,dt.strftime('%m/%d')+' '+day['week'].replace('星期','周'),16)
        text(x+246,375,f"{day['forecastMintemp']['value']}–{day['forecastMaxtemp']['value']}°",25,align='right')
        text(x,407,'全港 · 降雨概率 '+day.get('PSR','--'),14,width=246)
    d.line((300,378,300,422),fill=0,width=1)
    rule(441)

    text(38,462,f'{now.month:02}  /  月历',20)
    text(562,465,str(now.year),16,align='right')
    cell=524/7
    for col,day in enumerate('一二三四五六日'):
        text(38+(col+.5)*cell,507,day,16,align='center')
    weeks=calendar.Calendar(0).monthdayscalendar(now.year,now.month)
    step=34 if len(weeks)==6 else 42
    for row,week in enumerate(weeks):
        for col,day in enumerate(week):
            if not day:continue
            x=38+(col+.5)*cell;y=546+row*step
            if day==now.day:d.ellipse((x-19,y-9,x+19,y+29),fill=0)
            text(x,y,day,23,255 if day==now.day else 0,align='center')
    rule(756)
    text(38,773,'香港天文台',13)
    text(562,773,'更新 '+now.strftime('%m/%d %H:%M'),13,align='right')
    return im.convert('1',dither=Image.Dither.NONE)

def main():
    now=datetime.now(TZ)
    try:current=fetch('rhrread')
    except Exception:current={}
    try:forecast=fetch('fnd')
    except Exception:forecast={}
    try:lunar=fetch_url('https://data.weather.gov.hk/weatherAPI/opendata/lunardate.php?date='+now.strftime('%Y-%m-%d'))
    except Exception:lunar={}
    im=render(now,current,forecast,lunar);im.save(OUT/'screen.png')
    image=(OUT/'screen.png').read_bytes();digest=hashlib.sha256(image).hexdigest()
    # Content-addressed image prevents manifest/image races during deployment.
    name='image-'+digest[:16]+'.png';(OUT/name).write_bytes(image)
    meta={'schemaVersion':1,'generatedAt':int(now.timestamp()*1000),'sha256':digest,'image_url':name,'weatherUpdatedAt':current.get('updateTime'),'timezone':'Asia/Hong_Kong','lunar':lunar}
    (OUT/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False),encoding='utf-8')
    (OUT/'index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>屯门日历</title><style>body{background:#eee;text-align:center;font-family:sans-serif}img{max-width:100%;height:auto}p{font-size:14px}</style><h1>屯门日历</h1><p>云端每半小时计划更新；调度可能延迟。图片底部显示更新时间。</p><img src="screen.png" alt="屯门天气和中文月历"><p><a href="manifest.json">更新状态</a> · 天气来源：香港天文台</p></html>',encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
