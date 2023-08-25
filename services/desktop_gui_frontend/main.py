from app.gui import gui, windows
from app.service import BackendServiceFactory
from app.gui.events_handlers import EventsHandler


app_gui = gui.GUI(
    windows_factory=windows.HierarchicalWindow,
    events_handler=EventsHandler(BackendServiceFactory())
)
app_gui.start()
