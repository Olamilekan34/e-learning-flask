from app import create_app

# app, socketio = create_app()
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    # app.socketio.run(app, debug=True)
