#!/usr/bin/env python3
"""Plot seven reconstructed figure series from analyze_article.py outputs.
These plots show this script's coding, not the article's original figure data.
"""
import argparse
import csv
from pathlib import Path
import matplotlib.pyplot as plt


def rows(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def n(row,key):return int(row.get(key) or 0)

def save(path):
 plt.tight_layout();plt.savefig(path,dpi=200,bbox_inches='tight');plt.close()

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('analysis_dir',type=Path)
 ap.add_argument('--out',type=Path,default=Path('figures'))
 a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 annual=rows(a.analysis_dir/'annual_visibility.csv')
 years=[r['year'] for r in annual]
 counts=[n(r,'kurdish_related') for r in annual]
 rates=[100*n(r,'kurdish_related')/n(r,'all_messages') for r in annual]
 fig,ax=plt.subplots(figsize=(8,4));ax.bar(years,counts,color='#356ca0')
 for i,(v,p) in enumerate(zip(counts,rates)):ax.text(i,v+max(counts)*.015,f'{p:.1f}%',ha='center',fontsize=8)
 ax.set_ylabel('Matched posts');ax.set_title('Figure 1 reconstruction: Kurdish-related post screen')
 save(a.out/'figure_1_visibility.png')
 fig,ax=plt.subplots(figsize=(8,4))
 for field in ['agency','victimhood','security']:
  ax.plot(years,[100*n(r,field)/max(1,n(r,'kurdish_related')) for r in annual],marker='o',label=field.title())
 ax.set_ylabel('% of matched posts');ax.legend();ax.set_title('Figure 2 reconstruction: vocabulary frames')
 save(a.out/'figure_2_frames.png')
 import json
 summary=json.loads((a.analysis_dir/'summary.json').read_text(encoding='utf-8'))['total']
 fig,ax=plt.subplots(figsize=(7,4))
 labels=['Iranian nation','Kurdish nation candidate'];vals=[summary.get('iranian_nation',0),summary.get('kurdish_nation_candidate',0)]
 ax.bar(labels,vals,color=['#356ca0','#cb6730']);ax.set_ylabel('Posts')
 ax.set_title('Figure 3 reconstruction: raw phrase candidates')
 save(a.out/'figure_3_nation_names.png')
 ns=rows(a.analysis_dir/'names_and_slogans.csv');ys=[r['year'] for r in ns]
 jina=[100*n(r,'jina')/max(1,n(r,'jina')+n(r,'mahsa')) for r in ns]
 slogan=[100*n(r,'kurdish_slogan')/max(1,n(r,'kurdish_slogan')+n(r,'persian_slogan')) for r in ns]
 fig,ax=plt.subplots(figsize=(8,4));ax.plot(ys,jina,marker='o',label='Jina share of name matches')
 ax.plot(ys,slogan,marker='o',label='Kurdish slogan share');ax.set_ylabel('% of matched posts')
 ax.legend();ax.set_title('Figure 4 reconstruction: names and slogans')
 save(a.out/'figure_4_names_slogans.png')
 py=rows(a.analysis_dir/'party_year.csv');fig,ax=plt.subplots(figsize=(8,4))
 for k in ['kdpi','komala','pjak']:ax.plot([r['year'] for r in py],[n(r,k) for r in py],marker='o',label=k.upper())
 ax.legend();ax.set_ylabel('Posts');ax.set_title('Figure 5 reconstruction: party mentions')
 save(a.out/'figure_5_parties.png')
 pf=rows(a.analysis_dir/'party_frames.csv');fields=['agency','victimhood','security','attacks','statements','terrorist']
 fig,ax=plt.subplots(figsize=(9,4));x=list(range(len(fields)));w=.25
 for j,r in enumerate(pf):
  ax.bar([i+(j-1)*w for i in x],[100*n(r,k)/max(1,n(r,'posts')) for k in fields],w,label=r['party'].upper())
 ax.set_xticks(x,fields,rotation=18);ax.set_ylabel('% of party posts');ax.legend()
 ax.set_title('Figure 6 reconstruction: party vocabulary')
 save(a.out/'figure_6_party_frames.png')
 sources=rows(a.analysis_dir/'sources.csv');fig,ax=plt.subplots(figsize=(8,4))
 ax.bar([r['source'] for r in sources],[n(r,'posts') for r in sources],color='#356ca0')
 ax.tick_params(axis='x',rotation=25);ax.set_ylabel('Posts in matched subset')
 ax.set_title('Figure 7 reconstruction: named organisations')
 save(a.out/'figure_7_sources.png')
 print('Wrote seven reconstructed figures to',a.out)

if __name__=='__main__':main()
