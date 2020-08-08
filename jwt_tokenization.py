import jwt


mytoken = jwt.encode({'Abhay':'Pandey'}, 'Itsasecretletskeepitasone')

print(mytoken)
# print(jwt.decode(mytoken))    # Gives an error as it doesn't have the appropriate token
print(jwt.decode(mytoken, 'Itsasecretletskeepitasone'))
