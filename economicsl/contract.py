from collections import defaultdict


class Contract:
    __slots__ = "assetParty", "liabilityParty"
    """Base class for a model contract"""
    ctype = "Contract"

    def __init__(self, assetParty, liabilityParty):
        self.assetParty = assetParty
        self.liabilityParty = liabilityParty

    def get_asset_party(self):
        return self.assetParty

    def get_liability_party(self):
        return self.liabilityParty

    def get_valuation(self, side):
        # `side` is either A or L
        pass

    def get_action(self, me):
        pass

    def get_name(self):
        pass

    def is_eligible(self, me):
        return False


class Contracts:
    __slots__ = "all_assets", "all_liabilities"

    def __init__(self):
        self.all_assets = defaultdict(list)
        self.all_liabilities = defaultdict(list)
