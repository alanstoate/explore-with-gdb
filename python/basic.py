import gdb


class BasicBreakpoint(gdb.Breakpoint):
    def stop(self):
        return True
