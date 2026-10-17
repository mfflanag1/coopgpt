from fractions import Fraction as Q
if not __debug__:
    raise RuntimeError('Assertions required: run without Python -O')
checks=0
for m in range(1,101):
 for k in range(1,101):
  if m+k==1:continue
  a=Q(m,m+k);b=Q(1,m+k);R=a*a+m*k*b*b
  assert a+k*b==1 and R==Q(m,m+k)
  # Group KKT multipliers b: center load mb=a, leaf load b.
  assert m*b==a and m*b==R
  Rdel=Q(m-1,m+k-1)
  delta=R-Rdel
  assert delta==Q(k,(m+k)*(m+k-1))
  D=(1+m*k)*R-m*k*Rdel
  assert D==Q(m,m+k)+Q(m*k*k,(m+k)*(m+k-1))
  if m==k:
   assert D==Q(1,2)+Q(m*m,2*(2*m-1))
  # Leaf-underreport formula at exact sampled breakpoints.
  for u in (Q(0),Q(m-1,m+k-1),Q(1,2),Q(1)):
   own=max(Q(0),((m+k-1)*u-(m-1))/Q(k*(m+k)))
   assert 0<=own<=b
  checks+=1
assert Q(1,2)+Q(4,6)==Q(7,6)
print(f'PASS {checks} exact family and KKT checks; asymptotic rate analytic')
