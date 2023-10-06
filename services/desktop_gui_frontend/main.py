from app.gui import gui
from app.gui import windows
from app.gui.commands.history import CommandsHistory
from app.service import BackendServiceFactory
from app.diagrams.diagrams import DiagramsFactory
from app.config import get_settings

backend_url = get_settings().backend_location

service_factory = BackendServiceFactory(backend_url)
diagrams_factory = DiagramsFactory()
windows_factory = windows.WindowsFactory(service_factory, diagrams_factory)
commands_history = CommandsHistory()

app_gui = gui.GUI(windows_factory, commands_history)
app_gui.start()
