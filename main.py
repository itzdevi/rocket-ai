import app
import ai_agent
import keyboard_agent

import constants
import math

a = app.App(keyboard_agent.KeyboardAgent())
# a = app.App(ai_agent.AIAgent("./model/model.pt"))

while a.is_running():
    print(a.env.get_state().distance_from_touchdown[1])
    a.tick()
    a.draw()
    