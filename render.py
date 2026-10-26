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
    def text(x,y,s,size=22,fill=0):d.text((x,y),str(s),font=ImageFont.truetype(FONT,size),fill=fill)
    def center(x,y,s,size=22,fill=0):
        f=ImageFont.truetype(FONT,size);d.text((x-d.textlength(str(s),font=f)/2,y),str(s),font=f,fill=fill)
    def rule(y):d.line((28,y,572,y),fill=0,width=2)
    text(28,22,'香港 · 屯门',26);text(402,26,now.strftime('%Y 年 %m 月'),20);rule(65)
    text(28,75,f'{now.day:02}',110)
    text(205,94,'星期'+'一二三四五六日'[now.weekday()],38)
    text(207,150,now.strftime('%Y / %m / %d'),23)
    lunar_date=(lunar or {}).get('LunarDate','').replace('閏','闰').replace('臘','腊')
    lunar_year=(lunar or {}).get('LunarYear','').split('，')[0]
    text(207,186,('农历 '+lunar_year+' '+lunar_date) if lunar_date else '农历暂不可用',20)
    rule(222)
    temps=current.get('temperature',{}).get('data',[])
    station=next((x for x in temps if x['place'] in ('屯门','屯門')),None)
    updated=current.get('temperature',{}).get('recordTime',current.get('updateTime',''))
    text(28,239,'屯门站气温',19)
    text(27,266,f"{station['value']}°C" if station else '暂无数据',48)
    label='实测 '+updated[11:16] if updated[:10]==now.strftime('%Y-%m-%d') else '实测 '+updated[:16].replace('T',' ')
    text(29,326,label,16)
    codes=[code for code in current.get('icon',[]) if code in LABELS]
    if codes:
        im.paste(symbol(codes[0]),(28,348))
        condition='全港：'+'/'.join(LABELS[code] for code in codes)
        size=16
        while size>10 and d.textlength(condition,font=ImageFont.truetype(FONT,size))>190:size-=1
        text(64,354,condition,size)
    else:
        text(29,352,'天气情况暂无数据',16)
    days=[x for x in forecast.get('weatherForecast',[]) if x['forecastDate']>=now.strftime('%Y%m%d')][:2]
    for i,day in enumerate(days):
        x=265+i*160;dt=datetime.strptime(day['forecastDate'],'%Y%m%d')
        text(x,241,dt.strftime('%m/%d')+' '+day['week'].replace('星期','周'),19)
        text(x,274,f"{day['forecastMintemp']['value']}–{day['forecastMaxtemp']['value']}°",32)
        text(x,320,'降雨概率 '+day.get('PSR','--'),16)
    text(265,348,'预报范围：全港',16);rule(380)
    text(28,396,now.strftime('%Y 年 %m 月'),24)
    weekdays='一二三四五六日';cell=76
    for col,day in enumerate(weekdays):center(72+col*cell,439,day,19)
    weeks=calendar.Calendar(0).monthdayscalendar(now.year,now.month)
    for row,week in enumerate(weeks):
        for col,day in enumerate(week):
            if not day:continue
            x=72+col*cell;y=479+row*36
            if day==now.day:d.rounded_rectangle((x-23,y-2,x+23,y+30),radius=5,fill=0)
            center(x,y,day,23,255 if day==now.day else 0)
    rule(709)
    text(28,726,'数据：香港天文台  ·  图源：云端自动生成',16)
    text(28,754,'画面更新 '+now.strftime('%m/%d %H:%M')+'  ·  断网时保留最后画面',16)
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
