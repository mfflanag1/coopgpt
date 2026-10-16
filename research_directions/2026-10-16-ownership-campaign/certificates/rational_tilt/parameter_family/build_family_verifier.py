from pathlib import Path
BASE=Path(__file__).parent
s=(BASE.parent/'quarter_shape'/'verify_quarter_shape.py').read_text()
def rep(a,b):
 global s
 if a not in s:raise RuntimeError('missing '+a[:80])
 s=s.replace(a,b)
rep("BASE = Path(__file__).parent", "BASE = Path(__file__).parent\nA0 = Q(4, 45)")
rep("'dominant_long_bounds': 0, 'negative_controls': 0}","'dominant_long_bounds': 0, 'family_shape_bounds': 0, 'family_profile_checks': 0, 'negative_controls': 0}")
rep('def f(s):\n    s = Q(s)\n    return Q(0) if s <= Q(2, 3) else 2*(3*s-2)**2/(5*(9*s-5))','def f(s, a=A0):\n    s = Q(s)\n    v = 3*s-2\n    return Q(0) if v <= 0 else v*v/(10*(a+(1-a)*v))')
rep('def df(s):\n    s = Q(s)\n    return Q(0) if s <= Q(2, 3) else Q(2, 5)*(1-1/(9*s-5)**2)','def df(s, a=A0):\n    s = Q(s)\n    v = 3*s-2\n    return Q(0) if v <= 0 else Q(3, 10)*v*(2*a+(1-a)*v)/(a+(1-a)*v)**2')
rep('-972*s**4+2394*s**3-2421*s**2+1148*s-205','-3321*s**4+9122*s**3-10019*s**2+5092*s-988')
rep('def rule(reports, scale=Q(1)):','def rule(reports, scale=Q(1), a=A0):')
rep('scale*(f(L/D)-f(M/A))','scale*(f(L/D, a)-f(M/A, a))')
rep("Q('1.1291743487400027') < lower < upper < Q('1.1291743487400029')","Q('1.1288005100532478') < lower < upper < Q('1.1288005100532480')")
rep('Q(1, 2)-v*(1+v)/(1+3*v)**2','Q(1, 2)-v*(2-3*A0)*(2*A0+(1-2*A0)*v)/(10*(A0+(1-A0)*v)**2)')
rep("require(df(t)*t*(1-t) <= Q(8, 15)*v*(1-v), ('long nonmaximum bound', t))", "require(df(t)*t*(1-t) <= (Q(1, 2)+f(t))*3*v/(2*v+1), ('critical long inequality', t))")
rep('K = h*(1+s-3*R)-Q(6, 5)*(1-2*R)*(5-4*R)*R*(1+s-R)/((1+R)**2*(4-5*R)**2)','K = h*(1+s-3*R)-df(1/(1+R))*R*(1+s-R)/(1+R)**2')
rep("require(K >= Q(4, 15)*(1-2*R), ('active dominant-long derivative', s, R))", "require(K >= 0, ('active dominant-long derivative', s, R))")
rep('quarter-shape-verification.json','parameter-family-verification.json')
pos=s.index("    result = {'status':")
s=s[:pos]+'''    for k in range(101):
        a = A0+(Q(2, 3)-A0)*Q(k, 100)
        for j in range(1, 101):
            v = Q(j, 100)
            t = (v+2)/3
            D = a+(1-a)*v
            C = a*(45*a-4)+(-90*a*a+86*a-2)*v+(45*a*a-72*a+42)*v*v+(12-8*a)*v**3+2*(1-a)*v**4
            expanded = 9*D*(5*D+v*v)-(2*a+(1-a)*v)*(v+2)*(1-v)*(2*v+1)
            require(C == expanded >= 0, ('critical polynomial identity', a, v))
            require(df(t, a)*t*(1-t) <= Q(1, 16), ('uniform shape bound', a, t))
            if t < 1:
                balance = (1+t)*(f(1,a)-f(t,a))/(1-t)-t*df(t,a)
                expected = Q(1,2)-v*(2-3*a)*(2*a+(1-2*a)*v)/(10*D*D)
                require(balance == expected <= Q(1,2), ('family balance identity',a,t))
            COUNTS['family_shape_bounds'] += 1
    for trial in range(2500):
        a = A0+(Q(2,3)-A0)*Q(rng.randrange(101),100)
        n = 2+trial%7
        r = tuple((Q(rng.randrange(25), rng.randrange(1,14)),
                   Q(rng.randrange(25), rng.randrange(1,14))) for _ in range(n))
        y = rule(r,a=a)
        i,j = rng.randrange(n),rng.randrange(2)
        high = [list(row) for row in r]
        high[i][j] += Q(1,rng.choice([10,100,10000]))
        high = tuple(tuple(row) for row in high)
        require(rule(high,a=a)[i] >= y[i], ('family mixed own increment',a,r,high,i))
        T = min(sum(row[j] for row in r) for j in(0,1))
        require(sum(y) <= Q(1131,1000)*T, ('family coarse funding diagnostic',a,r))
        COUNTS['family_profile_checks'] += 1
    # Exact fixed-four-owner witnesses outside both parameter endpoints.
    low_a = Q(1,12)
    Rlow = Q(1,2)-Q(1,10**6)
    Rhigh = Rlow+Q(1,10**8)
    lowr = ((Q(1,2),Q(0)),(Q(1,2),Q(0)),(Q(0),Q(1)),(Q(0),Rlow))
    highr = lowr[:-1]+((Q(0),Rhigh),)
    lower_gap = rule(highr,a=low_a)[3]-rule(lowr,a=low_a)[3]
    require(lower_gap < 0, 'lower parameter obstruction')
    upper_a = Q(3,4)
    highr2 = ((Q(3,4),Q(0)),(Q(1,4),Q(0)),(Q(0),Q(999999,10**6)),(Q(0),Q(1,10**6)))
    lowr2 = ((Q(3,4)-Q(1,10**9),Q(0)),)+highr2[1:]
    upper_gap = rule(highr2,a=upper_a)[0]-rule(lowr2,a=upper_a)[0]
    require(upper_gap < 0, 'upper parameter obstruction')
    COUNTS['negative_controls'] += 2
''' +s[pos:]
rep("'over_scaled_negative_control': {'scale': '11/10', 'high_minus_low_payment': str(gap)}}", "'over_scaled_negative_control': {'scale': '11/10', 'high_minus_low_payment': str(gap)},\n              'lower_parameter_obstruction': {'a':str(low_a),'R_low':str(Rlow),'R_high':str(Rhigh),'high_minus_low_payment':str(lower_gap)},\n              'upper_parameter_obstruction': {'a':str(upper_a),'high_minus_low_payment':str(upper_gap)}}")
(BASE/'verify_parameter_family.py').write_text(s)
