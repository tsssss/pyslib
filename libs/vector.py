import numpy as np

def dot(vec1, vec2):
    """
    vec1,vec2 are m-dimension vectors in [n,m].
    return [n].
    """
    return np.sum(vec1*vec2, axis=-1)

def magnitude(vec):
    return np.sqrt(dot(vec,vec))

def normalize(vec):
    return vec/magnitude(vec)[:,np.newaxis]

def cross(vec1, vec2):
    return np.cross(vec1, vec2)