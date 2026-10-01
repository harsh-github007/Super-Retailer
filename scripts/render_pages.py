"""Redraw the five report pages as PNGs and a PDF from the data inside Super Retailer Report.pbix.

    pip install pbixray pandas matplotlib
    python scripts/render_pages.py
"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
MD=mdates.DateFormatter('%b %y')
from matplotlib.backends.backend_pdf import PdfPages
from pbixray import PBIXRay
m=PBIXRay('Super Retailer Report.pbix')
S=m.get_table('Sales'); D=m.get_table('Dates'); R=m.get_table('Regions'); M=m.get_table('Managers')
S['Date']=pd.to_datetime(S['Date']); D['Date']=pd.to_datetime(D['Date'])
S=S.merge(D,on='Date',how='left').merge(R[['Postcode','State']],on='Postcode',how='left').merge(M[['Postcode','Manager']],on='Postcode',how='left')
ACC='#1f6feb'; ACC2='#f2994a'; GREY='#8a8f98'; INK='#1f2328'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#d0d7de','axes.titleweight':'bold','axes.titlesize':11,'axes.titlelocation':'left'})
def money(x,_=None):
    if abs(x)<1: return '$0'
    s='-' if x<0 else ''; x=abs(x)
    return f'{s}${x/1e6:.1f}M' if x>=1e6 else f'{s}${x/1e3:.0f}K'
from matplotlib.ticker import FuncFormatter
MF=FuncFormatter(money)
def page(title):
    fig=plt.figure(figsize=(12.8,7.2),dpi=100); fig.patch.set_facecolor('white')
    fig.text(0.015,0.965,'Super Retailer',fontsize=9,color=GREY); fig.text(0.015,0.93,title,fontsize=16,weight='bold',color=INK)
    return fig
pages=[]
# 1 Overall
fig=page('Overall summary')
rev,pro=S.Revenue.sum(),S.Profit.sum()
for i,(k,v) in enumerate([('Revenue',money(rev)),('Profit',money(pro)),('Margin',f'{pro/rev:.1%}')]):
    ax=fig.add_axes([0.015+i*0.12,0.76,0.11,0.12]); ax.axis('off'); ax.add_patch(plt.Rectangle((0,0),1,1,fc='#f6f8fa',ec='#d0d7de',transform=ax.transAxes))
    ax.text(0.08,0.62,v,fontsize=17,weight='bold',color=INK,transform=ax.transAxes); ax.text(0.08,0.2,k,fontsize=9,color=GREY,transform=ax.transAxes)
mon=S.groupby('Date').Revenue.sum(); tgt=mon.shift(1)*1.05
ax=fig.add_axes([0.05,0.43,0.33,0.28]); ax.plot(mon.index,mon.values,color=ACC,lw=2,label='Revenue'); ax.plot(tgt.index,tgt.values,color=ACC2,lw=1.5,ls='--',label='Target (last month +5%)'); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue against target, by month'); ax.legend(frameon=False,fontsize=8); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4)); ax.xaxis.set_major_formatter(MD); ax.tick_params(axis='x',labelsize=8)
q=S.groupby('FY Qtr')[['Revenue','Profit']].sum()
ax=fig.add_axes([0.05,0.07,0.43,0.28]); x=np.arange(len(q)); ax.bar(x-0.2,q.Revenue,0.4,color=ACC,label='Revenue'); ax.bar(x+0.2,q.Profit,0.4,color=ACC2,label='Profit'); ax.set_xticks(x); ax.set_xticklabels(q.index,fontsize=8); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue and profit by financial quarter'); ax.legend(frameon=False,fontsize=8)
ch=S.groupby('Chain').Revenue.sum()
ax=fig.add_axes([0.40,0.42,0.2,0.38]); ax.pie(ch.values,labels=[f'{c}\n{money(v)} ({v/ch.sum():.0%})' for c,v in ch.items()],colors=[ACC,ACC2],startangle=90,wedgeprops=dict(width=0.38),textprops=dict(fontsize=9)); ax.set_title('Revenue by chain')
cu=S.groupby('Category')['Total Units'].sum().sort_values()
ax=fig.add_axes([0.70,0.42,0.28,0.48]); ax.barh(cu.index,cu.values,color=ACC); ax.set_title('Units sold by category'); ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v/1e3:.0f}K'))
st=S.groupby('State').Revenue.sum().sort_values(ascending=False)
ax=fig.add_axes([0.56,0.07,0.42,0.28]); ax.bar(st.index,st.values,color=ACC); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue by state (a map in the report)')
pages.append(('1-overall-summary',fig))
# 2 Date-wise
fig=page('Date-wise analysis')
var=(mon-tgt).dropna()
ax=fig.add_axes([0.05,0.52,0.92,0.33]); cum=0
for d,v in var.items():
    ax.bar(d,v,bottom=cum if v>=0 else cum+v,width=20,color='#2da44e' if v>=0 else '#cf222e'); cum+=v
ax.axhline(0,color='#d0d7de'); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(MD); ax.yaxis.set_major_formatter(MF); ax.set_title('Monthly revenue against target: running total of the gap (waterfall)')
ytd=S.assign(Y=S.Date.dt.year).groupby(['Y','Date']).Revenue.sum().groupby(level=0).cumsum().droplevel(0)
ax=fig.add_axes([0.05,0.07,0.42,0.35]); ax.fill_between(ytd.index,ytd.values,color=ACC,alpha=0.35); ax.plot(ytd.index,ytd.values,color=ACC); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue, year to date (calendar year, as in the report)'); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(MD); ax.tick_params(axis='x',labelsize=8)
yoy=(mon/mon.shift(12)-1).dropna()
ax=fig.add_axes([0.55,0.07,0.42,0.35]); ax.bar(yoy.index.strftime('%b %y'),yoy.values*100,color=[ACC if v>=0 else '#cf222e' for v in yoy.values]); ax.set_ylabel('%'); ax.set_title('Year-on-year revenue change, by month')
pages.append(('2-date-wise-analysis',fig))
# 3 Category
fig=page('Category deep dive')
c=S.groupby('Category').agg(R=('Revenue','sum'),P=('Profit','sum'),U=('Total Units','sum')); c['M']=c.P/c.R
ax=fig.add_axes([0.07,0.09,0.88,0.76]); ax.scatter(c.R,c.M*100,s=c.U/c.U.max()*2500,color=ACC,alpha=0.55,edgecolor=ACC)
for n,r in c.iterrows(): ax.annotate(n,(r.R,r.M*100),ha='center',va='center',fontsize=9,weight='bold')
ax.xaxis.set_major_formatter(MF); ax.set_xlabel('Revenue'); ax.set_ylabel('Margin (%)'); ax.set_title('Each category by revenue and margin; bubble size is units sold (the report animates this by quarter)')
pages.append(('3-category-deep-dive',fig))
# 4 Managers
fig=page('Manager performance')
mg=S.groupby('Manager').Revenue.sum().sort_values()
ax=fig.add_axes([0.2,0.07,0.75,0.78]); ax.barh(mg.index,mg.values,color=ACC); ax.xaxis.set_major_formatter(MF); ax.set_title('Revenue by store manager (the report drills down to suburb)')
for i,v in enumerate(mg.values): ax.text(v,i,' '+money(v),va='center',fontsize=8,color=GREY)
pages.append(('4-manager-performance',fig))
# 5 Price simulation
fig=page('Price simulation')
pc,uc=0.10,-0.10
fig.text(0.015,0.88,f'Example settings: price +{pc:.0%}, units {uc:+.0%}. In the report both are sliders (price ±20%, units ±40%).',fontsize=10,color=GREY)
g=S.assign(Sim=S['Sale Price']*(1+pc)*S['Total Units']*(1+uc)).groupby('Category').agg(Cur=('Revenue','sum'),Sim=('Sim','sum'),U=('Total Units','sum')).sort_values('Cur',ascending=False)
ax=fig.add_axes([0.06,0.09,0.86,0.72]); x=np.arange(len(g)); ax.bar(x-0.2,g.Cur,0.4,color=ACC,label='Current revenue'); ax.bar(x+0.2,g.Sim,0.4,color=ACC2,label='Simulated revenue'); ax.set_xticks(x); ax.set_xticklabels(g.index); ax.yaxis.set_major_formatter(MF)
ax2=ax.twinx(); ax2.plot(x,g.Cur/g.U,color=INK,marker='o',label='Average sale price'); ax2.set_ylabel('Average sale price ($)'); ax2.spines['top'].set_visible(False)
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax.legend(h1+h2,l1+l2,frameon=False,fontsize=9,loc='upper right'); ax.set_title('Current and simulated revenue by category')
pages.append(('5-price-simulation',fig))
with PdfPages('Super Retailer Report.pdf') as pdf:
    for name,f in pages:
        f.savefig(f'pages/{name}.png'); pdf.savefig(f); plt.close(f)
print('done', rev, pro)
