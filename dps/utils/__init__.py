from .logger import log
# define logger for this module
tools_log = log["tools"]


def delegate(attribute_name, method_names, attribute_names):
    def decorator(cls):
        # nonlocal attribute_name # works only in python3
        # workaround for python 2.x
        a = attribute_name
        if a.startswith('__'):
            a = '_' + cls.__name__ + a
        for name in method_names:
            func_dsc = 'lambda self, *a, **kw: self.{0}.{1}(*a, **kw)'
            func_dsc = func_dsc.format(a, name)
            setattr(cls, name, eval(func_dsc))

#         for name in attribute_names:
#             attr = 'lambda self:getattr(self.{0}, {1})'.format(a, name)
#             setattr(cls, name, eval(attr))
        return cls
    return decorator
