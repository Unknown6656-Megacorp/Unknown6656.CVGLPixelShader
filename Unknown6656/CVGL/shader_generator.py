from . import *
from .shader_variable import ShaderVariable


def _generate_shader_class(code : str, functions : str, variables : list[ShaderVariable]) -> type:
    import numpy as np
    import uuid

    def init_shader(): return PixelShader(code, functions, variables)
    init_code = f'''
def __init(self{"".join([f", {v.name} = {v.default_value}" for v in variables])}):
    self._shader = init_shader()
    '''
    for var in variables:
        init_code += f'\n    self._shader["{var.name}"] = {var.name}'

    exec(init_code, locals())
    _init = locals()['__init']

    def _apply(self, image : np.ndarray) -> np.ndarray: return self._shader.apply(image)

    def _enter(self): return self

    def _exit(self, extype, exvalue, trace) -> None: self._shader.close()

    def _get(self, var : ShaderVariable): return self._shader[var]

    def _set(self, var : ShaderVariable, value) -> None: self._shader[var] = value

    members = {
        '__init__': _init,
        '__call__': _apply,
        '__enter__': _enter,
        '__exit__': _exit,
        '__getitem__': _get,
        '__setitem__': _set,
        '__doc__': lambda: 'A dynamically generated shader class which uses the following variables:' + "".join(["\n - " + str(v) for v in variables]),
        'get_variable': _get,
        'set_variable': _set,
        'apply': _apply,
        'close': lambda x: _exit(x, None, None, None),
    }

    for var in variables:
        members[var.name] = property(lambda x: _get(x, var), lambda x, v: _set(x, var, v))

    _type = type(str(uuid.uuid4()), (object, ), members)

    return _type
