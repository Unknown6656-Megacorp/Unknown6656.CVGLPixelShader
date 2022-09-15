# Unknown6656.CVGLPixelShader
This is a small package wich enables the modification of OpenCV or NumPy images using OpenGL pixel shaders written in GLSL.

### Download / Installation
1. Install the package using `pip install Unknown6656.CVGLPixelShader`
2. Insert the following import statements into your Python code:
   ```python
   from Unknown6656.CVGLPixelShader import *
   import cv2
   ```

### Basic Example
Create a new shader by invoking the constructor `PixelShader(...)` as follows:
```python
my_shader = PixelShader('''
    vec4 color = texture(image, coords);

    out_color = vec4(1 - color.xyz, 1);
''')
```
The code segment passed to the constructor is GLSL code and will be inserted into the fragment shader of the program. Have a look at the [official GLSL documentation pages](https://www.khronos.org/opengles/sdk/docs/manglsl/docbook4/) from Khronos for more information on how to use the shader language.

The shader can then be used as follows:
```python
image_in = cv2.imread('.../path/to/image.png')   # read the input image from file
image_out = my_shader(image_in)                  # process the image using the pixel shader
cv2.imwrite('.../path/to/output.png', image_out) # save the processed image

my_shader.close()                                # close the shader and free all
                                                 # underlying resources
```
You may want to replace a call to `PixelShader.close(self)` with the usage of `with`-statement blocks:


```python
with PixelShader('''
    vec4 color = texture(image, coords);

    out_color = vec4(1 - color.xyz, 1);
''') as my_shader:
    image_in = cv2.imread('.../path/to/image.png')
    image_out = my_shader(image_in)
    cv2.imwrite('.../path/to/output.png', image_out)
```


### Using Variables
You may sometimes want to pass variables to the shader. This can be performed as follows:

1. **Create a new shader variable:**
   ```python
   my_variable = ShaderVariable('time', ShaderVariableType.FLOAT)
   ```
   This code creates a new variable with the name `'time'` and the type `float` (32-bit IEE754 floating-point value). Take a look at the enum `ShaderVariableType` for all supported shader variable types.

2. **Create a new shader and pass all variables to the shader:**
   ```python
   my_shader = PixelShader('''
       out_color = texture(image, coords);
       out_color.x += sin(time);
   ''', variables = [my_variable])
   ```
   Note that the GLSL code makes usage of the variable `time` in the line `out_color.x += sin(time);`.

3. **Assign a value to the variable:**
   ```python
   my_shader[my_variable] = time.time()
   ```

4. **Use the shader:**
   ```python
   image_out = my_shader(image_in)
   ```

#### Complete example:
```python
image = cv2.imread('...../image.png')
v_time = ShaderVariable('time', ShaderVariableType.FLOAT)
time = 0

with PixelShader('''
    out_color = texture(image, coords);
    out_color.x += sin(time * 2) * .5;
''', '', [v_time]) as shader:
    while True:
        time += .01
        shader[v_time] = time
        image = shader(image)

        cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
```

## Notes:
Please keep the following in mind:
1. This library is still in beta. Some bugs may occur.
2. You may declare multiple shaders and use them independently from each other. Please keep in mind that the image processing is still performed synchroniously in the background, meaning that two shaders cannot process an image at exactly the same time (at least on a per-process basis).
