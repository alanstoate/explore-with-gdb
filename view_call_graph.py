import graphviz
import re
import gdb


def tidy(function_name):
    function_name = str(function_name)
    function_name = function_name.replace("arrow::", "")
    function_name = function_name.replace("engine::", "")
    function_name = function_name.replace("std::", "")
    function_name = function_name.replace("(anonymous namespace)::", "")
    if function_name.startswith("CheckNotYetImplementedTestCase"):
        function_name = "CheckNotYetImplementedTestCase"
    function_name = "".join(re.split("\(|\)", function_name)[::2])
    return function_name


class StackTraceBreakpoint(gdb.Breakpoint):
    def __init__(self, breakpoint_location):
        super().__init__(breakpoint_location)
        self.name = "breakpoint_location"
        self.function_names = set()
        self.stacks = []

    def stop(self):
        frame = gdb.selected_frame()
        stack = []
        while frame:
            tidied_function_name = tidy(frame.function().name)
            stack.append(tidied_function_name)
            self.function_names.add(tidied_function_name)

            frame = frame.older()

        self.stacks.append(stack)

        return False

    def create_and_view_graph(self):
        self.dot = graphviz.Digraph(self.name)
        self.function_names_list = list(self.function_names)

        for index, function_name in enumerate(self.function_names_list):
            self.dot.node(str(index), str(function_name))

        self.edges = set()
        for stack in self.stacks:
            for i in range(len(stack) - 1):
                from_node = self.function_names_list.index(stack[i + 1])
                to_node = self.function_names_list.index(stack[i])
                self.edges.add((str(from_node), str(to_node)))

        for from_node, to_node in self.edges:
            self.dot.edge(str(from_node), str(to_node))

        self.dot.format = "svg"
        self.dot.view()
