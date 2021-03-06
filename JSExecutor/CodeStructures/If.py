from . import Types
import Exceptions
from .CodeBlock import index_check,CodeBlock

'''
branches:
    ((condition)(operations)(condition))

operation - ()

operations:
    ('var',variable_name,(one,two,+,...)) / (1,2,3),func / (1,2)|1,list
    ('var_change',variable_name,(one,two,+,...)) / variable_name = ''|variable name=()
    ('let',variable_name,(one,two,+,...))
    ('function',function_name,(input_arguments),(operations))
    ('loop',Loop())
    ('return',(one,two,+,...))
    ('if',If())
        ('if_condition',(one,two,+,...))
    ('try',Try())
    
'''


class If(CodeBlock):
    def __init__(self,branches:tuple):
        self.conditions = []
        self.operations = []

        branch_index = -1
        for item in branches:
            if item[0] == 'if_condition':
                self.conditions.append(item[1])
                branch_index += 1
                self.operations.append([])
            else:
                self.operations[branch_index].append(item)

        self.conditions = tuple(self.conditions)  

    def execute(self,global_variables:dict):
        local_variables = {}
        for index,condition in enumerate(self.conditions):
            if self.calc_operation(condition,\
                                global_variables,\
                                local_variables):
                for operation in self.operations[index]:
                    if operation[0] == 'var':
                        result = self.calc_operation(operation[2],\
                                                global_variables,\
                                                local_variables)
                        global_variables[operation[1]] = result
                    elif operation[0] == 'var_change':
                        index = self.calc_operation(operation[1],\
                                            global_variables,\
                                            local_variables)
                        result = self.calc_operation(operation[2],\
                                                global_variables,\
                                                local_variables)
                        if isinstance(index,tuple):
                            data = self.get_variable(index[0],
                                                     global_variables,
                                                     local_variables)
                            for layer in index[1:-1]:
                                new_index = index_check(layer)
                                try:
                                    data = data[new_index]
                                except:
                                    raise Exceptions.ReferenceError(new_index)

                            new_index = index_check(index[-1])
                            try:
                                data[new_index] = result 
                            except:
                                raise Exceptions.ReferenceError(new_index)
                        else:
                            self.change_variable(index,
                                                 result,
                                                 global_variables,
                                                 local_variables)

                    elif operation[0] == 'let':
                        result = self.calc_operation(operation[2],\
                                            global_variables,\
                                            local_variables)
                        local_variables[operation[1]] = result
                    elif operation[0] == 'function':
                        global_variables[operation[1]] = Types.Function(operation[2],operation[3],True)
                    elif operation[0] == 'if':
                        global_copy = global_variables.copy()
                        global_copy.update(local_variables)
                        result = operation[1].execute(global_copy)
                        if isinstance(result,tuple):
                            return result
                        
                    elif operation[0] == 'loop':
                        global_copy = global_variables.copy()
                        global_copy.update(local_variables)
                        result = operation[1].execute(global_copy)
                        if isinstance(result,tuple):
                            return result

                    elif operation[0] == 'try':                    
                        global_copy = global_variables.copy()
                        global_copy.update(local_variables)
                        result = operation[1].execute(global_copy)
                        if isinstance(result,tuple):
                            return result
                    
                    elif operation[0] == 'return':
                        result = self.calc_operation(operation[1],\
                                                global_variables,\
                                                local_variables)
                        return result,global_variables,'return'
                    elif operation[0] == 'continue':
                        return None,global_variables,'continue'
                    elif operation[0] == 'break':
                        return None,global_variables,'break'
                break
        return global_variables



