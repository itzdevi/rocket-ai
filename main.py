import app
import ai_agent

a = app.App(ai_agent.AIAgent())

while a.is_running():
    a.tick()
    a.draw()
    