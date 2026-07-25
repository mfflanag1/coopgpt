from fractions import Fraction as F
from tugame import Game
from leximin import leximin_core_exact
from lemD import binding_bumpable, star_holds, max_exact_bump, core_max_xS, xS
def members(S,n): return [i for i in range(n) if S>>i&1]
# the two star-failing exact games from exploration
g1v=['0','0','2','3','0','1','2','3','1','1','4','5','2','2','4','5','0','0','4','5','1','1','4','5','1','1','6','6','2','2','6','7']
g2v=['0','0','1','2','1','2','2','3','1','1','4','4','3','3','6','6','6','7','7','8','7','8','8','9','12','12','15','15','14','14','16','17']
for gv,Ss in [(g1v,[0b1101,0b10111,0b11011,0b11110]),(g2v,[0b111,0b11011])]:
    g=Game(5,[F(x) for x in gv]); phi=leximin_core_exact(g)
    print("phi",[str(p) for p in phi])
    for S in Ss:
        h,val,y=star_holds(g,phi,S)
        db=max_exact_bump(g,S)
        print(f"  S={members(S,5)} star_holds={h} maxcore_xS={core_max_xS(g,S)} phi(S)={xS(phi,S,5)} max_exact_bump={db}")
