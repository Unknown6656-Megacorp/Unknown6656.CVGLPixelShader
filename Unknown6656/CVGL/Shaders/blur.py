from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Blur = _generate_shader_class('out_color = blur(coords, radius, quality);', '', [
    ShaderVariable('quality', ShaderVariableType.FLOAT, 5.5),
    ShaderVariable('radius', ShaderVariableType.FLOAT, 10)
])


LinearBlur = _generate_shader_class('''
float phi = direction;
float i_qual = 1.0 / quality;
vec2 scale = size * .5 / vec2(width, height);

for (float i = -1.0; i <= 1.0; i += i_qual)
{
    vec2 c = coords + i * scale * vec2(cos(phi), sin(phi));
    out_color += texture2D(image, c);
}

out_color /= 2 * quality + 1;
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 10),
    ShaderVariable('direction', ShaderVariableType.FLOAT, 0),
    ShaderVariable('quality', ShaderVariableType.FLOAT, 5),
])


RadialBlur = _generate_shader_class('''
float i_qual = 1.0 / quality;
vec2 scale = size / vec2(width, height);

for (float i = -2.0; i <= 2.0; i += i_qual)
{

    vec2 c = (coords - center) * (1 + scale * i) + center;
    out_color += texture2D(image, c);
}

out_color /= 4 * quality + 1;
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 10),
    ShaderVariable('center', ShaderVariableType.FLOAT_2, [.5, .5]),
    ShaderVariable('quality', ShaderVariableType.FLOAT, 5),
])


# TODO : concentric blur


Bloom = _generate_shader_class('''
vec3 bloom = vec3(0.0);
float i_qual = 1.0 / quality;

const float EPS = 1.0e-10;
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



___TODO___ChromaticAbberation = _generate_shader_class('''
#define BLUR 1

const float scale_factor = 23.0 / max(width, height);
vec2 scale = (1.0 + scale_factor) * vec2(height / width, 1);
vec2 scale2 = (1.0 + scale_factor * 2.0) * vec2(height / width, 1);

out_color.r = blur((coords - center) / scale + center, BLUR, quality).r;
out_color.g = blur((coords - center) / scale2 + center, BLUR, quality).g;
out_color.b = blur(coords, BLUR, quality).b;
''', '', [
    ShaderVariable('threshold', ShaderVariableType.FLOAT, 0.75),
    ShaderVariable('quality', ShaderVariableType.FLOAT, 6),
    ShaderVariable('radius', ShaderVariableType.FLOAT, 40),
    
    ShaderVariable('center', ShaderVariableType.FLOAT_2, [.5, .5]),
])

