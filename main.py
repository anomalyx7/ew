from flask import Flask, session, render_template, redirect, url_for
from flask_socketio import SocketIO, join_room
from auth import auth
from admin import admin
from messenger import messenger
from instantMessenger import instantMessenger
from fts import fts
from instantMessenger import instantMessenger
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)

app.register_blueprint(auth)
app.register_blueprint(messenger)
app.register_blueprint(admin)
app.register_blueprint(fts)
app.register_blueprint(instantMessenger)


@app.route('/')
def index():
    if session.get('user_id'):
        return render_template("index.html")
    else:
        return redirect(url_for("auth.login"))


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_notice', data, room=data['room'])


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room: {}".format(data['username'], data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])


if __name__ == '__main__':
    app.secret_key = "2862"
    socketio.run(app, debug=True)

# TODO: Criação de grupos
# TODO: Enviar mensagem persistente a grupo
