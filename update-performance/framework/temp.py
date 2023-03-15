def call_it(function, argje):
    print('call_it runs')
    function(argje)
    print('call_it done')

def lam(argje):
    print('lam runs')
    print(argje)
    print('lam done')


print('cally')

call_it(lam, 'argje')
# print('call_it s')
# call_it(lambda: print("Hello"))
# call_it(lambda: print("Hello2"))


# def func2(text):
#     return text.upper()
#
# def func3(text):
#     return text.lower()
#
# def func1(func):
#     # storing the function in a variable
#     res = func("Hello World")
#     print(res)
#
# #funtion calls
# func1(func2)
# func1(func3)