def multiply(x,y):
    n = max(len(x), len(y))
    if n<=1 :
        return x*y
    else:
        xl , xr = #leftmost n/2, rightmost n/2 bits of x
        yl , yr = #leftmost n/2, rightmost n/2 bits of y
        p1 = multiply(xl, yl)
        p2 = multiply(xr, yr)
        p3 = multiply(xl+xr, yl+yr)
        return p1*pow(2,n)+(p3-p1-p2)*pow(2,(n/2))+p2

        