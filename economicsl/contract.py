from collections import defaultdict


class Contract(object):
    __slots__ = 'assetParty', 'liabilityParty', 'ctype'
    """Base class for a model contract"""
    ctype = 'Contract'

    def __init__(self, assetParty, liabilityParty):
        self.assetParty = assetParty
        self.liabilityParty = liabilityParty

    def get_asset_party(self):
        return self.assetParty

    def get_liability_party(self):
        return self.liabilityParty

    def get_value(self, me):
        pass

    def get_action(self, me):
        pass

    def get_name(self, me):
        pass

    def is_eligible(self, me):
        return False


class Contracts(object):
    __slots__ = 'all_assets', 'all_liabilities'

    def __init__(self):
        self.all_assets = defaultdict(list)
        self.all_liabilities = defaultdict(list)
