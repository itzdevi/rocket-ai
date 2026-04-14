import app
import ai_agent
import keyboard_agent

a = app.App(keyboard_agent.KeyboardAgent())
# a = app.App(ai_agent.AIAgent("./model/model.pt"))

while a.is_running():
    a.env.get_reward()
    a.tick()
    a.draw()
    