from dataclasses import dataclass
from enum import Enum
import numpy as np


class ShaderVariableType(Enum):
    '''An enumeration of possible shader variable data types. These include bool, int, ivec2, ivec3,
    ivec4, float, vec2, vec3, and vec4. Shader variables are used to pass values from Python to GLSL.

    Enumeration Fields
    ------------------
    BOOL : 0
        Represents a boolean variable (32bit). GLSL equivalent: int or bool.
    INT : 1
        Represents a 32-bit (4 byte) signed integer variable. GLSL equivalent: int.
    INT_2 : 2
        Represents a 8 byte large tuple of two 32-bit signed integer variables. GLSL equivalent: ivec2.
    INT_3 : 3
        Represents a 12 byte large tuple of three 32-bit signed integer variables. GLSL equivalent: ivec3.
    INT_4 : 4
        Represents a 16 byte large tuple of four 32-bit signed integer variables. GLSL equivalent: ivec4.
    FLOAT : 11
        Represents a 32-bit (4 byte) signed floating-point variable. GLSL equivalent: signed.
    FLOAT_2 : 12
        Represents a 8 byte large tuple of two 32-bit signed floating-point variables. GLSL equivalent: vec2.
    FLOAT_3 : 13
        Represents a 12 byte large tuple of three 32-bit signed floating-point variables. GLSL equivalent: vec3.
    FLOAT_4 : 14
        Represents a 16 byte large tuple of four 32-bit signed floating-point variables. GLSL equivalent: vec4.
    '''

    BOOL = 0
    INT = 1
    INT_2 = 2
    INT_3 = 3
    INT_4 = 4
    FLOAT = 11
    FLOAT_2 = 12
    FLOAT_3 = 13
    FLOAT_4 = 14

    def glsl_type(self) -> str:
        '''Returns the GLSL type equivalent for the given shader variable type instance.'''
        return {
            ShaderVariableType.BOOL    : 'bool',
            ShaderVariableType.INT     : 'int',
            ShaderVariableType.INT_2   : 'ivec2',
            ShaderVariableType.INT_3   : 'ivec3',
            ShaderVariableType.INT_4   : 'ivec4',
            ShaderVariableType.FLOAT   : 'float',
            ShaderVariableType.FLOAT_2 : 'vec2',
            ShaderVariableType.FLOAT_3 : 'vec3',
            ShaderVariableType.FLOAT_4 : 'vec4',
        }[self]

@dataclass
class ShaderVariable:
    '''Represents a shader variable which is characterized by its name and shader variable type.

    NOTE: Shader variable names are case-sensitive!'''
    name : str
    type : ShaderVariableType
    default_value : float | int | np.int32 | np.float32 | list[float] | list[int] | list[np.float32] | list[np.int32] | np.ndarray | None = None


    def __repr__(self) -> str:
        '''Returns the string representation of the shader variable, which equates to "<type> <name>".'''
        return f'{self.type.name} {self.name}{"" if self.default_value is None else f" = {self.default_value}"}'

    def __hash__(self) -> int:
        '''Returns the hash value of the shader varialbe, which is determined by the hash value of the shader variable's name'''
        return self.name.__hash__()
