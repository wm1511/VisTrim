import calc
import ui

sound = calc.SoundWave(ui.file_browse())
interface = ui.UserInterface(sound, 0.05)
#graph = ui.Graph(sound, interface.root)
#graph.draw_fresh()
