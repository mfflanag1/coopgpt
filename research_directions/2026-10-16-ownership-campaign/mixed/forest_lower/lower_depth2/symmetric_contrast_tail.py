from symmetric_two_pool import solve
for m,h in [(2,10),(3,9),(4,12),(6,18),(3,4),(3,5),(4,2),(4,3)]:
 try:solve(m,h)
 except ValueError as err:print('CHECK FAILED:',m,h,err,flush=True)
