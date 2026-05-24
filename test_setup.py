from django.template.context import BaseContext


def _base_context_copy(self):
    duplicate = BaseContext()
    duplicate.dicts = self.dicts[:]
    return duplicate


BaseContext.__copy__ = _base_context_copy
