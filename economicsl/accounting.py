from .notenoughgoods import NotEnoughGoods


def doubleEntry(debitAccount, creditAccount, amount):
    debitAccount.debit(amount)
    creditAccount.credit(amount)


class Account:
    def __init__(self, name, accountType, startingBalance=0.0):
        self.name = name
        self.accountType = accountType
        self.balance = startingBalance

    def doubleEntry(self, debitAccount, creditAccount, amount):
        doubleEntry(debitAccount, creditAccount, amount)

    # A Debit is a positive change for ASSET and EXPENSES accounts, and negative for the rest.
    def debit(self, amount):
        if (self.accountType == AccountType.ASSET) or (self.accountType == AccountType.EXPENSES):
            self.balance += amount
        else:
            self.balance -= amount

    # A Credit is a negative change for ASSET and EXPENSES accounts, and positive for the rest.
    def credit(self, amount):
        if ((self.accountType == AccountType.ASSET) or (self.accountType == AccountType.EXPENSES)):
            self.balance -= amount
        else:
            self.balance += amount

    def getAccountType(self):
        return self.accountType

    def getBalance(self):
        return self.balance

    def getName(self):
        return self.name


def enum(**enums):
    return type('Enum', (), enums)


AccountType = enum(ASSET=1,
                   LIABILITY=2,
                   EQUITY=3,
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
    def __init__(self, me):
        self.contractsToAssetAccounts = {}
        self.contracts = []
        self.equityAccounts = []
        self.liabilityAccounts = []
        self.goodsAccounts = {}
        self.allGoods = {}
        self.contractsToLiabilityAccounts = {}
        self.me = me
        self.equityAccount = Account("equityAccounts", AccountType.EQUITY)
        self.assetAccounts = []

        # A StressLedger is a list of accounts (for quicker searching)

        # Each Account includes an inventory to hold one type of contract.
        # These hashmaps are used to access the correct account for a given type of contract.
        # Note that separate hashmaps are needed for asset accounts and liability accounts: the same contract
        # type (such as Loan) can sometimes be an asset and sometimes a liability.

        # A book is initially created with a cash account and an equityAccounts account (it's the simplest possible book)
        self.addAccount(self.equityAccount, None)

        self.allGoods["cash"] = 0.0

    def getAssetValue(self):
        return sum([aa.getBalance() for aa in self.assetAccounts])

    def getLiabilityValue(self):
        return sum([la.getBalance() for la in self.liabilityAccounts])

    def getEquityValue(self):
        return sum([ea.getBalance() for ea in self.equityAccounts])

    def getAssetValueOf(self, contractType):
        # return contractsToAssetAccounts.get(contractType).getBalance();
        return sum([c.getValue(self.me) for c in self.allAssets if isinstance(c, contractType)])

    def getLiabilityValueOf(self, contractType):
        # return contractsToLiabilityAccounts.get(contractType).getBalance();
        return sum([c.getValue(self.me) for c in self.allLiabilities if isinstance(c, contractType)])

    def getAllAssets(self):
        return self.allAssets

    def getAllLiabilities(self):
        return self.allLiabilities

    def getAssetsOfType(self, contractType):
        return [c for c in self.allAssets if isinstance(c, contractType)]

    def getLiabilitiesOfType(self, contractType):
        return [c for c in self.allLiabilities if isinstance(c, contractType)]

    def getGood(self, name):
        if name not in self.allGoods:
            self.allGoods[name] = 0.0
        return self.allGoods[name]

    def getCash(self):
        return self.getGood("cash")

    def addAccount(self, account, contractType):
        switch = account.getAccountType()
        if switch == AccountType.ASSET:
            self.assetAccounts.append(account)
            self.contractsToAssetAccounts[contractType] = account
        elif switch == AccountType.LIABILITY:
            self.liabilityAccounts.append(account)
            self.contractsToLiabilityAccounts[contractType] = account
        elif switch == AccountType.EQUITY:
            self.equityAccounts.append(account)

        # Not sure what to do with INCOME, EXPENSES

    # Adding an asset means debiting the account relevant to that type of contract
    # and crediting equity.
    # @param contract an Asset contract to add
    def addAsset(self, contract):
        assetAccount = self.contractsToAssetAccounts.get(contract)

        if assetAccount is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            assetAccount = Account(contract.getName(self.me), AccountType.ASSET)
            self.addAccount(assetAccount, contract)

        # (dr asset, cr equity)
        doubleEntry(assetAccount, self.equityAccount, contract.getValue(self.me))

        # Add to the general inventory?
        self.allAssets.append(contract)

    # Adding a liability means debiting equity and crediting the account
    # relevant to that type of contract.
    # @param contract a Liability contract to add
    def addLiability(self, contract):
        liabilityAccount = self.contractsToLiabilityAccounts.get(contract)

        if liabilityAccount is None:
            # If there doesn't exist an Account to hold this type of contract, we create it
            liabilityAccount = Account(contract.getName(self.me), AccountType.LIABILITY)
            self.addAccount(liabilityAccount, contract)

        # (dr equity, cr liability)
        doubleEntry(self.equityAccount, liabilityAccount, contract.getValue(self.me))

        # Add to the general inventory?
        self.allLiabilities.append(contract)

    def addGoods(self, name, amount, value):
        assert amount >= 0.0
        have = self.allGoods.get(name, 0.0)
        self.allGoods[name] = have + amount
        physicalthingsaccount = self.getGoodsAccount(name)
        doubleEntry(physicalthingsaccount, self.equityAccount, amount * value)

    def subtractGoods(self, name, amount, value=None):
        if value is None:
            try:
                value = self.getPhysicalThingValue(name)
                self.subtractGoods(name, amount, value)
            except:
                raise NotEnoughGoods(name, 0, amount)
        else:
            assert amount >= 0.0
            have = self.getGood(name)
            if amount > have:
                raise NotEnoughGoods(name, have, amount)
            self.allGoods[name] = have - amount
            doubleEntry(self.equityAccount, self.getGoodsAccount(name), amount * value)

    def getGoodsAccount(self, name):
        account = self.goodsAccounts.get(name)
        if account is None:
            account = Account(name, AccountType.GOOD)
            self.goodsAccounts[name] = account
        return account

    def getPhysicalThingValue(self, name):
        try:
            return self.getGoodsAccount(name).getBalance() / self.getPhysicalThings(name)
        except:
            return 0.0

    def getPhysicalThings(self, name):
        return self.allGoods.get(name)

    # Reevaluates the current stock of phisical goods at a specified value and books
    # the change to org.economicsl.accounting
    def revalueGoods(self, name, value):
        old_value = self.getGoodsAccount(name).getBalance()
        new_value = self.allGoods.get(name) * value
        if (new_value > old_value):
            doubleEntry(self.getGoodsAccount(name), self.equityAccount, new_value - old_value)
        elif (new_value < old_value):
            doubleEntry(self.equityAccount, self.getGoodsAccount(name), old_value - new_value)

    def addCash(self, amount):
        # (dr cash, cr equity)
        self.addGoods("cash", amount, 1.0)

    def substractCash(self, amount):
        self.subtractGoods("cash", amount, 1.0)

    # Operation to pay back a liability loan; debit liability and credit cash
    # @param amount amount to pay back
    # @param loan the loan which is being paid back
    def payLiability(self, amount, loan):
        self.liabilityAccount = self.contractsToLiabilityAccounts.get(loan)

        assert self.getCash() >= amount  # Pre-condition: liquidity has been raised.

        # (dr liability, cr cash )
        doubleEntry(self.liabilityAccount, self.getGoodsAccount("cash"), amount)

    # If I've sold an asset, debit cash and credit asset
    # @param amount the *value* of the asset
    def sellAsset(self, amount, assetType):
        self.assetAccount = self.contractsToAssetAccounts.get(assetType)

        # (dr cash, cr asset)
        doubleEntry(self.getGoodsAccount("cash"), self.assetAccount, amount)

    def printBalanceSheet(self, me):
        print("Asset accounts:\n---------------")
        for a in self.assetAccounts:
            print(a.getName(), "-> %.2f" % a.getBalance())

        print("Breakdown: ")
        for c in self.allAssets:
            print("\t", c.getName(me), " > ", c.getValue(me))
        print("TOTAL ASSETS: %.2f" % self.getAssetValue())

        print("\nLiability accounts:\n---------------")
        for a in self.liabilityAccounts:
            print(a.getName(me), " -> %.2f" % a.getBalance())
        for c in self.allLiabilities:
            print("\t", c.getName(me), " > ", c.getValue(me))
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
        return self.contractsToAssetAccounts.get(contract)

    def getCashAccount(self):
        return self.getGoodsAccount("cash")

    def getContractsToAssetAccounts(self):
        return self.contractsToAssetAccounts

    def getContractsToLiabilityAccounts(self):
        return self.contractsToLiabilityAccounts

    def getEquityAccount(self):
        return self.equityAccount
