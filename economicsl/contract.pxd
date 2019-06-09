cimport cython

cdef class Contract:
    cdef public object assetParty
    cdef public object liabilityParty
    cpdef object get_asset_party(self)
    cpdef object get_liability_party(self)
    cpdef long double get_valuation(self, str side)
    cpdef object get_action(self, object me)
    cpdef str get_name(self)
    cpdef bint is_eligible(self, object me)
