import numpy as np

nlist = [12,45,74,869,154]

nparrary = np.array(nlist)

print(nparrary)
print(type(nparrary))

for i in nlist:
    print(i)

print()

for j in nparrary:
    print(j)

nlist = nlist + [5]
print(nlist)

nlist.append(6)
print(nlist)

# In numpy array, if we try to do the same i.e. add via +, it does the vector addition
print()
print(nparrary)
nparrary = nparrary + [5]
print(nparrary)
# nparrary.append(5)    # This will give an error as there is no append property in np
# print(nparrary)

print()

# Vector addition in numpy
nparrary = nparrary + nparrary
print(nparrary)

# For appending the value
nparrary = nlist + nlist
print(nparrary)

print()

# Vector addition within the same list
L3 = []
for i in nlist:
    L3.append(i+i)

print(L3)

print()

# Scalar multiply by vector
print(nlist)
nplist = np.array(nlist)

L4 = 2*nplist               # On Np List
print(L4)

L5 = 2*nlist               # On normal List
print(L5)

# Power of

print(nplist**2)
# print(pow(nlist))           # Error not supported

print()

# Square root , Log, Exponential
L7 = np.array([1, 2, 3])
print(np.sqrt(L7))
print()
print(np.log(L7))
print()
print(np.exp(L7))

print()

L8 = [4, 5, 6]
L9 = [[4, 5], [5, 6], [6, 7]]

print(L8[0])
print(L9[1][0])
# print(L9[1,0])                  # Error List must be integer or slices, not tuple

L10 = np.matrix([[4, 5], [5, 6], [6, 7]])
print(L10)
print(L10[0,0])                  # Line 85 declaration works on matrix only

# Transpose
print()
print(L10)
L11 = L10.T
print(L11)

# Shape
print()
print(L11.shape)

# Transposing the shape and checking shape
L12 = L11.T
print(L12.shape)

print(L12.ndim)
print(L12.size)
print(L12.dtype)

print()
L13 = np.array([1.1, 1.2, 1.3])
print(L13.dtype)

L13 = np.array([1.1, 1.2, 1.3], dtype=float)
print(L13.dtype)

print(L12.itemsize)
print(L13.itemsize)

print(L13.min())
print(L13.max())
print(L13.sum())

# Sum of matrix 0
print()
L14 = np.array([[1, 2], [3, 4], [5, 6]])
print(L14.sum(axis=0))                          # Vertical Addition
print(L14.sum(axis=1))                          # Horizontal Addition

print()
L15 = np.zeros((2, 5))
print(L15)

print()
L16 = np.ones((2, 5))
print(L16)

print()
L17 = np.ones((2, 5), dtype=np.int16)
print(L17)

print()
L18 = np.empty((2, 5), dtype=np.int16)
print(L18)

print(np.arange(1, 5))
print()
print(np.arange(1, 5, 2))
print()
print(np.linspace(1, 5))
print()
print(np.linspace(1, 5, 10))
print()
print(np.random.random((2,3)))
print()
print(L18.reshape((3,2)))           # Reshape of array with invalid size
print()
L19 = np.zeros((2,3))
print(L19.reshape((2,3)))
print()
print(L19.reshape((3,2)))
print()
print(L19.reshape((6,1)))

print()
L20 = np.ones((1, 8))
print(L20)
print()

d = np.ones((1,9))
print(d)
L21 = d.reshape((-1, 3))
print(L21)

h = np.zeros((3, 1))
g = np.zeros((3, 1))
print(np.vstack((g, h)))
print()
print(np.hstack((g, h)))

i = np.zeros((3, 3))
print()
print(i)
print()
print(np.hsplit(i, 1))
print()
print(np.vsplit(i, 3))
