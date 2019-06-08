from typing import Any, List, Dict

import numpy as np

from .abce import NotEnoughGoods, Inventory, eps
from .contract import Contracts


class Account(object):
    __slots__ = 'name', 'account_type', 'balance', '_is_asset_or_expenses'

    def __init__(self, name: str, account_type: int, starting_balance: np.longdouble = 0.0) -> None:
        self.name: str = name
        self.account_type: int = account_type
        self.balance = np.longdouble(starting_balance)
        # PERF cache sign for faster debit/credit
        self._is_asset_or_expenses: bool = (account_type == AccountType.ASSET) or (account_type == AccountType.EXPENSES)

    def debit(self, amount: np.longdouble) -> None:
        """
        A Debit is a positive change for ASSET and EXPENSES accounts, and negative for the rest.
        """
        if self._is_asset_or_expenses:
            self.balance += amount
        else:
            self.balance -= amount

    def credit(self, amount: np.longdouble) -> None:
        """
        A Credit is a negative change for ASSET and EXPENSES accounts, and positive for the rest.
        """
        if self._is_asset_or_expenses:
            self.balance -= amount
        else:
            self.balance += amount

    def get_account_type(self) -> int:
        return self.account_type

    def get_balance(self) -> np.longdouble:
        return self.balance

    def get_name(self) -> str:
        return self.name


def enum(**enums):
    return type('Enum', (), enums)


AccountType = enum(ASSET=1,
                   LIABILITY=2,
                   INCOME=4,
                   EXPENSES=5,
                   GOOD=6)


# This is the main class implementing double entry org.economicsl.accounting. All public operations provided by this class
# are performed as a double entry operation, i.e. a pair of (dr, cr) operations.
#
# A Ledger contains a set of accounts, and is the interface between an agent and its accounts. Agents cannot
# directly interact with accounts other than via a Ledger.
#
# At the moment, a Ledger contains an account for each type of contract, plus an equity account and a cash account.
#
# A simple economic agent will usually have a single Ledger, whereas complex firms and banks can have several books
# (as in branch banking for example).
class Ledger(object):
    __slots__ = 'asset_accounts', 'inventory', 'contracts', 'goods_accounts', 'liability_accounts', 'initial_equity'

    def __init__(self) -> None:
        # A Ledger is a list of accounts (for quicker searching)

        # Each Account includes an inventory to hold one type of contract.
        # These hashmaps are used to access the correct account for a given type of contract.
        # Note that separate hashmaps are needed for asset accounts and liability accounts: the same contract
        # type (such as Loan) can sometimes be an asset and sometimes a liability.

        # A book is initially created with a cash account (it's the simplest possible book)
        self.asset_accounts: Dict[Any] = {}  # a hashmap from a contract to an asset_account
        self.inventory = Inventory()
        self.contracts = Contracts()
        self.goods_accounts: Dict[Any] = {}
        self.liability_accounts: Dict[Any] = {}  # a hashmap from a contract to a liability_account
        self.initial_equity = 0

    def get_asset_valuation(self) -> np.longdouble:
        # return (sum(aa.get_balance() for aa in self.asset_accounts.values()) +
        return (sum(a.get_valuation('A') for sublist in self.contracts.all_assets.values() for a in sublist) +
                self.inventory.get_cash())

    def get_liability_valuation(self) -> np.longdouble:
        # return sum(la.get_balance() for la in self.liability_accounts.values())
        return sum(l.get_valuation('L') for sublist in self.contracts.all_liabilities.values() for l in sublist)

    def get_equity_valuation(self) -> np.longdouble:
        return self.get_asset_valuation() - self.get_liability_valuation()

    def get_asset_valuation_of(self, contract_type, contract_subtype=None) -> np.longdouble:
        # return asset_accounts.get(contractType).get_balance();
        if contract_subtype:
            return sum(c.get_valuation('A') for c in self.contracts.all_assets[contract_type.ctype] if c.get_asset_type() == contract_subtype)
        return sum(c.get_valuation('A') for c in self.contracts.all_assets[contract_type.ctype])

    def get_liability_valuation_of(self, contract_type) -> np.longdouble:
        # return liability_accounts.get(contractType).get_balance();
        return sum(c.get_valuation('L') for c in self.contracts.all_liabilities[contract_type.ctype])

    def get_all_assets(self) -> List[Any]:
        return [asset for sublist in self.contracts.all_assets.values() for asset in sublist]

    def get_all_liabilities(self) -> List[Any]:
        return [lia for sublist in self.contracts.all_liabilities.values() for lia in sublist]

    def get_assets_of_type(self, contractType) -> List[Any]:
        return self.contracts.all_assets[contractType.ctype]

    def get_liabilities_of_type(self, contractType) -> List[Any]:
        return self.contracts.all_liabilities[contractType.ctype]

    def add_account(self, account, contract_type) -> None:
        switch = account.get_account_type()
        if switch == AccountType.ASSET:
            self.asset_accounts[contract_type] = account
        elif switch == AccountType.LIABILITY:
            self.liability_accounts[contract_type] = account

        # TODO: Not sure what to do with INCOME, EXPENSES

    # Adding an asset means debiting the account relevant to that type of contract
    # and crediting equity.
    # @param contract an Asset contract to add
    def add_asset(self, contract) -> None:
        asset_account = self.asset_accounts.get(contract)

        if asset_account is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            asset_account = Account(contract.get_name(), AccountType.ASSET)
            self.add_account(asset_account, contract)

        asset_account.debit(contract.get_valuation('A'))

        self.contracts.all_assets[contract.ctype].append(contract)

    # Adding a liability means debiting equity and crediting the account
    # relevant to that type of contract.
    # @param contract a Liability contract to add
    def add_liability(self, contract) -> None:
        liability_account = self.liability_accounts.get(contract)

        if liability_account is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            liability_account = Account(contract.get_name(), AccountType.LIABILITY)
            self.add_account(liability_account, contract)

        liability_account.credit(contract.get_valuation('L'))

        # Add to the general inventory?
        self.contracts.all_liabilities[contract.ctype].append(contract)

    def create(self, name: str, amount, valuation) -> None:
        self.inventory.create(name, amount)
        self.get_goods_account(name).debit(amount * valuation)

    def destroy(self, name: str, amount, valuation=None) -> None:
        if valuation is None:
            try:
                valuation = self.get_physical_thing_valuation(name)
                self.destroy(name, amount, valuation)
            except Exception:
                raise NotEnoughGoods(name, 0, amount)
        else:
            self.inventory.destroy(name, amount)
            self.get_goods_account(name).credit(amount * valuation)

    def get_goods_account(self, name: str) -> Account:
        account = self.goods_accounts.get(name)
        if account is None:
            account = Account(name, AccountType.GOOD)
            self.goods_accounts[name] = account
        return account

    def get_physical_thing_valuation(self, name: str) -> np.longdouble:
        try:
            return self.get_goods_account(name).get_balance() / self.inventory.get_good(name)
        except Exception:
            return 0.0

    def revalue_goods(self, name, valuation) -> None:
        """
        Reevaluate the current stock of physical goods at a specified valuation and book
        the change to GoodsAccount.
        """
        old_valuation = self.get_goods_account(name).get_balance()
        new_valuation = self.inventory.get_good(name) * valuation
        if new_valuation > old_valuation:
            self.get_goods_account(name).debit(new_valuation - old_valuation)
        elif new_valuation < old_valuation:
            self.get_goods_account(name).credit(old_valuation - new_valuation)

    def add_cash(self, amount: np.longdouble) -> None:
        # (dr cash, cr equity)
        self.create("cash", np.longdouble(amount), 1.0)

    def subtract_cash(self, amount: np.longdouble) -> None:
        self.destroy("cash", np.longdouble(amount), 1.0)

    # Operation to pay back a liability loan; debit liability and credit cash
    # @param amount amount to pay back
    # @param loan the loan which is being paid back
    def pay_liability(self, amount, loan) -> None:
        liability_account = self.liability_accounts.get(loan)

        # Pre-condition: liquidity has been raised.
        assert (self.inventory.get_cash() - amount) >= -eps, (self.inventory.get_cash(), amount)

        # (dr liability, cr cash )
        self.book(liability_account, self.get_goods_account("cash"), amount)

    # If I've sold an asset, debit cash and credit asset
    # @param amount the *valuation* of the asset
    def sell_asset(self, amount: np.longdouble, assetType) -> None:
        asset_account = self.asset_accounts.get(assetType)

        # (dr cash, cr asset)
        self.book(self.get_goods_account("cash"), asset_account, amount)

    # Operation to cancel a Loan to someone (i.e. cash in a Loan in the Assets side).
    #
    # I'm using this for simplicity but note that this is equivalent to selling an asset.
    # @param amount the amount of loan that is cancelled
    def pull_funding(self, amount, loan) -> None:
        loan_account = self.get_account_from_contract(loan)
        # (dr cash, cr asset )
        self.book(self.get_cash_account(), loan_account, amount)

    def print_balance_sheet(self, me) -> None:
        print("Asset accounts:\n---------------")
        for a in self.asset_accounts.values():
            print(a.get_name(), "-> %.2f" % a.get_balance())

        print("Breakdown: ")
        for c in self.get_all_assets():
            print("\t", c.get_name(me), " > ", c.get_valuation('A'))
        print("TOTAL ASSETS: %.2f" % self.get_asset_valuation())

        print("\nLiability accounts:\n---------------")
        for a in self.liability_accounts.values():
            print(a.get_name(), " -> %.2f" % a.get_balance())
        for c in self.get_all_liabilities():
            print("\t", c.get_name(me), " > ", c.get_valuation('L'))
        print("TOTAL LIABILITIES: %.2f" % self.get_liability_valuation())
        print("\nTOTAL EQUITY: %.2f" % self.get_equity_valuation())

        print("\nSummary of encumbered collateral:")
        # for repo in self.get_liabilities_of_type(Repo):
        #     repo.print_collateral()
        print("\n\nTotal cash:", self.inventory.get_cash())
        # print("Encumbered cash:", self.get_encumbered_cash())
        # print("Unencumbered cash: " + (me.getCash_() - me.getEncumberedCash()));

    def get_initial_equity(self) -> np.longdouble:
        return self.initial_equity

    def set_initial_valuations(self) -> None:
        self.initial_equity = self.get_equity_valuation()

    def get_account_from_contract(self, contract):
        return self.asset_accounts.get(contract)

    def get_cash_account(self) -> Account:
        return self.get_goods_account("cash")

    def devalue_asset(self, asset, valuationLost: np.longdouble) -> None:
        """
        if an Asset loses valuation, I must credit asset
        @param valuationLost the valuation lost
        """
        self.asset_accounts.get(asset).credit(valuationLost)

        # TODO: perform a check here that the Asset account balances match the valuation of the assets. (?)

    def appreciate_asset(self, asset, valuationLost: np.longdouble) -> None:
        self.asset_accounts.get(asset).debit(valuationLost)

    def devalue_liability(self, liability, valuationLost: np.longdouble) -> None:
        self.liability_accounts.get(liability).debit(valuationLost)

    def appreciate_liability(self, liability, valuationLost) -> None:
        self.liability_accounts.get(liability).credit(valuationLost)

    def book(self, debit_account: Account, credit_account: Account, amount: np.longdouble):
        debit_account.debit(amount)
        credit_account.credit(amount)
