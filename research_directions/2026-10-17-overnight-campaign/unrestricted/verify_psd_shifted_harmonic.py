from fractions import Fraction as F

cases=0
for m in range(2,81):
    for denom in range(2,31):
        for num in range(denom):
            theta=F(num,denom); c=1-theta
            for epsilon in [F(1,100),F(1,3),F(1),F(7)]:
                D=1/(c+epsilon)+F(m-1)/c
                payment=(1+epsilon)/(c+epsilon)/D
                difference=payment-F(1,m)
                expected=epsilon*(1-m*theta)/(m*(m*c+(m-1)*epsilon))
                assert difference==expected
                assert (difference<0)==(theta>F(1,m))
                cases+=1
    assert m*(1-F(1,m))+F(1,m)==m-1+F(1,m)
print(f'PASS: {cases} exact shifted-harmonic comparisons; threshold theta<=1/m.')
