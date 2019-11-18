
def trial():
    code = '''
import numpy as np
def sum(a, b):
    return a + b
print("sum =",sum(5, 6))
x = np.zeros((2, 3))
print(x)
    '''
    codeObject = compile(code, 'sumstring', 'exec')

    exec(codeObject)


if __name__ == '__main__':
    trial()