from ..pixel_shader import np, PixelShader


def SinglePassConvolution(matrix : np.ndarray, normalize = False, grayscale = False) -> PixelShader:
    if len(matrix.shape) != 2:
        raise Exception('This method only accepts 2x2 numpy matrices as image convolution kernels.')

    if normalize:
        matrix /= matrix.sum()

    code = f'''
    vec2 scale = 1 / vec2(width, height);
    vec4 color = vec4(0.0)
    '''

    for row in range(rows := matrix.shape[0]):
        for col in range(cols := matrix.shape[1]):
            code += f'        + {matrix[row, col]} * texture2D(image, vec2({col - cols / 2}, {row - rows / 2}) * scale + coords) // row={row}, col={col}\n'

    code += f''';
    out_color = color;
    {"out_color.rgb = vec3(length(out_color.rgb));" if grayscale else ""}
    '''

    return PixelShader(code)


def TwoPassConvolution(horizontal : np.ndarray, vertical : np.ndarray, normalize = False, grayscale = False) -> PixelShader:
    if len(horizontal.shape) != 2 or len(vertical.shape) != 2:
        raise Exception('This method only accepts 2x2 numpy matrices as image convolution kernels.')

    if normalize:
        horizontal /= horizontal.sum()
        vertical /= vertical.sum()

    code = f'''
    vec2 scale = 1 / vec2(width, height);
    vec4 horizontal = vec4(0.0)
    '''

    for row in range(rows := horizontal.shape[0]):
        for col in range(cols := horizontal.shape[1]):
            code += f'        + {horizontal[row, col]} * texture2D(image, vec2({col - cols / 2}, {row - rows / 2}) * scale + coords)\n'

    code += ''';
    vec4 vertical = vec4(0.0)
    '''

    for row in range(rows := vertical.shape[0]):
        for col in range(cols := vertical.shape[1]):
            code += f'        + {vertical[row, col]} * texture2D(image, vec2({col - cols / 2}, {row - rows / 2}) * scale + coords)\n'

    code += f''';
    out_color = sqrt(vertical * vertical + horizontal * horizontal);
    {"out_color.rgb = vec3(length(out_color.rgb));" if grayscale else ""}
    '''

    return PixelShader(code)


def Emboss(strength : float = 1) -> PixelShader:
    return SinglePassConvolution(np.array([
        [2 * strength,  strength,             0],
        [    strength,         1,     -strength],
        [           0, -strength, -2 * strength],
    ]))


def Sobel(grayscale = False) -> PixelShader:
    return TwoPassConvolution(np.array([
        [1, 0, -1],
        [2, 0, -2],
        [1, 0, -1],
    ]), np.array([
        [1, 2, 1],
        [0, 0, 0],
        [-1, -2, -1],
    ]), grayscale = grayscale)


def SobelFeldman(grayscale = False) -> PixelShader:
    return TwoPassConvolution(np.array([
        [3, 0, -3],
        [10, 0, -10],
        [3, 0, -3],
    ]), np.array([
        [3, 10, 3],
        [0, 0, 0],
        [-3, -10, -3],
    ]), grayscale = grayscale)


def Prewitt(grayscale = False) -> PixelShader:
    return TwoPassConvolution(np.array([
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1],
    ]), np.array([
        [1, 1, 1],
        [0, 0, 0],
        [-1, -1, -1],
    ]), grayscale = grayscale)


def Roberts(grayscale = False) -> PixelShader:
    return TwoPassConvolution(np.array([
        [1, 0],
        [0, -1],
    ]), np.array([
        [0, 1],
        [-1, 0],
    ]), grayscale = grayscale)


def LineDetection(grayscale = False) -> PixelShader:
    return TwoPassConvolution(np.array([
        [-1, -1, -1],
        [2, 2, 2],
        [-1, -1, -1],
    ]), np.array([
        [-1, 2, -1],
        [-1, 2, -1],
        [-1, 2, -1],
    ]), grayscale = grayscale)


def EdgeDetection(grayscale = False) -> PixelShader:
    return SinglePassConvolution(np.array([
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1],
    ]), grayscale = grayscale)
