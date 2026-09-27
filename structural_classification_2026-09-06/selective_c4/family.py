from fractions import Fraction as F

def construct(q):
    if not isinstance(q,int) or q<1:raise ValueError('q must be positive integer')
    m=3*q+1;L=lambda s:0 if s==0 else 3*s-1;O=lambda s:3*s-2;R=lambda s:3*s
    A=[[[0]*m for _ in range(m)]for _ in range(4)]
    for s in range(q+1):A[1][L(s)][L(s)]=1
    for s in range(1,q+1):
        o,l,r,prev=O(s),L(s),R(s),L(s-1)
        A[0][o][o]=A[0][o][r]=2
        A[3][o][o]=A[3][o][l]=2
        A[1][r][r]=A[1][r][l]=A[1][prev][o]=1
        A[2][o][o]=A[2][l][l]=2
    tau=F(1,3*(q+1));t=F(1,4*(q+1));p=[[F(0)]*m for _ in range(4)];y=[[F(0)]*m for _ in range(4)]
    for s in range(q+1):
        j=L(s);v=(tau,1-(3*s+2)*tau,(3*s+1)*tau)
        for a in range(3):p[a][j]=v[a]-t/3
        y[2][j]=1
    for s in range(1,q+1):
        j=R(s);v=(tau,1-2*tau,tau)
        for a in range(3):p[a][j]=v[a]-t/3
        y[1][j]=1
        j=O(s);v=(4-(3*s-1)*tau,tau,(3*s-2)*tau)
        for a in range(3):p[a][j]=v[a]-t/3
        y[0][j]=3;y[2][j]=1
    for j in range(m):p[3][j]=A[2][j][j]+t;y[3][j]=A[2][j][j]
    partial=[]
    for s in range(1,q+1):partial += [(O(s),R(s),L(s),L(s)),(L(s-1),L(s-1),O(s),O(s))]
    return {'q':q,'m':m,'k':4,'edges':[(0,1),(1,2),(2,3),(0,3)],'matrices':A,'T':10*q+1,'floor':str(t),'target':2*m,'target_ideal':'1','ratio':str(t),'x_floor':[str(x)for sector in p for x in sector],'y_ideal':[str(x)for sector in y for x in sector],'matching':[(j,)*4 for j in range(m)],'partial_matching':partial}
