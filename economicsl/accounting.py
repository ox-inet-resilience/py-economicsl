import numpy as np
from abce import NotEnoughGoods


def doubleEntry(debitAccount, creditAccount, amount: np.longdouble):
    debitAccount.debit(amount)
    creditAccount.credit(amount)


class Account:
    def __init__(self, name, accountType, startingBalance: np.longdouble=0.0) -> None:
        self.name = name
        self.accountType = accountType
        self.balance = np.longdouble(startingBalance)

    # A Debit is a positive change for ASSET and EXPENSES accounts, and negative for the rest.
    def debit(self, amount: np.longdouble):
        if (self.accountType == AccountType.ASSET) or (self.accountType == AccountType.EXPENSES):
            self.balance += amount
        else:
            self.balance -= amount

    # A Credit is a negative change for ASSET and EXPENSES accounts, and positive for the rest.
    def credit(self, amount: np.longdouble):
        if ((self.accountType == AccountType.ASSET) or (self.accountType == AccountType.EXPENSES)):
            self.balance -= amount
        else:
            self.balance += amount

    def getAccountType(self):
        return self.accountType

    def getBalance(self) -> np.longdouble:
        return self.balance

    def getName(self) -> str:
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
class Ledger:
    def __init__(self, me, inventory) -> None:
        # A StressLedger is a list of accounts (for quicker searching)

        # Each Account includes an inventory to hold one type of contract.
        # These hashmaps are used to access the correct account for a given type of contract.
        # Note that separate hashmaps are needed for asset accounts and liability accounts: the same contract
        # type (such as Loan) can sometimes be an asset and sometimes a liability.

        # A book is initially created with a cash account (it's the simplest possible book)
        self.assetAccounts = {}  # a hashmap from a contract to a assetAccount
        self.inventory = inventory
        self.contracts = Contracts()
        self.goodsAccounts = {}
        self.liabilityAccounts = {}  # a hashmap from a contract to a liabilityAccount
        self.me = me

    def getAssetValue(self) -> np.longdouble:
        return sum([aa.getBalance() for aa in self.assetAccounts.values()])

    def getLiabilityValue(self) -> np.longdouble:
        return sum([la.getBalance() for la in self.liabilityAccounts.values()])

    def getEquityValue(self) -> np.longdouble:
        return self.getAssetValue() - self.getLiabilityValue()

    def getAssetValueOf(self, contractType) -> np.longdouble:
        # return assetAccounts.get(contractType).getBalance();
        return sum([c.getValue() for c in self.contracts.allAssets if isinstance(c, contractType)])

    def getLiabilityValueOf(self, contractType) -> np.longdouble:
        # return liabilityAccounts.get(contractType).getBalance();
        return sum([c.getValue() for c in self.contracts.allLiabilities if isinstance(c, contractType)])

    def getAllAssets(self):
        return self.contracts.allAssets

    def getAllLiabilities(self):
        return self.contracts.allLiabilities

    def getAssetsOfType(self, contractType):
        return [c for c in self.contracts.allAssets if isinstance(c, contractType)]

    def getLiabilitiesOfType(self, contractType):
        return [c for c in self.contracts.allLiabilities if isinstance(c, contractType)]

    def addAccount(self, account, contractType):
        switch = account.getAccountType()
        if switch == AccountType.ASSET:
            self.assetAccounts[contractType] = account
        elif switch == AccountType.LIABILITY:
            self.liabilityAccounts[contractType] = account

        # Not sure what to do with INCOME, EXPENSES

    # Adding an asset means debiting the account relevant to that type of contract
    # and crediting equity.
    # @param contract an Asset contract to add
    def addAsset(self, contract):
        assetAccount = self.assetAccounts.get(contract)

        if assetAccount is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            assetAccount = Account(contract.getName(self.me), AccountType.ASSET)
            self.addAccount(assetAccount, contract)

        assetAccount.debit(contract.getValue())

        self.contracts.allAssets.append(contract)

    # Adding a liability means debiting equity and crediting the account
    # relevant to that type of contract.
    # @param contract a Liability contract to add
    def addLiability(self, contract):
        liabilityAccount = self.liabilityAccounts.get(contract)

        if liabilityAccount is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            liabilityAccount = Account(contract.getName(self.me), AccountType.LIABILITY)
            self.addAccount(liabilityAccount, contract)

        liabilityAccount.credit(contract.getValue())

        # Add to the general inventory?
        self.contracts.allLiabilities.append(contract)

    def create(self, name, amount, value):
        self.inventory.create(name, amount)
        physicalthingsaccount = self.getGoodsAccount(name)
        physicalthingsaccount.debit(amount * value)

    def destroy(self, name, amount, value=None):
        if value is None:
            try:
                value = self.getPhysicalThingValue(name)
                self.destroy(name, amount, value)
            except:
                raise NotEnoughGoods(name, 0, amount)
        else:
            self.inventory.destroy(name, amount)
            self.getGoodsAccount(name).credit(amount * value)

    def getGoodsAccount(self, name):
        account = self.goodsAccounts.get(name)
        if account is None:
            account = Account(name, AccountType.GOOD)
            self.goodsAccounts[name] = account
        return account

    def getPhysicalThingValue(self, name):
        try:
            return self.getGoodsAccount(name).getBalance() / self.inventory.getGood(name)
        except:
            return 0.0

    # Reevaluates the current stock of phisical goods at a specified value and books
    # the change to org.economicsl.accounting
    def revalueGoods(self, name, value):
        old_value = self.getGoodsAccount(name).getBalance()
        new_value = self.inventory.getGood(name) * value
        if (new_value > old_value):
            self.getGoodsAccount(name).debit(new_value - old_value)
        elif (new_value < old_value):
            self.getGoodsAccount(name).credit(old_value - new_value)

    def addCash(self, amount: np.longdouble) -> None:
        # (dr cash, cr equity)
        self.create("cash", np.longdouble(amount), 1.0)

    def subtractCash(self, amount: np.longdouble) -> None:
        self.destroy("cash", np.longdouble(amount), 1.0)

    # Operation to pay back a liability loan; debit liability and credit cash
    # @param amount amount to pay back
    # @param loan the loan which is being paid back
    def payLiability(self, amount, loan):
        self.liabilityAccount = self.liabilityAccounts.get(loan)

        assert self.inventory.getCash() >= amount  # Pre-condition: liquidity has been raised.

        # (dr liability, cr cash )
        doubleEntry(self.liabilityAccount, self.getGoodsAccount("cash"), amount)

    # If I've sold an asset, debit cash and credit asset
    # @param amount the *value* of the asset
    def sellAsset(self, amount, assetType):
        assetAccount = self.assetAccounts.get(assetType)

        # (dr cash, cr asset)
        doubleEntry(self.getGoodsAccount("cash"), assetAccount, amount)

    # Operation to cancel a Loan to someone (i.e. cash in a Loan in the Assets side).
    #
    # I'm using this for simplicity but note that this is equivalent to selling an asset.
    # @param amount the amount of loan that is cancelled
    def pullFunding(self, amount, loan):
        loanAccount = self.getAccountFromContract(loan)
        # (dr cash, cr asset )
        doubleEntry(self.getCashAccount(), loanAccount, amount)

    def printBalanceSheet(self, me):
        print("Asset accounts:\n---------------")
        for a in self.assetAccounts.values():
            print(a.getName(), "-> %.2f" % a.getBalance())

        print("Breakdown: ")
        for c in self.contracts.allAssets:
            print("\t", c.getName(me), " > ", c.getValue())
        print("TOTAL ASSETS: %.2f" % self.getAssetValue())

        print("\nLiability accounts:\n---------------")
        for a in self.liabilityAccounts.values():
            print(a.getName(), " -> %.2f" % a.getBalance())
        for c in self.contracts.allLiabilities:
            print("\t", c.getName(me), " > ", c.getValue())
        print("TOTAL LIABILITIES: %.2f" % self.getLiabilityValue())
        print("\nTOTAL EQUITY: %.2f" % self.getEquityValue())

        print("\nSummary of encumbered collateral:")
        # for (Contract contract : getLiabilitiesOfType(Repo.class)) {
        #    ((Repo) contract).printCollateral();
        # }
        print("\n\nTotal cash: ", self.getGoodsAccount("cash").getBalance())
        # print("Encumbered cash: "+me.getEncumberedCash());
        # print("Unencumbered cash: " + (me.getCash_() - me.getEncumberedCash()));

    def getInitialEquity(self):
        return self.initialEquity

    def setInitialValues(self):
        self.initialEquity = self.getEquityValue()

    def getAccountFromContract(self, contract):
        return self.assetAccounts.get(contract)

    def getCashAccount(self):
        return self.getGoodsAccount("cash")

    # if an Asset loses value, I must debit equity and credit asset
    # @param valueLost the value lost
    def devalueAsset(self, asset, valueLost):
        self.assetAccounts.get(asset).credit(valueLost)

        # Todo: perform a check here that the Asset account balances match the value of the assets. (?)

    def appreciateAsset(self, asset, valueLost):
        self.assetAccounts.get(asset).debit(valueLost)

    def devalueLiability(self, liability, valueLost):
        self.liabilityAccounts.get(liability).debit(valueLost)

    def appreciateLiability(self, liability, valueLost):
        self.liabilityAccounts.get(liability).credit(valueLost)


class Contracts:
    def __init__(self):
        self.allAssets = []
        self.allLiabilities = []
