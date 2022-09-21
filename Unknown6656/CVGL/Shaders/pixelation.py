from .. import ShaderVariable, ShaderVariableType, _generate_shader_class


Pixelation = _generate_shader_class('''
if (size >= 0.5)
{
    vec2 scale = vec2(width, height) / size;
    out_color = texture2D(image, floor(coords * scale) / scale);
}
''', '', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 10)
])


HexagonalPixelation = _generate_shader_class('''
ivec2 hex_index = hexIndex(coords);
vec2 hex_coords = hexCoord(hex_index);

out_color = texture2D(image, hex_coords);
''', '''
#define H (size / max(width, height))
#define S (0.86602540378 * H)

vec2 hexCoord(const ivec2 hex_index)
{
    const int i = hex_index.x;
    const int j = hex_index.y;

    return vec2(
        i * S / width * height,
        j * H + (i % 2) * H * 0.5
    );
}

ivec2 hexIndex(const vec2 coord)
{
    const float x = coord.x / height * width;
    const float y = coord.y;

    const int it = int(x / S);
    const float yts = y - float(it % 2) * H * 0.5;
    const int jt = int(1.0 / H * yts);
    const float xt = x - it * S;
    const float yt = yts - jt * H;
    const int deltaj = yt > H * 0.5 ? 1 : 0;
    const float fcond = S * 0.66666666666 * abs(0.5 - yt / H);

    if (xt > fcond)
        return ivec2(it, jt);
    else
        return ivec2(
            it - 1,
            jt - ((it - 1) % 2) + deltaj
        );
}
''', [
    ShaderVariable('size', ShaderVariableType.FLOAT, 20)
])
