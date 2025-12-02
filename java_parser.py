import javalang
from javalang.tree import ClassDeclaration
import drawio
import typing


class JavaToDrawIOParser:
    def __init__(self):
        self.x, self.y = 0, 0
        self.tokens = {}
        self.token_order = tuple()
        self.block_statements = {}
        self.methods = {}
        self.endl_objs = []


    @staticmethod
    def get_dtype_attr(dtype) -> str:
        if dtype in ("Integer", "int", "Short", "short", "Long", "long", "byte"):
            return "∈N"
        elif dtype in ("Float", "float", "Double", "double"):
            return "∈R"
        else:
            return ""

    def subparse(self, node, drawio_obj = None, last_node = None):
        #print(type(node), node, "\n\n\n")
        #print(tokens)
        match type(node):
            case javalang.tree.ClassDeclaration:
                drawio_obj = drawio.DrawIO(node.name)
                if node.body is not None:
                    for i in range(len(node.body)):
                        subnode, subnode_children = self.subparse(node.body[i], drawio_obj, last_node)
                        if len(subnode_children) != 0:
                            for subnode_child in subnode_children:
                                self.endl_objs.append(subnode_child)

                #        else:
                #            drawio_obj.add_arrow(subnode, endl)

                self.y += 120
                endl = drawio_obj.add_procedure("Конец", self.x, self.y)
                for subnode in self.endl_objs:
                    drawio_obj.add_arrow(subnode, endl)

            case javalang.tree.MethodDeclaration:
                if node.name == "main" and node.modifiers == {'static', 'public'} and node.return_type is None:
                    method = drawio_obj.add_procedure("Начало", self.x, self.y)
                    self.methods[node.name] = method
                else:
                    if len(node.parameters) == 0:
                        method = drawio_obj.add_procedure(node.name, self.x, self.y)
                        self.methods[node.name] = method
                    else:
                        method = drawio_obj.add_procedure(f"{node.name} {(param.name for param in node.parameters)}", self.x, self.y)
                        self.methods[node.name] = method

                if node.body is not None:
                    last_node, last_children = method, []
                    for i in range(len(node.body)):
                        self.y += 120
                        subnode, subnode_children = self.subparse(node.body[i], drawio_obj, last_node)
                        #print(last_children, subnode_children)
                        if len(last_children) == 0:
                            if drawio_obj.add_arrow(last_node, subnode) != "":
                                last_node, last_children = subnode, subnode_children
                        else:

                            if any([drawio_obj.add_arrow(last_child, subnode) != "" for last_child in last_children]):
                                last_node, last_children = subnode, subnode_children
                    self.endl_objs.append(last_node)
                return method, []
            case javalang.tree.LocalVariableDeclaration:
                decls = self.get_expression_line(node.position)
                if decls.replace(" ", "") not in ["Scannerscanner=newScanner(System.in)"]:
                    if "scanner.next" in decls:  # todo: исправить / возвожны не от System.in:
                        return drawio_obj.add_io(f"Ввод {" ".join(self.get_variable_declarators_names(node.declarators))}{self.get_dtype_attr(node.type.name)}", self.x, self.y), []
                    elif any(method in self.get_variable_declarators_members(node.declarators) for method in self.methods):
                        return drawio_obj.add_call(f"{self.get_expression_line(node.position)}", self.x, self.y), []
                    else:
                        return drawio_obj.add_operation(f"{self.get_expression_line(node.position)}", self.x, self.y), []
                return "", []
            case javalang.tree.IfStatement:
                condition = drawio_obj.add_if(self.get_parentheses_line(self.get_expression_line(node.position, "{")), self.x, self.y)
                self.y += 120
                self.x -= 160
                else_st, else_st_children = self.subparse(node.else_statement, drawio_obj, condition)
                arrow = drawio_obj.add_arrow(condition, else_st)
                drawio_obj.add_arrow_txt(arrow, "Ложь")
                self.x += 160*2
                then_st, then_st_children = self.subparse(node.then_statement, drawio_obj, condition)
                arrow = drawio_obj.add_arrow(condition, then_st)
                drawio_obj.add_arrow_txt(arrow, "Истина")
                self.x -= 160
                return condition, [else_st, then_st]
            case javalang.tree.BlockStatement:
                if node.statements is not None:
                    statement = None
                    previous = None
                    for subnode in node.statements:
                        if statement is None:
                            statement, statement_children = self.subparse(subnode, drawio_obj, last_node)
                            previous = statement
                        else:
                            previous = drawio_obj.subparse(subnode, drawio_obj, previous)
                    if node.label is not None:
                        self.block_statements[node.label] = drawio_obj.block_list[-1]
                    return statement, [previous]
            case javalang.tree.StatementExpression:
                return self.subparse(node.expression, drawio_obj)
            case javalang.tree.MethodInvocation:
                decls = self.get_expression_line(node.position)
                if any(io_str in decls for io_str in ["System.out.printf",
                                                      "System.out.println",
                                                      "System.out.print"]):
                    return drawio_obj.add_io(f"Вывод {self.get_parentheses_line(decls)}", self.x, self.y), []
                elif node.member in self.methods:
                    return drawio_obj.add_call(decls), []
                else:
                    return drawio_obj.add_call(decls), []


               # print("\n", node)
                #print(self.get_expression_line(node.position), "\n")



        return drawio_obj

    def parse(self, source_code: str) -> typing.Iterable[drawio.DrawIO]:
        self.x, self.y = 0, 0
        java_tokens = javalang.tokenizer.tokenize(source_code)
        tokens = {}
        token_order_list = []
        for token in java_tokens:
            self.tokens[token.position] = token.value
            token_order_list.append(token.position)
        token_order_list = sorted(token_order_list)
        self.token_order = tuple(token_order_list)
        source_types = javalang.parse.parse(source_code).types
        return [self.subparse(node, tokens) for node in source_types]

    def get_token(self, position, offset = 0):
        return self.tokens[self.token_order[self.token_order.index(position) + offset]]

    def get_expression_line(self, position, bpoint: str = ";"):
        token = ""
        out = ""
        i = 0
        while token != bpoint:
            out += token
            if token not in """.,(")'=+-/*<>""":
                out += " "
            else:
                if len(out) > 0:
                    if out[-2] == " ":
                        out = out[:-2] + out[-1]
            token = self.get_token(position, i)
            i += 1
        return out

    def get_variable_declarators_names(self, declarators: list):
        return [declarator.name for declarator in declarators]

    def get_variable_declarators_members(self, declarators: list):
        members = []
        for declarator in declarators:
            if declarator.initializer is not None:
                if hasattr(declarator.initializer, "member"):
                    members.append(declarator.initializer.member)
        return members

    @staticmethod
    def get_parentheses_line(line: str):
        return line[line.find("(")+1:line.rfind(")")]

