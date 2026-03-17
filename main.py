import app

app = app.App()

while app.is_running():
    app.tick()
    app.draw()