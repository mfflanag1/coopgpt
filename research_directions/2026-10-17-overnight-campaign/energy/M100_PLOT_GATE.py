"""Plot recorded descriptive summaries only; no raw telemetry is redistributed."""
from pathlib import Path
import datetime,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
B=Path('/private/tmp/coopgpt-overnight-20261017')
d=json.loads((B/'checks/M100_PANEL_SUPPLEMENT.json').read_text());p=json.loads((B/'checks/M100_PANEL_INSPECTION.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans','figure.facecolor':'white'})
fig,(a,b)=plt.subplots(2,1,figsize=(11.5,7.8),layout='constrained',gridspec_kw={'height_ratios':[1.2,1]})
alltimes=[x['t'] for x in d['timeline']];grid=list(range(min(alltimes),max(alltimes)+1,20000));dates=[datetime.datetime.fromtimestamp(t/1000,datetime.timezone.utc)for t in grid]
for metric,color,label in [('psu_sum','#17665e','Both PSU inputs available'),('total_power','#6e55ad','total_power available')]:
 counts={x['t']:x['nodes']for x in d['timeline']if x['metric']==metric}
 a.plot(dates,[100*counts.get(t,0)/980 for t in grid],lw=.8,color=color,alpha=.9,label=label)
a.set_ylabel('Nodes with a recorded value (%)');a.set_ylim(-3,103);a.set_title('A simultaneous panel exists, but the released interval is incomplete',loc='left',fontweight='bold')
a.xaxis.set_major_locator(mdates.HourLocator(interval=12));a.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M',tz=datetime.timezone.utc));a.legend(loc='upper right',frameon=True,facecolor='white',edgecolor='none',framealpha=.95,fontsize=9)
a.annotate('No records in these files\nfor >51 hours',(mdates.date2num(datetime.datetime(2020,4,2,12,tzinfo=datetime.timezone.utc)),3),ha='center',xytext=(0,35),textcoords='offset points',fontsize=10,color='#465064')
a.grid(axis='y',alpha=.15);a.set_xlabel('UTC • April 2020 archive; 20-second grid • zero means no record, not zero power')
xs=np.array([x['delta_w']for x in d['delta_histogram']]);ys=np.array([x['n']for x in d['delta_histogram']]);b.bar(xs,ys/ys.sum()*100,width=9,color='#17665e',alpha=.85)
b.axvline(0,color='#6e55ad',lw=1.4,ls='--');b.set_title('The two meter definitions are not interchangeable',loc='left',fontweight='bold')
b.set_xlabel('total_power − (PSU0 input + PSU1 input), watts');b.set_ylabel('Same-time triples (%)');b.grid(axis='y',alpha=.15)
b.text(.98,.92,f"{p['triples']['n']:,} same-node/time triples\nMean difference: {p['triples']['mean_delta_w']:.1f} W\nMedian: {p['triples']['median_delta_w']:.0f} W\nExact equality: {100*p['triples']['equal_values']/p['triples']['n']:.3f}%",ha='right',va='top',transform=b.transAxes,fontsize=10)
fig.suptitle('M100 public power-data intake • descriptive gate',x=.085,ha='left',fontsize=17,fontweight='bold')
fig.text(.085,-.025,'Source: Zenodo 7588815, complete April target members. No state, ownership, reliability or pooling inference.',fontsize=9,color='#465064')
for ext in ['png','svg']:
 fig.savefig(B/'handoff'/('m100-data-gate.'+ext),dpi=160,bbox_inches='tight')
print('Saved descriptive figure from recorded summaries')
