# x86compiler
A toy compiler (with SLR parser, for x86_64, written in python). 

## Usage:

    python compiler.py SOURCE_FILE

## Examples:

 **Variable Declaration, Assignment, and Loading**
 
    {
    int a;
    a = 6;
    iprint(a);
    }
-> 6


**Arithmetic Operations**

    {
      int a;
      int b;
      a = 7;
      b = 3;
      iprint(a+1);
      iprint(b+1);
      iprint(a+b);
      iprint(a-b);
      iprint(a*b);
      iprint(a/b);
    }
->84104212

**Variable Scopes**

    {
      int a;
      int b;
      a = 111;
      b = 123;
      iprint(a);
      iprint(b);
      {
        int a;
        a = 777;
        iprint(a);
        iprint(b);
      }
      iprint(a);
      iprint(b);
    }
-> 111123777123111123

**Arrays**

    {
      int a[3];
      int b;
      a[0] = 1;
      a[1] = 2;
      a[2] = 3;
      b = 777;
      iprint(a[0]);
      iprint(a[1]);
      iprint(a[2]);
      iprint(b);
      {
        int a[3];
        a[0] = 4;
        a[1] = 5;
        a[2] = 6;
        iprint(a[0]);
        iprint(a[1]);
        iprint(a[2]);
        iprint(b);
      }
      iprint(a[0]);
      iprint(a[1]);
      iprint(a[2]);
      iprint(b);
    }
-> 123777456777123777

**Control Structure (IF and WHILE)**

    {
      int a;
      int b;
      a = 7;
      b = 1;
      if(a!=5){
        iprint(1);
        if(a<=5){
          iprint(0);
        }else{
          iprint(2);
        }end
      }end
      while(b<10){
        iprint(b);
        b = b+1;
      }end
    }
-> 12123456789

**Functions**

    {
      int a[3];
      int b;
      int f(int x, int y){
        int z;
    	z = x * y;
        a[1] = 777;
        iprint(a[1]);
        iprint(z);
    	return z;
        iprint(z);
      }
      int g(){
        iprint(999);
      }
      b = f(111, 3);
      g();
      iprint(b);
      iprint(a[1]);
    }
-> 777333999333777

**Recursive Call**

    {
        int a;
        int f(int n){
            if(n<1)
                return 1;
            else
                return n * f(n-1);
            end
        }
        a = f(5);
        iprint(a);
    }
-> 120

## Notes: Development environment:

 - CPU: Intel(R) Core(TM) i7-4770HQ CPU @ 2.20GHz 64 bits
 - OS: Ubuntu 14.04 LTS
 - gcc: 4.8.4 (Ubuntu 4.8.4-2ubuntu1~14.04.3)
 - python: 3.6.0
