from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Blur = _generate_shader_class('''
const float TAU = 6.28318530718;
float i_qual = 1.0 / quality;

for (float phi = 0.0; phi < TAU; phi += TAU * i_qual * i_qual)
    for (float i = i_qual; i <= 1.0; i += i_qual)
        out_color += texture2D(image, coords + vec2(cos(phi) / width, sin(phi) / height) * radius * i);

out_color *= i_qual * i_qual * i_qual;
''', '', [
    ShaderVariable('quality', ShaderVariableType.FLOAT, 5.5),
    ShaderVariable('radius', ShaderVariableType.FLOAT, 10)
])


Bloom = _generate_shader_class('''
vec3 bloom = vec3(0.0);
float i_qual = 1.0 / quality;

const float EPS = 1.0e-10;
const float TAU = 6.28318530718;
const vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);

for (float phi = 0.0; phi < TAU; phi += TAU * i_qual * i_qual)
    for (float i = i_qual; i <= 1.0; i += i_qual)
    {
        const vec3 texsample = texture2D(image, coords + vec2(cos(phi) / width, sin(phi) / height) * radius * i).rgb;
        const vec4 p = mix(vec4(texsample.bg, K.wz), vec4(texsample.gb, K.xy), step(texsample.b, texsample.g));
        const vec4 q = mix(vec4(p.xyw, texsample.r), vec4(texsample.r, p.yzx), step(p.x, texsample.r));
        const float d = q.x - min(q.w, q.y);

        bloom += texsample * smoothstep(threshold, 1, (1.0 - d / (q.x + EPS)) * q.x);
    }

bloom *= i_qual * i_qual * i_qual;
out_color.rgb += bloom * intensity;
''', '', [
    ShaderVariable('intensity', ShaderVariableType.FLOAT, 1.6),
    ShaderVariable('threshold', ShaderVariableType.FLOAT, 0.75),
    ShaderVariable('quality', ShaderVariableType.FLOAT, 6),
    ShaderVariable('radius', ShaderVariableType.FLOAT, 40),
])
