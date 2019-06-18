cimport cython
from .contract cimport Contract

cdef class Account:
    cdef public object name
    cdef public int account_type
    cdef public long double balance
    cdef public bint _is_asset_or_expenses

    cpdef void debit(self, long double amount)
    cpdef void credit(self, long double amount)

cdef class FastLedger:
    cdef public long double cash
    cdef public object contracts
    cdef public long double initial_equity

    @cython.locals(out=cython.longdouble, sublist=list, a=Contract)
    cpdef long double get_asset_valuation(self)
    @cython.locals(out=cython.longdouble, sublist=list, a=Contract)
    cpdef long double get_liability_valuation(self)
    cpdef long double get_equity_valuation(self)
    #cpdef long double get_asset_valuation_of(self, object contract_type, contract_subtype=*)
    #cpdef long double get_liability_valuation_of(self, object contract_type)
    #cpdef object get_all_assets(self)
    #cpdef object get_all_liabilities(self)
    #cpdef object get_assets_of_type(self, object contractType)
    #cpdef object get_liabilities_of_type(self, object contractType)
    #cpdef void add_asset(self, object contract)
    #cpdef void add_liability(self, object contract)
    #cpdef void add_cash(self, long double amount)
    #cpdef void subtract_cash(self, long double amount)
    #cpdef void pay_liability(self, long double amount, object loan)
    #cpdef void sell_asset(self, long double amount, object assetType)
    #cpdef void pull_funding(self, long double amount, object loan)
    #cpdef long double get_initial_equity(self)
    #cpdef void set_initial_valuations(self)
    #cpdef void devalue_asset(self, object asset, long double valuationLost)
    #cpdef void appreciate_asset(self, object asset, long double valuationLost)
    #cpdef void devalue_liability(self, object liability, long double valuationLost)
    #cpdef void appreciate_liability(self, object liability, long double valuationLost)
