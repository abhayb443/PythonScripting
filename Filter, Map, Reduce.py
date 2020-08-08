import collections
from pprint import pprint
from functools import reduce
import itertools


mylist = collections.namedtuple('mylist', ['rollnumber', 'name', 'WorkStatus', 'boolean'])

# mylist = ((1, 'Abhay', 'Employeed', True),
#         (2, 'Dipen', 'Studying', False),
#         (3, 'Chetan', 'Employeed', True),
#         (4, 'Arpit', 'Employeed', True),
#         (5, 'Arpit Pandye', 'Employeed', False),
#         (6, 'Akshay', 'Employeed', True))


mylist = (
        mylist(rollnumber=1, name='Abhay', WorkStatus='Employeed', boolean=True),
        mylist(rollnumber=2, name='Dipen', WorkStatus='Studying', boolean=False),
        mylist(rollnumber=3, name='Chetan', WorkStatus='Employeed', boolean=True),
        mylist(rollnumber=4, name='Arpit', WorkStatus='Employeed', boolean=True),
        mylist(rollnumber=5, name='Arpit Pandye', WorkStatus='Employeed', boolean=False),
        mylist(rollnumber=6, name='Akshay', WorkStatus='Employeed', boolean=True)
          )

pprint(mylist)

print()
pprint(list(filter(lambda x: x.boolean is True, mylist)))
fs = filter(lambda x: x.boolean is True, mylist)

print()
print(next(fs))
print(next(fs))
print(next(fs))
print(next(fs))
# print(next(fs))

print()
pprint(tuple(filter(lambda x: x.boolean is True, mylist)))

print()
pprint(tuple(filter(lambda x: x.boolean is True, mylist)))

print()
pprint(tuple(filter(lambda x: x.WorkStatus is 'Employeed', mylist)))

# Another cleaner way to filter the data

def nobel_filter(x):
        return x.boolean is True

print()
pprint(tuple(filter(nobel_filter, mylist)))

# Filtering List Comprehensions

print()
pprint([x for x in mylist if x.boolean is True])

# Using Tuple Comprehension via generators (), Generator Expression
print()
pprint(tuple(x for x in mylist if x.boolean is True))


# Map with Tuple of dictionary
print()
names_and_rollno = tuple(map(lambda x: {'name': x.name, 'id': x.rollnumber}, mylist))
pprint(names_and_rollno)

# Map with List of dictionary
print()
names_and_rollno = list(map(lambda x: {'name': x.name, 'id': x.rollnumber}, mylist))
pprint(names_and_rollno)

# Normal way via list comprehension with condition
names_rollno =[
                {'name': x.name, 'rollno': x.rollnumber}
                for x in mylist if x.rollnumber > 2
               ]
print()
pprint(names_rollno)

# Map with Generator
print()
pprint(tuple({'name': x.name, 'rollnumber': x.rollnumber} for x in mylist))

# Reduce
total_roles = reduce(lambda acc, val: acc + val[0],
                     mylist,
                     0)
print()
print(total_roles)

# Doing more with reduce
def reducer(acc, val):
    acc[val.WorkStatus].append((val.name))
    return acc

print()
names_with_status = reduce(reducer, mylist, {'Employeed': [], 'Studying': []})
pprint(names_with_status)

# Better way to do the same above with reduce
print()
names_with_enh_status = reduce(
        reducer,
        mylist,
        collections.defaultdict(list)
)

pprint(names_with_enh_status)

# Default Dict Example
def_list_Instance = collections.defaultdict(list)
print()
print(def_list_Instance)
print(def_list_Instance['Hello'])
print(def_list_Instance)
print(def_list_Instance['Hey'])
print(def_list_Instance)

# Group by
print()
group_by_example = {
        item[0] : list(item[1])
        for item in itertools.groupby(mylist, lambda x: x.name)
}

pprint(group_by_example)
