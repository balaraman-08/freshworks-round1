def create():
    print("Create function called")


def read():
    print("Read function called")


def delete():
    print("Delete function called")


options = {
    "1": {"name": "CREATE", "function": create},
    "2": {"name": "READ", "function": read},
    "3": {"name": "DELETE", "function": delete},
    "4": {"name": "EXIT (Press q)", "function": lambda exit: exit(0)}
}


def listOptions():
    for key, option in options.items():
        print("{}. {}".format(key, option["name"]))

def getOperation():
    listOptions()
    while True:
        option = input("\nSelect any option (1 - 4): ")
        if option == "q" or option == "4":
            exit(0)
        elif not option.isnumeric():
            print("Option not valid")
            continue            
        elif 4 < int(option) < 0:
            print("Option not valid")
            continue   
        selectedOption = options[option]
        selectedFuntion = selectedOption["function"]
        selectedFuntion()


#driver code
getOperation()