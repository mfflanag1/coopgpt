# Closing the transfer path does not amplify the designated loss

September 5, 2026. Conventional deduction for the specific coupled-block family; not a general theorem about cyclic pair-additive markets.

Take q>=2 of the original nine-player blocks and include A(c_s,d_{s+1})=2 cyclically, with indices modulo q. The same block matching has weight8q. The two constant block vectors below cover every local triple, every noncoupler mixed triple, and every coupler slice, so the integral total is8q and the core is nonempty.

At every core point, the local weight4 triple (b_s,e_s,g_s) and matching equality c_s+e_s+g_s=4 give b_s>=c_s. Each incoming weight3 coupling triple gives c_{s-1}>=b_s. Chaining these inequalities around the ring forces all b_s and c_s to have one common value.

The local weight4 triple (b_s,f_s,g_s) then gives e_s<=f_s. Since a_s+f_s+i_s=1 with nonnegative payoffs, H_{e_s}<=1. Repeating

    P=(0,1,1; 1,1,1; 2,1,0)

attains e_s=1 for every block. It covers all within-block pair contributions except B_ai=1, which is covered by the global second-sector floor1. Every coupler has c_prev+d_next=2 and h_next=1, so all its slices are covered. Hence H_{e_s}=1.

Repeating

    F=(1/3,1,1; 1,1/3,1/3; 8/3,1,1/3)

is another entire-core cover. Every coordinate is at least1/3. Its local matching totals are1,3,4; all positive within-block pair sums are at least the pair value minus1/3. Coupler sums satisfy c_prev+d_next=2 and c_prev+d_next+h_next=3. Thus the first leximin floor is exactly1/3. It fixes every a_s,f_s,i_s to1/3, and e_s<=f_s forces every e_s to1/3 too. Subsequent full lexicographic stages preserve these coordinates.

Therefore, for these designated players,

    x_{e_s}/H_{e_s}=1/3.

Closing the open path removes the large ideal-payoff witness that made its asymptotic1/6 loss possible. It is not a route to vanishing individual protection. No claim is made here about other players' ratios or either full selector's total distance.
