import app

a = app.App()

while a.is_running():
    a.tick()
    a.draw()
    