# -*- coding: utf-8 -*-
import math, sys, io
import scipy
from scipy import stats
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
L=[]
def nc(k1,n1,k2,n2,lab):
    p1,p2=k1/n1,k2/n2
    l1=stats.beta.ppf(0.05,k1,n1-k1+1) if k1>0 else 0.0
    u1=stats.beta.ppf(0.95,k1+1,n1-k1) if k1<n1 else 1.0
    l2=stats.beta.ppf(0.05,k2,n2-k2+1) if k2>0 else 0.0
    u2=stats.beta.ppf(0.95,k2+1,n2-k2) if k2<n2 else 1.0
    lo=(p1-p2)-math.sqrt((p1-l1)**2+(u2-p2)**2)
    hi=(p1-p2)+math.sqrt((u1-p1)**2+(p2-l2)**2)
    L.append('%s: Newcombe hybrid-score 90%% CI = %+.1f to %+.1f pp' % (lab,100*lo,100*hi))
nc(46,84,42,81,'OLD GTEx   (published -9.7 to +15.4)')
nc(46,84,47,81,'NEW GTEx   (to report)')
nc(44,84,38,72,'eQTLGen    (published -13.3 to +12.6)')
# TOST validation
def tost(k1,n1,k2,n2,m):
    p1,p2=k1/n1,k2/n2; d=p1-p2; se=math.sqrt(p1*(1-p1)/n1+p2*(1-p2)/n2)
    return max(1-stats.norm.cdf((d+m/100)/se), 1-stats.norm.cdf((m/100-d)/se))
L.append('')
L.append('TOST OLD GTEx  +/-10/15/20 = %.3f / %.3f / %.3f   (published 0.181 / 0.060 / 0.014)'%(tost(46,84,42,81,10),tost(46,84,42,81,15),tost(46,84,42,81,20)))
L.append('TOST NEW GTEx  +/-10/15/20 = %.3f / %.3f / %.3f'%(tost(46,84,47,81,10),tost(46,84,47,81,15),tost(46,84,47,81,20)))
L.append('TOST eQTLGen   +/-10/15/20 = %.3f / %.3f / %.3f   (published 0.116 / 0.034 / 0.007)'%(tost(44,84,38,72,10),tost(44,84,38,72,15),tost(44,84,38,72,20)))
L.append('\nscipy %s | matplotlib: %s'%(scipy.__version__, __import__('importlib').util.find_spec('matplotlib') is not None))
open(r"E:\workbuddy\2026-09-11-19-30-45\ci_check.txt",'w',encoding='utf-8').write("\n".join(L))
print('ok')
