
    usage as decorator:
    TCOP = TimeCop()

    @TCOP
    def my_func():
        # stuff
        pass

    print("mean execution time of my_func = " + TCOP[my_func].mean)

    usage as contextmanager:
    with TCOP.open("my_context"):
        #stuff
        pass

    print(TCOP["my_context"])

    usage as contextmanager with default name:
    with TCOP:
        #stuff
        pass

    print(TCOP["default"])
