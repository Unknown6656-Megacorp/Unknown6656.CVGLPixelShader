from .. import *
from ..shader_generator import _generate_shader_class


Invert = _generate_shader_class('out_color = mix(out_color, 1 - out_color, strength);', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Grayscale = _generate_shader_class('''
out_color = mix(out_color, dot(out_color.rgb, vec3(0.299, 0.587, 0.114)), strength);
''', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Sepia = _generate_shader_class('''
float gray = dot(out_color.rgb, vec3(0.299, 0.587, 0.114));

out_color.rgb = mix(out_color.rgb, gray * color, strength);
''', '', [
    ShaderVariable('color', ShaderVariableType.FLOAT_3, [1.2, 1.0, 0.8]),
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])
