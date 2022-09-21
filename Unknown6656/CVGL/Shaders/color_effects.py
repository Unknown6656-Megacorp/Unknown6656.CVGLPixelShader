from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Invert = _generate_shader_class('out_color = mix(out_color, 1 - out_color, strength);', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Grayscale = _generate_shader_class('''
const vec3 gray = vec3(dot(out_color.rgb, vec3(0.299, 0.587, 0.114)));
out_color.rgb = mix(out_color.rgb, gray, clamp(strength, 0, 1));
''', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Saturation = _generate_shader_class('''
const vec3 gray = vec3(dot(out_color.rgb, vec3(0.299, 0.587, 0.114)));
out_color.rgb = mix(gray, out_color.rgb, clamp(saturation, 0, 1000000));
''', '', [
    ShaderVariable('saturation', ShaderVariableType.FLOAT, 1)
])


Sepia = _generate_shader_class('''
float gray = dot(out_color.rgb, vec3(0.299, 0.587, 0.114));

out_color.rgb = mix(out_color.rgb, gray * color, strength);
''', '', [
    ShaderVariable('color', ShaderVariableType.FLOAT_3, [1.2, 1.0, 0.8]),
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Brightness = _generate_shader_class('out_color.rgb += brightness;', '', [
    ShaderVariable('brightness', ShaderVariableType.FLOAT, 0)
])


Contrast = _generate_shader_class('out_color.rgb = (out_color.rgb - .5) * contrast + .5;', '', [
    ShaderVariable('contrast', ShaderVariableType.FLOAT, 1)
])


Hue = _generate_shader_class('''
const float TAU = 6.28318530718;
vec3 hsv = rgb2hsv(out_color.rgb);
const float h = hsv.x + hue / TAU;

hsv.x = h - floor(h);

out_color.rgb = hsv2rgb(hsv);
''', '''
vec3 rgb2hsv(const vec3 c)
{
    const vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    const vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    const vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    const float d = q.x - min(q.w, q.y);
    const float e = 1.0e-10;

    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(const vec3 c)
{
    const vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    const vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);

    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
''', [
    ShaderVariable('hue', ShaderVariableType.FLOAT, 0)
])



# TODO:
# - saturation
