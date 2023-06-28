from gui import gui, windows


app_gui = gui.GUI(windows_factory=windows.HierarchicalWindow)
app_gui.start()
