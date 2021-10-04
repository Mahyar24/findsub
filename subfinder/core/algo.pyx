# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

from cpython.datetime cimport timedelta


cdef struct scene:
    double begin
    double end


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
        scene c_base[100_000]
        scene c_other[100_000]
        unsigned int dialog, speech
        unsigned int i, ii


    for i in range(base_len):
        c_base[i].begin = <double> base[i][0]
        c_base[i].end = <double> base[i][1]
        base_total += c_base[i].end - c_base[i].begin

    for ii in range(other_len):
        c_other[ii].begin = <double> other[ii][0].total_seconds()
        c_other[ii].end = <double> other[ii][1].total_seconds()

    for dialog in range(other_len):
        for speech in range(base_len):
            if c_base[speech].begin > c_other[dialog].end or c_other[dialog].begin > c_base[speech].end:  # Huge SpeedUP.
                continue

            if (
                c_other[dialog].begin <= c_base[speech].begin and c_other[dialog].end >= c_base[speech].end
            ):  # base is included in other completely
                matched += c_base[speech].end - c_base[speech].begin
            elif (
                c_other[dialog].begin >= c_base[speech].begin and c_base[speech].end >= c_other[dialog].end
            ):  # other is included in base completely
                matched += c_other[dialog].end - c_other[dialog].begin
            elif c_other[dialog].begin <= c_base[speech].begin <= c_other[dialog].end <= c_base[speech].end:  # partially
                matched += c_other[dialog].end - c_base[speech].begin
            elif c_base[speech].begin <= c_other[dialog].begin <= c_base[speech].end <= c_other[dialog].end:  # partially
                matched += c_base[speech].end - c_other[dialog].begin

    return matched / base_total
