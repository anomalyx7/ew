from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import os
from datetime import datetime

messenger = Blueprint('messenger', 'messenger')


# Useful methods


def get_messages_from_user(sender, receiver):
    file = open(f'Messenger_records/{sender}/{receiver}.txt', 'r')
    _ = file.readline()
    messages = []
    for m in file:
        x = m.split(' ', 1)
        mode = x[0]
        split = x[1]
        y = split.split('-', 1)
        messages.append((mode, y[1]))
    return messages


def get_user_conversations(user):
    _ = os.listdir(f'Messenger_records/{user}')
    people = [x[:-4] for x in _]
    return people


def session_user_add(username):
    _ = session['people']
    people = []
    for p in _:
        people.append(p)
    people.append(username)
    session['people'] = people


def get_last_visit(username):
    me = session.get('user_id')
    if username[0] != 'G':
        file = open(f'Messenger_records/{me}/{username}', 'r')
        _ = file.readline()
        x = _.split(':', 1)
        file.close()
        return x[1]


def update_last_read_time(username, time):
    me = session.get('user_id')
    file = open(f'Messenger_records/{me}/{username}.txt', 'r')
    first_line, remainder = file.readline(), file.read()
    file.close()
    file = open(f'Messenger_records/{me}/{username}.txt', 'w')
    file.write(f'LastRead:{time}\n{remainder}')
    file.close()


def check_for_new_messages():
    me = session.get('user_id')
    counter = 0
    new_messages = {}
    for filename in os.listdir(f'Messenger_records/{me}/'):
        if filename[0] != 'G':
            last_visit = get_last_visit(filename)
            file = open(f'Messenger_records/{me}/{filename}', 'r')
            _ = file.readline()
            for line in file:
                counter = 0
                x = line.split(' ', 1)
                if x[0] == 'Received':
                    remainder = x[1]
                    y = remainder.split('-', 1)
                    date = y[0]
                    if date > last_visit:
                        counter += 1
            if counter > 0:
                new_messages[f'{filename[:-4]}'] = counter
    return new_messages


def delete_message(index, folder, person):
    int_index = int(index, base=10)

    file = open(f'Messenger_records/{folder}/{person}.txt', 'r')
    output = [file.readline()]
    i = 0

    for line in file:

        if i != int_index:
            output.append(line)
        i += 1

    file.close()
    file = open(f'Messenger_records/{folder}/{person}.txt', 'w')
    file.writelines(output)
    file.close()


def send_group_message(to_send, message):
    username = session.get('user_id')

    file = open(f"Messenger_records/{username}/{to_send}.txt", "r")
    _ = file.readline()
    file.close()
    members = _.split(' ')
    members[-1] = members[-1][:-1]
    dt_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    file = open(f"Messenger_records/{username}/{to_send}.txt", "a")
    file.write(f"Sent {dt_now}-{message}\n")
    file.close()

    for m in members:
        file = open(f"Messenger_records/{m}/{to_send}.txt", 'a')
        file.write(f'Received {dt_now}-{username}:{message}\n')
        file.close()

    print(members)


# Ao aceder a este link, o programa vai recolher as conversas ativas do utilizador
# e redireciona para outro link
@messenger.route('/Messenger')
def load_messenger():
    user_id = session.get('user_id')
    people = get_user_conversations(user_id)
    session['people'] = people

    if people:
        return redirect(url_for('messenger.load_messenger_messages', current_conversation=people[0]))
    return redirect(url_for('messenger.load_messenger_messages', current_conversation="null"))


@messenger.route('/Messenger/c/<string:current_conversation>', methods=['GET'])
def load_messenger_messages(current_conversation):
    if current_conversation != "null":
        user_id = session['user_id']

        unread_messages = check_for_new_messages()
        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if current_conversation[0] != 'G':
            update_last_read_time(current_conversation, time)
        messages = get_messages_from_user(user_id, current_conversation)
        return render_template('MessengerForm.html', mensagens=messages, nMessages=len(messages), people=session['people'], currentPerson=current_conversation, unreadMessages=unread_messages)
    else:
        return render_template('MessengerForm.html')


@messenger.route('/messenger/searchPerson', methods=['POST'])
def messenger_search_person():
    username = request.form.get('usernameS')
    user_id = session.get('user_id')

    if username in session['people']:
        return jsonify(alreadyadded="User is already in your list!")
    else:
        if os.path.exists(f'Messenger_records/{username}'):
            file = open(f'Messenger_records/{user_id}/{username}.txt', 'w')
            file.write("LastRead: 00/00/0000 00:00:00\n")
            session_user_add(username)
            return redirect(url_for('messenger.load_messenger_messages', current_conversation=username))
        else:
            return jsonify(nonexistent="User does not exist!")


@messenger.route('/Messenger/send_message', methods=['PUT'])
def messenger_post():
    message = request.form['messageSend']
    sender = session.get('user_id')
    to_send = request.form['to_send']

    if to_send[0] != 'G':
        dt_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        file = open(f'Messenger_records/{sender}/{to_send}.txt', 'a')
        file.write(f'Sent {dt_now}-{message}\n')
        file.close()

        if not os.path.exists(f'Messenger_records/{to_send}/{sender}.txt'):
            _ = open(f'Messenger_records/{to_send}/{sender}.txt', "w")
            _.write("LastRead: 00/00/0000 00:00:00\n")
            _.close()

        file2 = open(f'Messenger_records/{to_send}/{sender}.txt', 'a')
        file2.write(f'Received {dt_now}-{message}\n')
        file2.close()
    else:
        send_group_message(to_send, message)
    return jsonify(message=message)


@messenger.route("/messenger/deletemsg", methods=['DELETE'])
def delete_msg():
    user_id = session.get('user_id')
    sent_to = request.form['sent_to']
    msg_index = request.form['msgNumber']

    delete_message(msg_index, user_id, sent_to)
    delete_message(msg_index, sent_to, user_id)

    nmessages = len(get_messages_from_user(user_id, sent_to))

    return jsonify(result="Message deleted successfully!", nmessages=nmessages)
