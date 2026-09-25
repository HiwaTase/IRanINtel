#!/usr/bin/env python3
"""Reconstruct the article's text-analysis workflow from the public Telegram export.

All matches are transparent dictionary screens. They do not recover undocumented
manual corrections behind the published article. Outputs include intermediate
matched post IDs for qualitative review and a comparison to published counts.
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

Y0, Y1 = '2018', '2025'
START = '2022-09-14'
# Persian/Kurdish spellings and transliterations; avoid the bare Persian "کرد"
# because it is also the past tense of "to do".
PATTERNS = {
 'kurdish_related': r'سنندج|سنە|سقز|سەقز|مهاباد|بوکان|بۆکان|پیرانشهر|جوانرود|جوانڕۆ|اشنویه|مریوان|مەریوان|بانه|دیواندره|کامیاران|کردستان|کوردستان|کردها|کوردها|(?:زبان|فرهنگ|ادبیات) کردی|کوردی|کردنشین|کوردنشین|شهروندان کرد|مردم کرد|مردم کردستان|زندانیان کرد|فعالان کرد|کولبر|کۆڵبەر|کومله|کومەلە|دموکرات کردستان|پژاک|پژاک|روژهلات|ڕۆژهەڵات',
 'agency': r'اعتراض|معترض|تجمع|تظاهرات|راهپیمایی|اعتصاب|فراخوان|بیانیه|مطالبات|حقوق|فدرالیسم|خودمختاری|همبستگی',
 'victimhood': r'اعدام|قتل|کشته|بازداشت|دستگیر|زندان|شکنجه|تیراندازی|کولبر|کۆڵبەر',
 'security': r'تجزیه|جدایی.?طلب|تروریس|مسلح|گروهک|تمامیت ارضی|امنیت',
 'attacks': r'حمله|موشک|پهپاد|بمباران|توپباران',
 'statements': r'بیانیه|اطلاعیه|فراخوان|اعلام کرد|درخواست کرد',
 'state_sources': r'سپاه پاسداران|وزارت اطلاعات|خبرگزاری فارس|خبرگزاری تسنیم|ایرنا',
 'iranian_nation': r'ملت ایران|ملتِ ایران|ملت بزرگ ایران',
 'kurdish_nation_candidate': r'ملت کرد|ملتِ کرد|ملت کورد|ملتِ کورد',
 'kurdish_citizens': r'شهروندان کرد|شهروندان کورد|شهروندانِ کرد',
 'kurdish_people': r'مردم کرد|مردم کورد|مردم کردستان|مردم کوردستان',
 'rojhelat': r'روژهلات|ڕۆژهەڵات|Rojhelat',
 'kurdistan': r'کردستان|کوردستان',
 'iraqi_kurdistan': r'اقلیم کردستان|اقلیمِ کردستان|کردستان عراق',
 'kurdistan_province': r'استان کردستان|استانِ کردستان',
 'minority': r'اقلیت',
 'ethnic_groups': r'اقوام|قومیت',
 'autonomy': r'خودمختاری|حق تعیین سرنوشت',
 'jina': r'ژینا|جینا|Jina',
 'mahsa': r'مهسا|Mahsa',
 'amini': r'امینی|Amini',
 'kurdish_slogan': r'ژن[،,\s]+ژیان[،,\s]+ئازادی|Jin[ ,]+Jiyan[ ,]+Azad',
 'persian_slogan': r'زن[،,\s]+زندگی[،,\s]+آزادی|Zan[ ,]+Zendegi[ ,]+Azad',
 'kdpi': r'حزب دموکرات کردستان|حزب دمکرات کردستان|حزب دموکرات کوردستان|حدکا|حدک|KDPI|PDKI',
 'komala': r'کومله|کومەلە|کۆمەڵە|Komala',
 'pjak': r'پژاک|PJAK',
 'hengaw': r'هه.?نگاو|هەنگاو|هنگاو|Hengaw',
 'khrn': r'شبکه حقوق بشر کردستان|شبکه حقوق بشر کوردستان|Kurdistan Human Rights Network',
 'kurdpa': r'کردپا|کوردپا|Kurdpa',
 'hrana': r'هرانا|HRANA',
 'iran_human_rights': r'سازمان حقوق بشر ایران|Iran Human Rights',
 'amnesty': r'عفو بین.?الملل|Amnesty International',
 'grouplet': r'گروهک',
 'terrorist': r'تروریست|تروریستی',
 'armed': r'مسلح',
 'mohtadi': r'عبدالله مهتدی|عبداله مهتدی|Abdullah Mohtadi',
 'azizi': r'خالد عزیزی|Khalid Azizi',
 'alizadeh': r'ابراهیم علیزاده|Ibrahim Alizadeh',
 'hijri': r'مصطفی هجری|Mustafa Hijri',
 'ilkhanizadeh': r'عمر ایلخانی.?زاده|Omar Ilkhanizadeh',
 'ghassemlou': r'عبدالرحمان قاسملو|عبدالرحمن قاسملو|Abdul Rahman Ghassemlou',
 'kaabi': r'رضا کعبی|Reza Kaabi',
 'galaleh': r'گلاله شرفکندی|Galaleh Sharafkandi',
 'mauludi': r'مصطفی مولودی|Mustafa Mauludi',
 'sadegh': r'صادق شرفکندی|Sadegh Sharafkandi',
 'haji_ahmadi': r'رحمان حاجی احمدی|Rahman Haji Ahmadi',
}
PLACES = {
 'sanandaj': r'(?<![\wآ-ی])(?:سنندج|سنە|Sanandaj)(?![\wآ-ی])',
 'saqqez': r'سقز|سەقز', 'mahabad': r'مهاباد', 'marivan': r'مریوان|مەریوان',
 'bukan': r'بوکان|بۆکان', 'oshnavieh': r'اشنویه', 'kamayaran': r'کامیاران',
 'kermanshah': r'(?<![\wآ-ی])(?:کرمانشاه|کرماشان|کەرماشان|Kermanshah|Kirmashan)(?![\wآ-ی])',
 'ilam': r'(?<![\wآ-ی])(?:ایلام|ئیلام|Ilam|Îlam)(?![\wآ-ی])',
}
REFERENCE = {
 'all_messages':299254,'kurdish_related':4250,'iranian_nation':888,
 'kurdish_nation_contextual':1,'kurdish_citizens':54,'kurdish_people':49,
 'rojhelat':0,'kurdistan':1680,'iraqi_kurdistan':419,'kurdistan_province':189,
 'komala':142,'kdpi':135,'pjak':12,'hengaw_in_subset':226,
 'khrn_in_subset':83,'kurdpa_in_subset':24,
}
RX={k:re.compile(v,re.I) for k,v in PATTERNS.items()}
PX={k:re.compile(v,re.I) for k,v in PLACES.items()}
LEADERS=['mohtadi','azizi','alizadeh','hijri','ilkhanizadeh','ghassemlou','kaabi','galaleh','mauludi','sadegh','haji_ahmadi']
PARTIES=['kdpi','komala','pjak']
SOURCES=['hengaw','khrn','kurdpa','hrana','iran_human_rights','amnesty']
FRAMES=['agency','victimhood','security','attacks','statements','state_sources','terrorist','armed','grouplet']


def flatten(value):
 if isinstance(value,str):return value
 if isinstance(value,list):return ''.join(x if isinstance(x,str) else x.get('text','') for x in value)
 return ''


def csv_out(path,rows,fields):
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('archive',type=Path)
 ap.add_argument('--out',type=Path,default=Path('article_output'))
 args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 with args.archive.open(encoding='utf-8') as f: messages=json.load(f)['messages']
 annual=defaultdict(Counter);monthly=defaultdict(Counter);tot=Counter()
 party_year=defaultdict(Counter);party_frame=defaultdict(Counter)
 name_year=defaultdict(Counter);source_count=Counter();leader_year=defaultdict(Counter)
 leader_speech=Counter();place_count=Counter();matched=[]
 with (args.out/'post_flags.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['id','date','year','kurdish_related','matched_categories','matched_places','text']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for m in messages:
   date=m.get('date','')[:10];year=date[:4]
   if m.get('type')!='message' or not(Y0<=year<=Y1):continue
   text=flatten(m.get('text',''))
   hits={k for k,rx in RX.items() if rx.search(text)}
   places={k for k,rx in PX.items() if rx.search(text)}
   kurdish='kurdish_related' in hits
   tot['all_messages']+=1;annual[year]['all_messages']+=1
   for k in hits:tot[k]+=1
   for k in places:
    place_count[k]+=1
    if kurdish:place_count[k+'_in_subset']+=1
   if kurdish:
    tot['kurdish_related']+=0 # already included in hits above
    annual[year]['kurdish_related']+=1
    monthly[date[:7]]['kurdish_related']+=1
    for k in FRAMES:
     if k in hits:annual[year][k]+=1
    for k in SOURCES:
     if k in hits:source_count[k]+=1
    for k in PARTIES:
     if k in hits:tot[k+'_in_subset']+=1
   for k in PARTIES:
    if k in hits:
     party_year[year][k]+=1
     for frame in FRAMES:
      if frame in hits:party_frame[k][frame]+=1
   if date>=START:
    for k in ['jina','mahsa','kurdish_slogan','persian_slogan']:
     if k in hits and (k not in ['jina','mahsa'] or 'amini' in hits):name_year[year][k]+=1
   for k in LEADERS:
    if k in hits:
     leader_year[k][year]+=1
     # Proxy only: requires manual reading to decide whether a leader speaks.
     if re.search(r'گفت|می.?گوید|مصاحبه|گفت.?وگو|گفتگو',text):leader_speech[k]+=1
   if kurdish or places:
    w.writerow({'id':m['id'],'date':date,'year':year,
      'kurdish_related':int(kurdish),'matched_categories':';'.join(sorted(hits)),
      'matched_places':';'.join(sorted(places)),'text':text})

 csv_out(args.out/'annual_visibility.csv',
  [dict(year=y,**annual[y]) for y in sorted(annual)],
  ['year','all_messages','kurdish_related']+FRAMES)
 csv_out(args.out/'monthly_visibility.csv',
  [dict(month=y,**monthly[y]) for y in sorted(monthly)],['month','kurdish_related'])
 csv_out(args.out/'party_year.csv',
  [dict(year=y,**party_year[y]) for y in sorted(annual)],['year']+PARTIES)
 csv_out(args.out/'party_frames.csv',
  [dict(party=k,posts=tot[k],**party_frame[k]) for k in PARTIES],
  ['party','posts']+FRAMES)
 csv_out(args.out/'names_and_slogans.csv',
  [dict(year=y,**name_year[y]) for y in sorted(name_year)],
  ['year','jina','mahsa','kurdish_slogan','persian_slogan'])
 csv_out(args.out/'sources.csv',
  [dict(source=k,posts=source_count[k]) for k in SOURCES],['source','posts'])
 csv_out(args.out/'leaders.csv',
  [dict(leader=k,total=sum(leader_year[k].values()),speech_keyword_proxy=leader_speech[k],
        **{y:leader_year[k][y] for y in sorted(annual)}) for k in LEADERS],
  ['leader','total','speech_keyword_proxy']+sorted(annual))
 csv_out(args.out/'places.csv',
  [dict(place=k,all_posts=place_count[k],kurdish_subset=place_count[k+'_in_subset']) for k in PLACES],
  ['place','all_posts','kurdish_subset'])
 # A contextual phrase can otherwise match "did [something] for the nation".
 candidate_ids=[]
 with (args.out/'post_flags.csv').open(encoding='utf-8',newline='') as f:
  for row in csv.DictReader(f):
   if 'kurdish_nation_candidate' in row['matched_categories'].split(';'):
    candidate_ids.append(row['id'])
 summary={'total':dict(tot),'source_in_kurdish_subset':dict(source_count),
          'places':dict(place_count),'kurdish_nation_candidate_ids':candidate_ids,
          'reference_counts':REFERENCE}
 with (args.out/'summary.json').open('w',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2)
 with (args.out/'comparison.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['metric','article','script','difference','note'])
  for k,ref in REFERENCE.items():
   if k=='kurdish_nation_contextual': val='manual review required'
   elif k.endswith('_in_subset') and k[:-10] in SOURCES:val=source_count[k[:-10]]
   else:val=tot.get(k,0)
   w.writerow([k,ref,val,val-ref if isinstance(val,int) else '',
     'dictionary reconstruction; compare individual posts for discrepancies'])
 print('Messages:',tot['all_messages'],'Kurdish subset:',tot['kurdish_related'])
 print('See comparison.csv for differences from the published article.')

if __name__=='__main__':main()
