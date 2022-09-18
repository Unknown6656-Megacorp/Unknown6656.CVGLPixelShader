from .. import *
from ..shader_generator import _generate_shader_class


Pixelation = _generate_shader_class('''
if (size > 1)
{
    vec2 scale = vec2(width, height) / size;
    out_color = texture2D(image, floor(coords * scale) / scale);
}
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 10)
])
