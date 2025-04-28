def print_pattern(n):
    for i in range (1,n+1):
         print(i*"*")
    for j in range (1,n+1):
        print (j)
        print(j*"*")
print_pattern(5)


def fibanocci(n):
    a,b=0,1
    for i in range (n):
        print(a,end=" ")
        a,b=b,a+b
fibanocci(10)