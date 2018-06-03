import numpy as np

"""
Inspired by this snippet: http://code.activestate.com/recipes/542190-rational-approximations
"""


def chain(x):
    """Generate continued fraction approximations for x
    """
    while True:
        a = int(x)
        x = 1/(x-a)
        yield a



def eval_chain(fractions):
    """Compute best rational approximation of a continued fraction
    """
    n1, n2 = 1, 0
    d1, d2 = 0, 1
    for a in fractions:

        for b in np.arange((a+1)/2, a+1, dtype=np.uint):
            yield (b*n1+n2, b*d1+d2)

        n1, n2 = a*n1+n2, n1
        d1, d2 = a*d1+d2, d1

        
        
def rational_approximation(value, max_num=None, max_den=None,
                           lohi_num=[0, np.inf], lohi_den=[1, np.inf], max_iter=1e6):
    """Compute best rational approximation of a fraction via continued fraction series
    """
    eps = 1.e-10
    if max_num:
        lohi_num[1] = max_num
        
    if max_den:
        lohi_den[1] = max_den
        
    n2, d2 = int(value), 1
    count = 0
    for n1, d1 in eval_chain(chain(value)):
        count += 1
        if count > max_iter:
            raise ValueError('Max iterations exceeded.')

        if lohi_num[0] < n1 and lohi_den[0] < d1:
            if n1 > lohi_num[1] or d1 > lohi_den[1]:
                # Finish if exceeded either max threshold
                return n2, d2
            elif abs(value - n1/d1) <= eps:
                # Finish if results are good enough
                return n1, d1
            
        n2, d2 = n1, d1

    