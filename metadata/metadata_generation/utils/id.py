# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

class IDGenerator: 


    def __init__(self):
        self.__next_id = 0

    
    def get_id(self): 
        current_id = self.__next_id
        self.__next_id += 1
        return current_id

