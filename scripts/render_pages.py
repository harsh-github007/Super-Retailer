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
ACC='#455b42'; ACC2='#b58b55'; GREY='#62685d'; INK='#292e27'
plt.rcParams.update({'text.parse_math':False,'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#d6cdc0','axes.labelcolor':INK,'text.color':INK,'xtick.color':GREY,'ytick.color':GREY,'axes.facecolor':'#fffdf9','axes.titleweight':'bold','axes.titlesize':11,'axes.titlelocation':'left'})
def money(x,_=None):
    if abs(x)<1: return '$0'
    s='-' if x<0 else ''; x=abs(x)
    return f'{s}${x/1e6:.1f}M' if x>=1e6 else f'{s}${x/1e3:.0f}K'
from matplotlib.ticker import FuncFormatter
MF=FuncFormatter(money)
def page(title):
    fig=plt.figure(figsize=(12.8,7.2),dpi=100); fig.patch.set_facecolor('#f2eee7')
    fig.text(0.025,0.97,'SUPER RETAILER / HISTORICAL SALES STUDY',fontsize=8,color=GREY); fig.text(0.015,0.93,title,fontsize=16,weight='bold',color=INK)
    fig.text(0.025,0.015,'Source: SuperRetailerData · Jan 2016–Aug 2017 · Australian dollars · Public practice dataset',fontsize=7,color=GREY)
    return fig
pages=[]
# 1 Overall
fig=page('Overall summary')
rev,pro=S.Revenue.sum(),S.Profit.sum()
for i,(k,v) in enumerate([('Revenue',money(rev)),('Profit',money(pro)),('Margin',f'{pro/rev:.1%}')]):
    ax=fig.add_axes([0.015+i*0.12,0.76,0.11,0.12]); ax.axis('off'); ax.add_patch(plt.Rectangle((0,0),1,1,fc='#fffdf9',ec='#d6cdc0',transform=ax.transAxes))
    ax.text(0.08,0.62,v,fontsize=17,weight='bold',color=INK,transform=ax.transAxes); ax.text(0.08,0.2,k,fontsize=9,color=GREY,transform=ax.transAxes)
mon=S.groupby('Date').Revenue.sum().sort_index(); tgt=mon.shift(12)*1.05
ax=fig.add_axes([0.05,0.43,0.33,0.28]); ax.plot(mon.index,mon.values,color=ACC,lw=2,label='Revenue'); ax.plot(tgt.index,tgt.values,color=ACC2,lw=1.5,ls='--',label='Same month prior year +5%'); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue against target, by month'); ax.legend(frameon=False,fontsize=8); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4)); ax.xaxis.set_major_formatter(MD); ax.tick_params(axis='x',labelsize=8)
q=S.groupby('FY Qtr')[['Revenue','Profit']].sum()
ax=fig.add_axes([0.05,0.07,0.43,0.28]); x=np.arange(len(q)); ax.bar(x-0.2,q.Revenue,0.4,color=ACC,label='Revenue'); ax.bar(x+0.2,q.Profit,0.4,color=ACC2,label='Profit'); ax.set_xticks(x); ax.set_xticklabels(q.index,fontsize=8); ax.yaxis.set_major_formatter(MF); ax.set_title('Revenue and profit by financial quarter'); ax.legend(frameon=False,fontsize=8)
ch=S.groupby('Chain').Revenue.sum()
ax=fig.add_axes([0.40,0.42,0.2,0.38]); ax.pie(ch.values,labels=None,colors=[ACC,ACC2],startangle=90,wedgeprops=dict(width=0.38),textprops=dict(fontsize=9)); ax.set_title('Revenue by chain'); ax.text(0,-1.35,'\n'.join(f'{c}: {money(v)} ({v/ch.sum():.0%})' for c,v in ch.items()),ha='center',fontsize=8,color=GREY)
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
    ax.bar(d,v,bottom=cum,width=20,color='#2da44e' if v>=0 else '#cf222e'); cum+=v
ax.axhline(0,color='#d0d7de'); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(MD); ax.yaxis.set_major_formatter(MF); ax.set_title('Cumulative revenue gap vs prior-year month +5% (2017 only)')
fy = mon.index.year + (mon.index.month >= 7).astype(int)
ytd = mon.groupby(fy).cumsum()
assert np.isclose(ytd.loc['2016-07-01'], mon.loc['2016-07-01'])
assert np.isclose(ytd.loc['2017-07-01'], mon.loc['2017-07-01'])
ax=fig.add_axes([0.05,0.07,0.42,0.35]); ax.fill_between(ytd.index,ytd.values,color=ACC,alpha=0.35); ax.plot(ytd.index,ytd.values,color=ACC); ax.yaxis.set_major_formatter(MF); ax.set_title('Financial-year revenue YTD (July–June; first FY partial)'); ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(MD); ax.tick_params(axis='x',labelsize=8)
yoy=(mon/mon.shift(12)-1).dropna()
ax=fig.add_axes([0.55,0.07,0.42,0.35]); ax.bar(yoy.index.strftime('%b %y'),yoy.values*100,color=[ACC if v>=0 else '#cf222e' for v in yoy.values]); ax.set_ylabel('%'); ax.set_title('Year-on-year revenue change, by month')
pages.append(('2-date-wise-analysis',fig))
# 3 Category
fig=page('Category deep dive')
c=S.groupby('Category').agg(R=('Revenue','sum'),P=('Profit','sum'),U=('Total Units','sum')); c['M']=c.P/c.R
ax=fig.add_axes([0.07,0.09,0.88,0.76]); ax.scatter(c.R,c.M*100,s=c.U/c.U.max()*2500,color=ACC,alpha=0.55,edgecolor=ACC)
for n,r in c.iterrows(): ax.annotate(n,(r.R,r.M*100),ha='center',va='center',fontsize=9,weight='bold')
ax.xaxis.set_major_formatter(MF); ax.set_xlabel('Revenue'); ax.set_ylabel('Margin (%)'); ax.margins(y=.12); ax.set_title('Each category by revenue and margin; bubble size is units sold (the report animates this by quarter)')
pages.append(('3-category-deep-dive',fig))
# 4 Managers: margin comparison alongside territory revenue, without claiming causality.
fig=page('Manager performance / revenue and margin')
mg=S.groupby('Manager').agg(R=('Revenue','sum'),P=('Profit','sum')); mg['Margin']=mg.P/mg.R
mg=mg.sort_values('Margin')
ax=fig.add_axes([0.18,0.12,0.34,0.72]);ax.barh(mg.index,mg.R,color=ACC);ax.xaxis.set_major_formatter(MF);ax.set_title('Territory revenue')
ax2=fig.add_axes([0.65,0.12,0.30,0.72]);ax2.barh(np.arange(len(mg)),mg.Margin*100,color=ACC2);ax2.set_yticks(np.arange(len(mg)));ax2.set_yticklabels([]);ax2.set_xlabel('Profit margin (%)');ax2.set_title('Margin on the same territories')
for i,v in enumerate(mg.Margin*100):ax2.text(v+.3,i,f'{v:.1f}%',va='center',fontsize=7,color=GREY)
ax2.set_xlim(0, max(mg.Margin*100)*1.18)
fig.text(0.18,0.055,'Sorted by margin. Territory size and product mix differ; these figures are not a causal manager ranking.',fontsize=8,color=GREY)
pages.append(('4-manager-performance',fig))
# 5 Price sensitivity: volume reacts to an explicitly assumed elasticity.
fig=page('Price scenarios / revenue is not profit')
rev,pro=S.Revenue.sum(),S.Profit.sum();cost=rev-pro
prices=np.linspace(-.2,.2,81)
for rect,metric,title in [([.07,.35,.40,.48],'revenue','Revenue response'),([.56,.35,.40,.48],'profit','Profit response')]:
    ax=fig.add_axes(rect)
    for elasticity,color in [(0,ACC),(-1,ACC2),(-1.5,GREY)]:
        volume=(1+prices)**elasticity
        values=rev*(1+prices)*volume if metric=='revenue' else (rev*(1+prices)-cost)*volume
        ax.plot(prices*100,values/1e6,color=color,lw=2,label=f'Elasticity {elasticity:g}')
    ax.axvline(0,color='#bdb7ac',lw=1,ls=':');ax.set_xlabel('Uniform price change (%)');ax.set_ylabel('AUD millions');ax.set_title(title);ax.legend(frameon=False,fontsize=8)
fig.text(.07,.24,'ASSUMPTIONS, NOT A FORECAST',fontsize=9,color=ACC,weight='bold')
fig.text(.07,.19,'Volume multiplier = (1 + price change) ^ elasticity. Unit costs remain fixed; all products change uniformly.',fontsize=9,color=GREY)
fig.text(.07,.145,f'Baseline: {money(rev)} revenue / {money(pro)} profit. At +10% price and elasticity −1: revenue unchanged;',fontsize=9,color=INK)
simprofit=(rev*1.1-cost)/1.1
fig.text(.07,.10,f'profit becomes {money(simprofit)} ({simprofit/pro-1:+.1%}). Real elasticity is not estimated by this dataset.',fontsize=9,color=INK)
assert np.isclose(rev*1.1*(1.1**-1),rev)
pages.append(('5-price-simulation',fig))
with PdfPages('Super Retailer Report.pdf') as pdf:
    for name,f in pages:
        f.savefig(f'pages/{name}.png'); pdf.savefig(f); plt.close(f)
print('done', rev, pro)
