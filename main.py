import app
import keyboard_agent
import controller_agent

a = app.App(controller_agent.ControllerAgent())

while a.is_running():
    a.tick()
    a.draw()
    