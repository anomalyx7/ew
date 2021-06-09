from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session
from auth import check_if_user_exists, create_user, change_user_password, delete_user
import os

admin = Blueprint('admin', 'admin')


def create_group(name, members):
    for member in members:
        line = ""
        file = open(f"Messenger_records/{member}/G_{name}.txt", 'w')

        for w in members:
            if w != member:
                line += f"{w} "
        line += '\n'
        file.write(line)
        file.close()


@admin.route('/admin')
def load_admin():
    user_id = session.get('user_id')
    if user_id != 'root':
        return redirect(url_for('index'))
    return render_template('AdminPanel.html')


@admin.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    username = request.form['usernameC']
    password = request.form['passwordC']

    if check_if_user_exists(username):
        return jsonify({'error': 'Username already exists!'})

    create_user(username, password)

    return jsonify({'success': 'Username registered successfully!'})


@admin.route('/admin/change_password', methods=['PUT'])
def admin_change_password():
    username = request.form['usernameCP']
    password = request.form['passwordCP']

    if check_if_user_exists(username):
        change_user_password(username, password)
        return jsonify({'success': 'Password changed successfully!'})

    return jsonify({'error': 'Username does not exists'})


@admin.route('/admin/remove_user/', methods=['DELETE'])
def admin_remove_user():
    username = request.form['usernameD']

    if check_if_user_exists(username):
        delete_user(username)
        return jsonify({'success': 'User removed successfully!'})
    return jsonify({'error': 'User does not exists!'})


@admin.route('/admin/create_group/', methods=['POST'])
def admin_create_group():
    group_name = request.form['groupName']
    _ = request.form['groupMembers']
    group_members = _.split(' ')

    create_group(group_name, group_members)

    return jsonify(success="ola")


@admin.route('/admin/create_chat', methods=['POST'])
def admin_create_chat():
    chat_name = request.form['chatName']
    if os.path.exists(f"./Room_Users/Room-{chat_name}.txt"):
        return jsonify(error="This Chat Room already exists")
    else:
        file = open(f"Room_Users/Room-{chat_name}.txt", "w")
        file.close()
        return jsonify(success="Chat Room Created!")

# TODO: Definir grupos para utilizadores
# TODO: Definir canais
