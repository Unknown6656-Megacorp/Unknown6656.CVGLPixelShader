from .. import *
from ..shader_generator import _generate_shader_class


Blur = _generate_shader_class('''
float TAU = 6.28318530718;

out_color = texture2D(image, coords);
float i_qual = 1.0 / quality;

for (float phi = 0.0; phi < TAU; phi += TAU * i_qual * i_qual)
    for (float i = i_qual; i <= 1.0; i += i_qual)
        out_color += texture2D(image, coords + vec2(cos(phi) / width, sin(phi) / height) * radius * i);

out_color *= i_qual * i_qual * i_qual;
''', '', [
    ShaderVariable('quality', ShaderVariableType.FLOAT, 5.5),
    ShaderVariable('radius', ShaderVariableType.FLOAT, 10)
])
