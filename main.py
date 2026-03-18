import app
import keyboard_agent

a = app.App(keyboard_agent.KeyboardAgent())

while a.is_running():
    a.tick()
    a.draw()
    