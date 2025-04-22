def add_numbers(a,b):return a+b
def subtract_numbers(a,b):return a-b
def multiply_numbers(a,b):return a*b
def divide_numbers(a,b):return a/b if b!=0 else "Division by zero error"

# Some comments
class Calculator:
    def __init__(self):
        """
        Initialize a new calculator instance.
        """
        self.history=[]

    def add(self,a,b):
        """
        Add two numbers and store the result in history.

        Parameters
        ----------
        a (float)
            The first number.
        b (float)
            The second number.

        Returns
        -------
        float
            The sum of a and b.
        """
        result=add_numbers(a,b)
        self.history.append(f"Added {a} to {b} got {result}")
        return result

    def subtract(self,a,b):
        """
        Subtract two numbers and store the result in history.

        Parameters
        ----------
        a (float)
            The first number.
        b (float)
            The second number.

        Returns
        -------
        float
            The difference between a and b.
        """
        result=subtract_numbers(a,b)
        self.history.append(f"Subtracted {b} from {a} got {result}")
        return result

    def multiply(self,a,b):
        """
        Multiply two numbers and store the result in history.

        Parameters
        ----------
        a (float)
            The first number.
        b (float)
            The second number.

        Returns
        -------
        float
            The product of a and b.
        """
        result=multiply_numbers(a,b)
        self.history.append(f"Multiplied {a} with {b} got {result}")
        return result

    def divide(self,a,b):
        """
        Divide two numbers and store the result in history.

        Parameters
        ----------
        a (float)
            The first number.
        b (float)
            The second number.

        Returns
        -------
        float
            The quotient of a and b or error message if division by zero.
        """
        result=divide_numbers(a,b)
        self.history.append(f"Divided {a} by {b} got {result}")
        return result

    def print_history(self):
        """
        Print the history of all operations performed.
        """
        for record in self.history:
            print(record)

if __name__=="__main__":
    calc=Calculator()
    print(calc.add(5,3))
    print(calc.subtract(10,4))
    print(calc.multiply(2,7))
    print(calc.divide(8,2))
    print(calc.divide(5,0))
    calc.print_history()