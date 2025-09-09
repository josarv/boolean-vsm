from functools import reduce

def compose(*functions):
    return reduce(lambda f, g: lambda x: g(f(x)), functions, lambda x: x)
