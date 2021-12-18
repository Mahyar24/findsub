# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
Compatible with python3.9+ and Cython0.29.25+.
Mahyar@Mahyar24.com, Thu 19 Aug 2021.
"""

from cython.view cimport array as cy_array
from cpython.datetime cimport timedelta


cpdef double match(list base, list other):
    """
    Based on the data structure, calculate that how much of the time that there is
    some speech going on in base, there is a subtitle in other.
    """
    cdef:
        unsigned int base_len = len(base)
        unsigned int other_len = len(other)
        double matched = 0.0
        double base_total = 0.0
        double [:, :] c_base = cy_array(shape=(base_len, 2), itemsize=sizeof(double), format="d")
        double [:, :] c_other = cy_array(shape=(other_len, 2), itemsize=sizeof(double), format="d")
        unsigned int dialog, speech
        unsigned int i, ii


    for i in range(base_len):
        c_base[i, 0] = <double> base[i][0]
        c_base[i, 1] = <double> base[i][1]
        base_total += c_base[i, 1] - c_base[i, 0]

    for ii in range(other_len):
        c_other[ii, 0] = <double> other[ii][0].total_seconds()
        c_other[ii, 1] = <double> other[ii][1].total_seconds()

    for speech in range(base_len):
        for dialog in range(other_len):
            if c_base[speech, 0] > c_other[dialog, 1] or c_other[dialog, 0] > c_base[speech, 1]:  # Huge SpeedUP.
                continue

            if (
                c_other[dialog, 0] <= c_base[speech, 0] and c_other[dialog, 1] >= c_base[speech, 1]
            ):  # base is included in other completely
                matched += c_base[speech, 1] - c_base[speech, 0]
            elif (
                c_other[dialog, 0] >= c_base[speech, 0] and c_base[speech, 1] >= c_other[dialog, 1]
            ):  # other is included in base completely
                matched += c_other[dialog, 1] - c_other[dialog, 0]
            elif c_other[dialog, 0] <= c_base[speech, 0] <= c_other[dialog, 1] <= c_base[speech, 1]:  # partially
                matched += c_other[dialog, 1] - c_base[speech, 0]
            elif c_base[speech, 0] <= c_other[dialog, 0] <= c_base[speech, 1] <= c_other[dialog, 1]:  # partially
                matched += c_base[speech, 1] - c_other[dialog, 0]

    return matched / base_total
