import graphviz
import re
import gdb
import dearpygui.dearpygui as dpg


class ExitBreakpoint(gdb.Breakpoint):
    def __init__(self, do_on_exit):
        super().__init__("exit")
        self.do_on_exit = do_on_exit

    def stop(self):
        self.do_on_exit()
        return False


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
        self.name = "array-c-bridge-test"
        self.function_names = set()
        self.stacks_and_locals = []
        ExitBreakpoint(self.on_exit)

    def stop(self):
        frame = gdb.selected_frame()

        frame_locals = []
        for symbol in frame.block():
            frame_locals.append(
                {
                    "name": str(symbol.name),
                    "value": symbol.value(frame).format_string(),
                }
            )

        stack = []
        while frame:
            tidied_function_name = tidy(frame.function().name)
            stack.append(tidied_function_name)
            self.function_names.add(tidied_function_name)

            frame = frame.older()

        self.stacks_and_locals.append((stack, frame_locals))

        return False

    def create_and_view_graph(self, selected_stack_index):
        self.dot = graphviz.Digraph(self.name)
        self.function_names_list = list(self.function_names)

        for index, function_name in enumerate(self.function_names_list):
            self.dot.node(str(index), str(function_name))

        self.edges = set()
        for stack_index, (stack, locals) in enumerate(self.stacks_and_locals):
            for i in range(len(stack) - 1):
                from_node = self.function_names_list.index(stack[i + 1])
                to_node = self.function_names_list.index(stack[i])
                self.edges.add(
                    (
                        str(from_node),
                        str(to_node),
                        "red" if stack_index is selected_stack_index else "black",
                    )
                )

        for from_node, to_node, color in self.edges:
            self.dot.edge(str(from_node), str(to_node), color=color)

        self.dot.format = "svg"
        self.dot.view()

    def create_and_show_stack_table(self):
        dpg.create_context()

        def on_row_select(sender, app_data, user_data):
            row_selected_index = user_data
            self.create_and_view_graph(row_selected_index)

        with dpg.window(tag="Selectable Tables"):
            with dpg.table(
                tag="SelectRows",
                header_row=True,
                resizable=True,
                policy=dpg.mvTable_SizingStretchProp,
                borders_outerH=True,
                borders_innerV=True,
                borders_outerV=True,
            ):
                dpg.add_table_column(label="Stack Index")

                # assume all locals have the same schema
                # add the columns
                first_locals = self.stacks_and_locals[0][1]
                for local in first_locals:
                    dpg.add_table_column(label=local["name"])

                dpg.add_table_column(label="test name")

                # add the data
                for index, (stack, locals) in enumerate(self.stacks_and_locals):
                    with dpg.table_row():
                        dpg.add_selectable(
                            label=f"{index}",
                            span_columns=True,
                            callback=on_row_select,
                            user_data=index,
                        )

                        for local in locals:
                            dpg.add_text(local["value"])

                        dpg.add_text(stack[-12])

        dpg.create_viewport(title="Locals", width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def on_exit(self):
        self.create_and_view_graph(None)
        self.create_and_show_stack_table()
