import app
import ai_agent
import keyboard_agent

import constants

# a = app.App(keyboard_agent.KeyboardAgent())
a = app.App(ai_agent.AIAgent("./model/model.pt"))

while a.is_running():
    print(0.3 - a.env.get_state().velocity[1])
    a.tick()
    a.draw()
    