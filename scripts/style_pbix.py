"""Apply presentation-only styling; preserve the embedded model byte for byte."""
import hashlib,json,shutil,zipfile
from pathlib import Path
p=Path('Super Retailer Report.pbix')
backup=Path('/tmp/super-retailer-original.pbix')
if not backup.exists(): shutil.copy2(p,backup)
def literal(v): return {'expr':{'Literal':{'Value':v}}}
def color(v): return {'solid':{'color':literal("'"+v+"'")}}
with zipfile.ZipFile(p) as z:
 entries=[(i,z.read(i.filename)) for i in z.infolist()]
original=dict((i.filename,b) for i,b in entries)
l=json.loads(original['Report/Layout'].decode('utf-16-le'))
theme_path='Report/StaticResources/SharedResources/BaseThemes/CY22SU11.json'
t=json.loads(original[theme_path])
t.update(dataColors=['#455B42','#B58B55','#798A73','#786653','#A8B39F','#D3B78F'],foreground='#292E27',foregroundNeutralSecondary='#62685D',background='#FFFDF9',backgroundLight='#F2EEE7',backgroundNeutral='#D8D6CD',tableAccent='#455B42',good='#455B42',bad='#A65D50',maximum='#455B42',minimum='#DDE4D8')
for c in t['textClasses'].values(): c.update(fontFace='Segoe UI',color='#292E27')
count=0
for s in l['sections']:
 c=json.loads(s['config']);o=c.setdefault('objects',{})
 o['background']=[{'properties':{'color':color('#F2EEE7'),'transparency':literal('0D')}}]
 o['outspace']=[{'properties':{'color':color('#F2EEE7')}}]
 s['config']=json.dumps(c,separators=(',',':'))
 for v in s['visualContainers']:
  c=json.loads(v['config']);sv=c.get('singleVisual')
  if not sv: continue
  if sv.get('visualType') not in ('actionButton','textbox'):
   o=sv.setdefault('vcObjects',{})
   o['dropShadow']=[{'properties':{'show':literal('false')}}]
   o['border']=[{'properties':{'show':literal('true'),'radius':literal('8D'),'color':color('#D8D6CD')}}]
   o['background']=[{'properties':{'show':literal('true'),'color':color('#FFFDF9'),'transparency':literal('0D')}}]
   for title in o.get('title',[]):
    title['properties'].update(fontColor=color('#292E27'),fontFamily=literal("'Segoe UI'"))
   count+=1
  # Replace explicit neon gradient endpoints without changing the measure/selector.
  def recolor(x):
   if isinstance(x,dict):
    for k,val in x.items():
     if k=='Value' and isinstance(val,str):
      x[k]={'\'#F80000\'':"'#D3B78F'",'\'#00FF51\'':"'#455B42'"}.get(val,val)
     else: recolor(val)
   elif isinstance(x,list):
    for val in x: recolor(val)
  recolor(sv)
  v['config']=json.dumps(c,separators=(',',':'))
updated={'Report/Layout':json.dumps(l,separators=(',',':'),ensure_ascii=False).encode('utf-16-le'),theme_path:json.dumps(t,separators=(',',':')).encode()}
new=p.with_suffix('.tmp')
with zipfile.ZipFile(new,'w',zipfile.ZIP_DEFLATED) as z:
 for info,data in entries: z.writestr(info,updated.get(info.filename,data))
with zipfile.ZipFile(new) as z:
 assert z.testzip() is None
 assert z.read('DataModel')==original['DataModel']
 assert len(json.loads(z.read('Report/Layout').decode('utf-16-le'))['sections'])==5
 for name,data in original.items():
  if name not in updated: assert z.read(name)==data
new.replace(p)
print(f'Styled {count} visuals across 5 pages; DataModel SHA256 {hashlib.sha256(original["DataModel"]).hexdigest()} unchanged.')
