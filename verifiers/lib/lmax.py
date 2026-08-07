from fractions import Fraction as F
import z3, audit

def lmax(n, v):
    """Core allocation lexicographically minimizing the maximal payoffs."""
    full = (1 << n) - 1
    x = [z3.Real(f"x{i}") for i in range(n)]
    base = [z3.Sum(x) == audit.to_z3(v[full])] + [
        z3.Sum([x[i] for i in range(n) if S >> i & 1]) >= audit.to_z3(v[S])
        for S in range(1, full)]
    pinned, free = {}, set(range(n))
    while free:
        t = z3.Real("t"); o = z3.Optimize(); o.add(base)
        for j, val in pinned.items(): o.add(x[j] == audit.to_z3(val))
        for i in free: o.add(x[i] <= t)
        h = o.minimize(t); assert o.check() == z3.sat
        lvl = audit.rat(o.lower(h))
        newly = []
        for i in sorted(free):
            o2 = z3.Optimize(); o2.add(base)
            for j, val in pinned.items(): o2.add(x[j] == audit.to_z3(val))
            for k in free: o2.add(x[k] <= audit.to_z3(lvl))
            h2 = o2.minimize(x[i]); assert o2.check() == z3.sat
            if audit.rat(o2.lower(h2)) == lvl: newly.append(i)
        assert newly
        for i in newly: pinned[i] = lvl; free.discard(i)
    return [pinned[i] for i in range(n)]

if __name__ == "__main__":
    A=(2,0,12,6,0); B=(0,0,0,0,20); P=(0,2,10,4,4)
    base=audit.envelope(5,[tuple(map(F,g)) for g in (A,B,P)])
    endp=audit.envelope(5,[tuple(map(F,g)) for g in (A,B)])
    S=29
    for name,v in (("base",base),("endpoint",endp)):
        mn=audit.lmin(5,v); mx=lmax(5,v)
        print(f"{name:9s} Lmin={[str(q) for q in mn]}  Lmax={[str(q) for q in mx]}  equal={mn==mx}")
    b=lmax(5,base); e=lmax(5,endp)
    print("Lmax drops on S={1,3,4,5}:",
          {i+1:(str(b[i]),str(e[i])) for i in range(5) if S>>i&1 and e[i]<b[i]})
    mb=audit.lmin(5,base); me=audit.lmin(5,endp)
    print("Lmin drops on S={1,3,4,5}:",
          {i+1:(str(mb[i]),str(me[i])) for i in range(5) if S>>i&1 and me[i]<mb[i]})
