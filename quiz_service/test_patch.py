from django.template import context


def _patched_base_context_copy(self):
    duplicate = object.__new__(context.BaseContext)
    duplicate.dicts = self.dicts[:]
    return duplicate


context.BaseContext.__copy__ = _patched_base_context_copy
