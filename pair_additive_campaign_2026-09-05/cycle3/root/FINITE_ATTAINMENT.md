# One-sixth attained in a finite pair-additive market

September 5, 2026. Conventional proof and independent standard-library rational verifier. This proves finite attainment of the previously known upper bound; it does not establish a universal lower bound or priority.

## Construction

Take three blocks s=0,1,2 of players (a_s,b_s,c_s;d_s,e_s,f_s;g_s,h_s,i_s). In each block use

    A=[[0,0,0],[2,0,1],[0,1,0]],
    B=[[0,0,1],[1,0,0],[0,0,0]],
    C=[[0,1,0],[3,0,0],[2,0,0]].

Between blocks all pair weights are zero except

    A(a_0,d_1)=B(a_0,i_2)=C(d_1,i_2)=1.

No path couplers from cycle2 are included. There are27 players and27 positive pair entries. Every complete triple has value A+B+C; pairs alone have value zero.

## Matching and full-core witnesses

For each block use the matching (a,f,i), (b,d,h), (c,e,g), of values1,3,4. Its total is24. The following cover also totals24, so the matching is optimal and the full core is nonempty.

For blocks0 and2 use

    P=(1/3,4/3,5/6;5/6,5/6,1/3;7/3,5/6,1/3),

and for block1 use

    Q=(1/3,1/3,1/3;7/3,1/3,1/3;10/3,1/3,1/3).

All729 triples are covered. `verify_finite_attainment.py` constructs the matrices independently and checks every inequality using rational arithmetic, including triples containing more than one interface pair.

An ideal-attaining core allocation consists of the three block vectors

    U0=(1,2,0;0,2,0;2,1,0),
    U1=(0,2,1;1,0,0;3,0,1),
    U2=(0,2,1;0,0,0;3,1,1).

It also totals24 and passes all729 raw triple inequalities. Thus every coalition's integral matching is covered. In particular it gives b_1=2 and a_1=0.

## The full leximin coordinate

Every core allocation satisfies the three matching equalities per block. The small team a_s+f_s+i_s=1 bounds the first common floor by1/3. The cover(P,Q,P) attains this floor. On the first optimal face all small-team coordinates equal1/3.

The interface triple gives a_0+d_1+i_2>=3. Consequently on that face d_1>=7/3. Since b_1+d_1+h_1=3 and b_1,h_1>=1/3, both b_1 and h_1 are forced to1/3. Later lexicographic stages cannot change them. Hence the FULL leximin allocation satisfies x_(b_1)=1/3. No identification of every other final coordinate is needed for this proof.

## The true ideal and spread

At an arbitrary core allocation, a_0<=1 and i_2<=1 by their small matching teams and nonnegativity. The same interface triple gives d_1>=1, and then b_1+d_1+h_1=3 gives b_1<=2. The allocation(U0,U1,U2) attains2. Therefore

    H_(b_1)=2,  x_(b_1)/H_(b_1)=1/6.

Equivalently, summing the two small-team equalities and the middle matching equality, and subtracting the interface inequality, gives

    b_1+h_1+f_0+i_0+a_2+f_2<=2.

This is an exact nonnegative-term certificate for the ideal bound.

The same witness has a_1=0, so the within-sector spread defined in SECTOR_SPREAD.md satisfies R_(b_1)>=2. Since R_i<=H_i, it equals2. Thus R_(b_1)/x_(b_1)=6: this example also disproves the proposed stronger bound R_i<=3x_i. The valid sector-translation lemmas survive; their attempted bridge to one-sixth does not.

## Interpretation

The old all-size family only approached1/6. This different interface mechanism attains1/6 with finitely many players. The market-size minimum is not established, no below1/6 example follows, and universal protection remains unproved. The numerical pilot's other full-selector values and distance are separately recorded in its exact solver artifact; this independent proof promotes only the designated ratio and spread obstruction.
