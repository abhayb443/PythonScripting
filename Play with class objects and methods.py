

"""
kirk = ["James Kirk", 34, "Captain", 2265]
spock = ["Spock", 35, "Science Officer", 2254]
mccoy = ["Leonard McCoy", "Chief Medical Officer", 2266]


class Dog:

    # Class attribute
    species = "Canis familiaris"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    # Instance method
    # def description(self):
    #     return f"{self.name} is {self.age} years old"

    # Replace .description() with __str__()
    def __str__(self):
        return f"{self.name} is {self.age} years old"

    # Another instance method
    def speak(self, sound):
        return f"{self.name} says {sound}"


d = Dog("Buddy", 2)
print(d)

print(d.name, d.species, d.age)

d.age = 3

print(d.name, d.species, d.age)

print(d, 'and', d.speak('Wooooo'))

print(isinstance(d, Dog))
print()


import pickle, json, jsons
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
pickled_object = pickle.dumps(d)

r.set('Test_Key', pickled_object)
unpacked_object = pickle.loads(r.get('Test_Key'))
print(d == unpacked_object)
print(unpacked_object)
print(pickled_object)
print()

# or

data = 'object : {}'.format(d)
json_object = json.dumps(data)
r.set('Test_Key-1', json_object)
unpacked_object = json.loads(r.get('Test_Key-1'))
print(json_object)
print(unpacked_object)
# print(d == unpacked_object)
# or

"""

"""
class A:
    a = "I am a class attribute!"

x = A()
y = A()
print(x)
print(y)
print(x.a)
print(y.a)
print()

x.a = "This creates a new instance attribute for x!"

print()
print(y.a)
print(A.a)
A.a = "This is changing the class attribute 'a'!"
print(A.a)
print(y.a)
print(x.a)
print()
print()

print(x.__dict__)
print(y.__dict__)
print(A.__dict__)

print()
print()

print(x.__class__.__dict__)
"""

"""
class c:
    counter= 0

    def __init__(self):
        type(self).counter += 1

    def __del__(self):
        type(self).counter -= 1


if __name__ == '__main__':
    x = c()
    print("Number of instances : "+str(c.counter))
    y = c()
    print("Number of instances : " + str(c.counter))
    del x
    print("Number of instances : " + str(c.counter))
    del y
    print("Number of instances : " + str(c.counter))
    
"""

"""
class Robot:
    __counter = 0

    def __init__(self):
        type(self).__counter += 1

    def RobotInstances(self):
        return Robot.__counter


if __name__=="__main__":
    x = Robot()
    print(x.RobotInstances())
    y = Robot()
    print(y.RobotInstances())
    z = Robot()
    print(z.RobotInstances())

"""

"""
class Robot:
    __counter = 0

    def __init__(self):
        type(self).__counter += 1

    # @staticmethod
    # def RobotInstances():
    #     return Robot.__counter

    @classmethod
    def RobotInstances(cls):
        return cls, Robot.__counter


if __name__=="__main__":
    print(Robot.RobotInstances())
    x = Robot()
    print(x.RobotInstances())
    y = Robot()
    print(x.RobotInstances())
    y = Robot()
    print(Robot.RobotInstances())

    for i in Robot.RobotInstances():
        print(i)

"""


"""
class Pet:
    _class_info = "pet animals"

    # Instance Method
    # def about(self):
    #     print("This class is about " + self._class_info + "!")

    # @staticmethod
    # def about():
    #     print("This class is about " + Pet._class_info + "!")

    @classmethod
    def about(cls):
        print("This class is about " + cls._class_info + "!")

class Dog(Pet):
    _class_info = "man's best friends"


class Cat(Pet):
    _class_info = "all kinds of cats"


# Instance Method         Accessible by all classes
# p = Pet()
# print(p.about())
# d = Dog()
# print(d.about())
# c = Cat()
# print(c.about())

# static Method          Only Accessible by the same class
# Pet.about()
# Dog.about()
# Cat.about()

# Class Method          Accessible by all classes
# Pet.about()
# Dog.about()
# Cat.about()

"""

# https://www.geeksforgeeks.org/python-classes-and-objects/
# https://www.python-course.eu/python3_class_and_instance_attributes.php
