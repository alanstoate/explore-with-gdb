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
    def stop(self):
        frame = gdb.selected_frame()
        while frame:
            print(tidy(frame.function().name))

            frame = frame.older()

        return True
