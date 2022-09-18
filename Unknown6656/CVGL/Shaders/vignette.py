from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Vignette = _generate_shader_class('''
float vignette = smoothstep(radius, radius - softness, length(coords - .5));

out_color.rgb = mix(
    out_color.rgb,
    mix(
        color,
        out_color.rgb,
        vignette
    ),
    strength
);
''', '', [
    ShaderVariable('radius', ShaderVariableType.FLOAT, .75),
    ShaderVariable('softness', ShaderVariableType.FLOAT, .45),
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1),
    ShaderVariable('color', ShaderVariableType.FLOAT_3, [0, 0, 0])
])
