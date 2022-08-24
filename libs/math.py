import itertools
import numpy as np

def mkarthm(a, b, c, mode):
    """
    mode='x0', a=x0, b=dx, c=n
    mode='x1', a=x1, b=dx, c=n
    mode='dx', a=x0, b=x1, c=dx
    mode='n' , a=x0, b=x1, c=n
    :param x0: the first element
    :param x1: the last element
    :param dx: the step between elements
    :param n: the number of element
    :return: a list of array

    print(utils.mkarthm(0,1,9, 'x0'))
    print(utils.mkarthm(0,-1,9, 'x1'))
    print(utils.mkarthm(0,10,1,'dx'))
    print(utils.mkarthm(0,10,5,'n'))
    """

    assert mode in ['x0','x1','dx','n']

    if mode == 'x0':
        return a+b*np.arange(c)
    elif mode == 'x1':
        return a-b*np.flip(np.arange(c))
    elif mode == 'dx':
        ns = (b-a)/c
        if ns-np.floor(ns) >= 0.9: ns = np.round(ns)
        else: ns = np.floor(ns)
        ns += 1
        return a+c*np.arange(ns)
    else:
        dx = (b-a)/(c-1)
        return a+dx*np.arange(c)



def sort_uniq(seq):
    """
    Return a sorted and uniq list of the input list.
    :param seq: input list.
    :return: output list.
    """
    return (x[0] for x in itertools.groupby(sorted(seq)))