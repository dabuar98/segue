import numpy as np

def cosine_similarity(vect_A, vect_B):
    """
    Computes the cosine similarity between vect_A and vect_B
    @params vect_A, vect_B
    @returns similarity (float)
    Note: vect_A and vect_B must have the same dimension
    """
    # Calculate dot product and norms
    dot_product = np.dot(vect_A, vect_B)
    norm_A = np.linalg.norm(vect_A)
    norm_B = np.linalg.norm(vect_B)
    result = dot_product / (norm_A * norm_B) # This operation returns a numpy.ndarray with one element
    return result.item() # Convert to native python float
