import graphviz


dot = graphviz.Digraph("example")

dot.node("main")
dot.node("a")
dot.node("b")
dot.node("c")

dot.edge("main", "a")
dot.edge("main", "b")
dot.edge("main", "c")

dot.edge("a", "c")

dot.edge("b", "c")

dot.format = "svg"
dot.save()
