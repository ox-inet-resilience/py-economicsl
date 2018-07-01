from collections import defaultdict


class Contract:
    """Base class for a model contract"""
    def get_asset_party(self):
        pass

    def get_liability_party(self):
        pass

    def get_value(self, me):
        pass

    def get_available_actions(self, me):
        pass

    def get_name(self, me):
        pass


class Contracts(object):
    __slots__ = 'all_assets', 'all_liabilities'

    def __init__(self):
        self.all_assets = defaultdict(list)
        self.all_liabilities = defaultdict(list)
