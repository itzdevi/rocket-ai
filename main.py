import app
import ai_agent

a = app.App(ai_agent.AIAgent("./model/model.pt"))

while a.is_running():
    a.tick()
    a.draw()
    