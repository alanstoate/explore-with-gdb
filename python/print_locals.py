import gdb


class PrintLocalsBreakpoint(gdb.Breakpoint):
    def stop(self):
        frame = gdb.selected_frame()
        for symbol in frame.block():
            print(f"{str(symbol.name)}: {symbol.value(frame).format_string()}")
        return True
