from ctypes import POINTER, c_void_p
from typing import ClassVar
from threading import Lock

import numpy as np
import cv2

import OpenGL.GL as gl
import OpenGL.GL.shaders as gls
import glfw

from .shader_variable import *


ENABLE_GLSL_LINE_NUMBER_CORRECTION = True


class PixelShader:
    '''Represents a GLSL pixel shader. A pixel shader is a piece of OpenGL Shader Language code which, after having been compiled
    using the GLSL compiler, can be applied to any given OpenCV/NumPy image.'''

    __instances : ClassVar[int] = 0
    __mutex : ClassVar[Lock] = Lock()
    __window : ClassVar[POINTER(glfw._GLFWwindow) | None] = None
    __VAR_CODE = '%__CODE__%'
    __VAR_UNIFORMS = '%__UNIFORMS__%'
    __VAR_ADD_FUNCTIONS = '%__FUNCTIONS__%'
    __VERTEX_SHADER = """
    #version 450

    in vec2 position;
    out vec2 coords;

    void main() {
        gl_Position = vec4(position, 0.0, 1.0);
        coords = (1.0 + position) * 0.5;
    }
    """
    __FRAGMENT_SHADER = f"""
    #version 450

    in vec2 coords;
    layout (location = 0) out vec4 out_color;

    layout (location = 1) uniform int width;
    layout (location = 2) uniform int height;
    {__VAR_UNIFORMS}
    layout (binding = 0) uniform sampler2D image;

    const float TAU = 6.28318530718;

    vec4 blur(const vec2 coords, const float r, const float q)
    {{
        float i_qual = 1.0 / q;
        vec4 color = texture2D(image, coords);

        for (float phi = 0.0; phi < TAU; phi += TAU * i_qual * i_qual)
            for (float i = i_qual; i <= 1.0; i += i_qual)
                color += texture2D(image, coords + vec2(cos(phi) / width, sin(phi) / height) * r * i);

        return color * i_qual * i_qual * i_qual;
    }}

    vec3 rgb2hsv(const vec3 c)
    {{
        const vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
        const vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
        const vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
        const float d = q.x - min(q.w, q.y);
        const float e = 1.0e-10;

        return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }}

    vec3 hsv2rgb(const vec3 c)
    {{
        const vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        const vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);

        return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }}

    float ciegray(const vec3 c)
    {{
        return dot(c, vec3(0.299, 0.587, 0.114));
    }}

    {__VAR_ADD_FUNCTIONS}
    void main() {{
        out_color = texture(image, coords);

        {__VAR_CODE}

        out_color = clamp(out_color, 0, 1);
    }}
    """


    def __init__(self, shader_code : str, additional_functions : str = '', variables : list[ShaderVariable] = []):
        '''Creates a new pixel shader using the given GLSL shader code.

        Parameters
        ----------
        shader_code : str
              The OpenGL Shader Language code, which will be executed in the shader's main function. GLSL shader code may
              make usage of any defined shader variables (see "variables" parameter), any built-in or additional functions
              (see the "additional_functions" parameter), as well as the following pre-defined variables:
              - int32 width: The image width in pixels.
              - int32 height: The image height in pixels.
              - sampler2D image: The image as a 2D texture sampler with four color channels (RGBA).
              - vec2 coords: The current image coordinates, normalized to [0..1]x[0..1].
              - vec4 out_color: The output color at this position. If this variable is unused, the input color will be copied
                to the output.

        additional_functions : str
              GLSL code which is located before the main method and after the declaration of all global and uniform variables
              This code can contain, but is not limited to, local or helper functions.

        variables : list[ShaderVariable]
              A list of shader variables which can be used to pass values from Python to GLSL during runtime.
        '''
        PixelShader.__mutex.acquire()
        try:
            PixelShader.__instances = max(PixelShader.__instances + 1, 1)

            if PixelShader.__instances <= 1 or PixelShader.__window is None:
                glfw.init()
                glfw.window_hint(glfw.VISIBLE, False)
                PixelShader.__window = glfw.create_window(200, 200, '', None, None)

            glfw.make_context_current(PixelShader.__window)

            uniform_declarations = '\n'.join([f'layout (location = {i + 3}) uniform {x.type.glsl_type()} /* {x.type} */ {x.name};' for i,x in enumerate(variables)])

            if ENABLE_GLSL_LINE_NUMBER_CORRECTION:
                shader_code = '\n'.join([f'#line {i}\n{x}' for i,x in enumerate(shader_code.splitlines())])

            self._vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
            self._fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
            self._fragment_shader_code = PixelShader.__FRAGMENT_SHADER.replace(PixelShader.__VAR_CODE, shader_code) \
                                                                      .replace(PixelShader.__VAR_ADD_FUNCTIONS, additional_functions) \
                                                                      .replace(PixelShader.__VAR_UNIFORMS, uniform_declarations)

            gl.glShaderSource(self._vertex_shader, [PixelShader.__VERTEX_SHADER])
            gl.glCompileShader(self._vertex_shader)

            gl.glShaderSource(self._fragment_shader, [self._fragment_shader_code])
            gl.glCompileShader(self._fragment_shader)

            if not gl.glGetShaderiv(self._fragment_shader, gl.GL_COMPILE_STATUS):
                error = gl.glGetShaderInfoLog(self._fragment_shader)
                gl.glDeleteShader(self._fragment_shader)
                raise Exception(error)

            self._shader_program = gls.compileProgram(self._vertex_shader, self._fragment_shader)

            if not gl.glGetProgramiv(self._shader_program, gl.GL_LINK_STATUS):
                error = gl.glGetProgramInfoLog(self._shader_program)
                gl.glDeleteProgram(self._shader_program)
                raise Exception(error)

            gl.glUseProgram(self._shader_program)

            self._vertex_buffer_obj, self._element_buffer_obj = gl.glGenBuffers(2)
            self._vertices = np.array([
                -1, -1,
                1, -1,
                1,  1,
                -1,  1,
            ], np.float32)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vertex_buffer_obj)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self._vertices) * 4, self._vertices, gl.GL_STATIC_DRAW)

            self._indices = np.array([0, 1, 2, 2, 3, 0], np.uint32)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._element_buffer_obj)
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self._indices, gl.GL_STATIC_DRAW)

            position = gl.glGetAttribLocation(self._shader_program, 'position')
            gl.glVertexAttribPointer(position, 2, gl.GL_FLOAT, gl.GL_FALSE, 8, c_void_p(0))
            gl.glEnableVertexAttribArray(position)

            p_image = gl.glGetUniformLocation(self._shader_program, 'image')
            gl.glUniform1i(p_image, np.int32(0))

            self._texture_in, self._texture_out = gl.glGenTextures(2)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_in)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

            self._framebuffer = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._framebuffer)

            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_out)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

            self._variables = {var : var.default_value for var in variables}
        finally:
            PixelShader.__mutex.release()

    def close(self) -> None:
        '''Closes and destroys the GLSL shader'''
        gl.glDeleteShader(self._fragment_shader)
        gl.glDeleteShader(self._vertex_shader)
        gl.glDeleteProgram(self._shader_program)
        gl.glDeleteBuffers(2, [self._vertex_buffer_obj, self._element_buffer_obj])
        gl.glDeleteTextures(2, [self._texture_in, self._texture_out])
        gl.glDeleteFramebuffers(1, [self._framebuffer])

        PixelShader.__mutex.acquire()
        try:
            PixelShader.__instances -= 1

            if PixelShader.__instances < 1:
                glfw.destroy_window(PixelShader.__window)
                glfw.terminate()
                PixelShader.__window = None
        finally:
            PixelShader.__mutex.release()

    def get_variable(self, variable : ShaderVariable | str) -> np.float32 | np.int32 | list[np.float32] | list[np.int32] | None:
        '''Returns the value associated with the given variable.'''
        for key in self._variables:
            if key == variable or key.name == str(variable):
                return self._variables[key]
        raise Exception(f'No shader variable "{variable}" could be found. Did you forget to pass it to the constructor of the "PixelShader"-class?')

    def set_variable(self, variable : ShaderVariable | str, value : float | int | np.int32 | np.float32 | list[float] | list[int] | list[np.float32] | list[np.int32] | np.ndarray | None) -> None:
        '''Sets the value associated with the given variable.'''
        for key in self._variables:
            if key == variable or key.name == str(variable):
                match key.type:
                    case ShaderVariableType.BOOL | ShaderVariableType.INT:
                        self._variables[key] = np.int32(value)
                    case ShaderVariableType.INT_2 | ShaderVariableType.INT_3 | ShaderVariableType.INT_4:
                        self._variables[key] = [np.int32(x) for x in value]
                    case ShaderVariableType.FLOAT:
                        self._variables[key] = np.float32(value)
                    case ShaderVariableType.FLOAT_2 | ShaderVariableType.FLOAT_3 | ShaderVariableType.FLOAT_4:
                        self._variables[key] = [np.float32(x) for x in value]
                    case _:
                        raise Exception(f'The variable "{variable}" is not supported due to an unknown type. All supported types can be found in the enum class "ShaderVariableType".')
                return
        raise Exception(f'No shader variable "{variable}" could be found. Did you forget to pass it to the constructor of the "PixelShader"-class?')

    def apply(self, image : np.ndarray) -> np.ndarray:
        '''Applies the pixel shader to the given image.
        This function expects the image to be normalized to the range [0..255]. This function
        further expects the image to be two dimensional with one or three color channels, i.e.
        the image must have the following shape:
        - Height x Width
        - Height x Width x 1
        - Height x Width 3
        '''
        if PixelShader.__instances < 1:
            raise Exception('This PixelShader class instance seems to have been destroyed using the "close"-function. There are no active GLFW instances left for this ' +
                'process. Please start a new one by calling the constructor of "PixelShader".')
        if len(image) == 0:
            raise Exception('The image must not be empty.')
        elif not 1 < len(image.shape) < 4:
            raise Exception('The image must be two- or three-dimensional.')
        elif image.dtype != np.uint8:
            image = image.astype(np.uint8)

        if len(image.shape) == 2:
            image = np.repeat(image[:, :, None], 3, 2)
        elif image.shape[2] == 1:
            image = np.repeat(image, 3, 2)
        elif image.shape[2] != 3:
            raise Exception('The image must have exactly one or three color channels.')

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        width = image.shape[1]
        height = image.shape[0]

        PixelShader.__mutex.acquire()
        try:
            glfw.make_context_current(self.__window)
            glfw.set_window_size(self.__window, width, height)

            gl.glUseProgram(self._shader_program)

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vertex_buffer_obj)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._element_buffer_obj)

            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_in)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image)

            for variable in self._variables:
                value = self._variables[variable]
                if value is not None:
                    location = gl.glGetUniformLocation(self._shader_program, variable.name)
                    if location >= 0:
                        if variable.type is ShaderVariableType.BOOL or type is ShaderVariableType.INT:
                            gl.glUniform1i(location, value)
                        elif variable.type is ShaderVariableType.INT_2:
                            gl.glUniform2i(location, value[0], value[1])
                        elif variable.type is ShaderVariableType.INT_3:
                            gl.glUniform3i(location, value[0], value[1], value[2])
                        elif variable.type is ShaderVariableType.INT_4:
                            gl.glUniform4i(location, value[0], value[1], value[2], value[3])
                        elif variable.type is ShaderVariableType.FLOAT:
                            gl.glUniform1f(location, value)
                        elif variable.type is ShaderVariableType.FLOAT_2:
                            gl.glUniform2f(location, value[0], value[1])
                        elif variable.type is ShaderVariableType.FLOAT_3:
                            gl.glUniform3f(location, value[0], value[1], value[2])
                        elif variable.type is ShaderVariableType.FLOAT_4:
                            gl.glUniform4f(location, value[0], value[1], value[2], value[3])
                    # else: print(f'The variable {variable} seems to have been optimized away by the OpenGL compiler. The variable will therefore be ignored.')

            p_width = gl.glGetUniformLocation(self._shader_program, 'width')
            p_height = gl.glGetUniformLocation(self._shader_program, 'height')

            gl.glUniform1i(p_width, np.int32(width))
            gl.glUniform1i(p_height, np.int32(height))

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._framebuffer)

            image_out = np.empty(image.shape, np.uint8)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texture_out)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, c_void_p(0))

            gl.glFramebufferTexture(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, self._texture_out, 0)
            gl.glDrawBuffers(1, [gl.GL_COLOR_ATTACHMENT0])

            gl.glBindTextureUnit(np.int32(0), self._texture_in)

            gl.glViewport(0, 0, width, height)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            gl.glDrawElements(gl.GL_TRIANGLES, len(self._indices), gl.GL_UNSIGNED_INT, None)

            gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image_out)

            return cv2.cvtColor(image_out, cv2.COLOR_RGB2BGR)
        finally:
            PixelShader.__mutex.release()

    def __enter__(self): return self

    def __exit__(self, exception_type, exception_value, traceback) -> None: self.close()

    def __getitem__(self, variable : ShaderVariable | str) -> np.float32 | np.int32 | list[np.float32] | list[np.int32] | None: return self.get_variable(variable)

    def __setitem__(self, variable : ShaderVariable | str, value : float | int | np.int32 | np.float32 | list[float] | list[int] | list[np.float32] | list[np.int32] | np.ndarray | None) -> None:
        self.set_variable(variable, value)

    def __call__(self, image : np.ndarray) -> np.ndarray: return self.apply(image)

    def __eq__(self, other) -> bool: return isinstance(other, PixelShader) and int(self._shader_program) == int(other._shader_program)

    def __add__(self, other):
        if not isinstance(other, PixelShader):
            raise Exception(f'Concatenation is only permitted with two instances of "PixelShader".')

        # add: __call__
        # add: __setitem__
        # add: __getitem__
        # add: apply
        # add: get_variable
        # add: set_variable




def apply_shader(shader : type | PixelShader, image : np.ndarray, **kwargs : float | int | np.int32 | np.float32 | list[float] | list[int] | list[np.float32] | list[np.int32] | np.ndarray | None) -> np.ndarray:
    if shader == PixelShader:
        raise Exception('Please call "PixelShader(...)" before passing it to the function "apply_shader".')
    elif isinstance(shader, type):
        shader = shader(**kwargs)

    for key in kwargs:
        shader[key] = kwargs[key]

    image = shader(image)
    shader.close()

    return image
