from langchain.tools import tool

#Step1. To create your own custom tool, all you need is to create an function and add an tool decorator above the function declaration. 
#Step2. An function should have a good description which is necessary and if you're giving any input paramters make sure to have an good function definition like its datatype and default value (if provided then good). 
#Step3. Append your function in the main.py by adding an line call: tools.append('your-function-name'). for instance, tools.append(say_hello_to_user). #Remember do not call the function just write the name. 

@tool #necessary
def say_hello_to_user(username: str = 'Apsara') -> str: 
    #An function description is necessary 
    """
    This tool says hello to a user.

    Args:
        username: str: The name of the user to say hello to.

    Returns:
        A string containing the greeting.
    """
    return f"Hello, {username}!"

if __name__ == '__main__':
    pass