import numpy as np

def map_key_former_version(key):
    """
    Map key to its integer value according to Lavengood [1]. Keys are represented with enharmonic equivalents A#/Bb,
    D#/Eb and G#/Ab from Essentia v2.1-beta2
    Args:
        key: Key in { "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#" } [2] (string)

    Returns:
        value: Value to be mapped (integer)

    References:
    [1] M. Lavengood, "Pitch and pitch class," in Open Music Theory, VIVA Pressbooks, 2023.
        [Online]. Available: https://viva.pressbooks.pub/openmusictheory/chapter/pitch-and-pitch-class/.
        [Accessed: Jul. 26, 2026].
    [2] Music Technology Group, Universitat Pompeu Fabra, "key.cpp," essentia, v2.1_beta2.
        [Online]. Available: https://github.com/MTG/essentia/blob/v2.1_beta2/src/algorithms/tonal/key.cpp.
        [Accessed: Jul. 26, 2026].
    """
    key_map = {
        'C': 0,
        'C#': 1,
        'D': 2,
        'D#': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'G': 7,
        'G#': 8,
        'A': 9,
        'A#': 10,
        'B': 11,
    }

    return key_map[key]

def map_key_scale(key_scale):
    """
    Maps scale (minor, major) to an integer value
    :params key_scale: (str) : scale of the key (major or minor)
    :returns value: (int) : Value to be mapped (1 or -1)
    """
    return 1 if key_scale == 'major' else -1

def map_key_current_version(key):
    """
    Map key to its integer value according to Lavengood [1]
    Args:
        key: Key in { "A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab" } [2] (string)

    Returns:
        value: Value to be mapped (integer)
        
    References:
        [1] M. Lavengood, "Pitch and pitch class," in Open Music Theory, VIVA Pressbooks, 2023.
            [Online]. Available: https://viva.pressbooks.pub/openmusictheory/chapter/pitch-and-pitch-class/.
            [Accessed: Jul. 26, 2026].
        [2] Music Technology Group, Universitat Pompeu Fabra, "key.cpp," Essentia (source code repository), commit 3089d2d, GitHub.
            [Online]. Available: https://github.com/MTG/essentia/blob/b9fa6cb674ca43dfb94d28d293aeda441c6745db/src/algorithms/tonal/key.cpp.
            [Accessed: Jul. 26, 2026].
    """
    key_map = {
        'C': 0,
        'C#': 1,
        'D': 2,
        'Eb': 3,
        'E': 4,
        'F': 5,
        'F#': 6,
        'G': 7,
        'Ab': 8,
        'A': 9,
        'Bb': 10,
        'B': 11,
    }

    return key_map[key]

def is_valid_int(value):
    """
    Checks whether value is an integer
    Args:
        value: number to be checked (string)

    Returns:
        boolean: True if it is an integer, False otherwise

    """
    try:
        int(value)
        return True
    except ValueError:
        return False

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
