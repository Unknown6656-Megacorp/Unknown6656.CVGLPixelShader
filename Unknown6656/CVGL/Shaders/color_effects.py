from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Invert = _generate_shader_class('out_color = mix(out_color, 1 - out_color, strength);', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Grayscale = _generate_shader_class('''
const float gray = ciegray(out_color.rgb);
out_color.rgb = mix(out_color.rgb, vec3(gray), clamp(strength, 0, 1));
''', '', [
    ShaderVariable('strength', ShaderVariableType.FLOAT, 1)
])


Saturation = _generate_shader_class('''
const float gray = ciegray(out_color.rgb);
out_color.rgb = mix(vec3(gray), out_color.rgb, clamp(saturation, 0, 1000000));
''', '', [
    ShaderVariable('saturation', ShaderVariableType.FLOAT, 1)
])


Sepia = _generate_shader_class('''
const float gray = ciegray(out_color.rgb);
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
vec3 hsv = rgb2hsv(out_color.rgb);
const float h = hsv.x + hue / TAU;

hsv.x = h - floor(h);

out_color.rgb = hsv2rgb(hsv);
''', '', [
    ShaderVariable('hue', ShaderVariableType.FLOAT, 0)
])


RGBLinearSplit = _generate_shader_class('''
const vec2 offs = vec2(
    cos(direction) / width,
    sin(direction) / height
) * size;

out_color.r = texture2D(image, coords - offs).r;
out_color.b = texture2D(image, coords + offs).b;
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 20),
    ShaderVariable('direction', ShaderVariableType.FLOAT, 0),
])


RGBRadialSplit = _generate_shader_class('''
vec2 scale = 1.0 + size / vec2(width, height);
vec2 scale2 = 1.0 + size * 2.0 / vec2(width, height);

out_color.g = texture2D(image, (coords - center) / scale + center).g;
out_color.b = texture2D(image, (coords - center) / scale2 + center).b;
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 20),
    ShaderVariable('center', ShaderVariableType.FLOAT_2, [.5, .5]),
])



# TODO:
# - saturation
