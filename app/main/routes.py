import re
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import emit, join_room
from app import mysql, socketio 
from app.utils import allowed_file

main = Blueprint('main', __name__)


@main.app_template_filter('linkify')
def linkify_mentions(text):
    if not text: return ""
    return re.sub(r'@(\w+)', r'<a href="/\1" class="text-accent text-decoration-none fw-bold">@\1</a>', text)

def add_notification(user_id, message, type='like', target_id=0):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO notifications (user_id, message, type, target_id) VALUES (%s, %s, %s, %s)", 
                (user_id, message, type, target_id))
    mysql.connection.commit()
    cur.close()

def process_mentions(text, post_id, type='post'):
    usernames = re.findall(r'@(\w+)', text)
    unique_usernames = set(usernames)
    
    cur = mysql.connection.cursor()
    for username in unique_usernames:
        cur.execute("SELECT id FROM users WHERE username = %s", [username])
        user = cur.fetchone()
        
        if user and user[0] != session['id']:
            target_id = user[0]
            msg = f"{session['username']} me-mention Anda dalam sebuah {type}."
            cur.execute("SELECT 1 FROM notifications WHERE user_id=%s AND type='mention' AND target_id=%s", 
                        (target_id, post_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO notifications (user_id, message, type, target_id) VALUES (%s, %s, %s, %s)", 
                            (target_id, msg, 'mention', post_id))
    mysql.connection.commit()
    cur.close()

def get_posts_with_files(cursor, mode='all', specific_user_id=None):
    query = """
        SELECT p.id, p.caption, p.user_id, p.created_at, 
               u.username, u.full_name, u.profile_pic,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = %s) as is_liked
        FROM posts p 
        JOIN users u ON p.user_id = u.id
    """
    params = [session['id']] 

    if mode == 'following':
        query += """
            WHERE p.user_id = %s 
            OR p.user_id IN (SELECT followed_id FROM follows WHERE follower_id = %s)
        """
        params.append(session['id']) 
        params.append(session['id']) 
        
    elif mode == 'user' and specific_user_id:
        query += " WHERE p.user_id = %s"
        params.append(specific_user_id)
        
    elif mode == 'search':
        query += " WHERE p.caption LIKE %s"
        params.append(f"%{specific_user_id}%") 

    query += " ORDER BY p.created_at DESC"
    
    cursor.execute(query, params)
    raw_posts = cursor.fetchall()
    
    final_posts = []
    
    for post in raw_posts:
        p_list = list(post) 
        post_id = p_list[0]
        
        cursor.execute("SELECT file_path, file_type FROM post_files WHERE post_id = %s", [post_id])
        files = cursor.fetchall()
        p_list.append(files) 
        
        cursor.execute("""
            SELECT c.content, u.username, u.profile_pic, u.full_name, c.created_at, c.id, c.user_id
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.post_id = %s 
            ORDER BY c.created_at ASC
        """, [post_id])
        comments = cursor.fetchall()
        p_list.append(comments)

        final_posts.append(p_list)
        
    return final_posts

# ================= ROUTES UTAMA =================

@main.route('/', methods=['GET', 'POST'])
def index():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        if 'caption' in request.form:
            caption = request.form['caption']
            files = request.files.getlist('files[]')
            
            cur.execute("INSERT INTO posts (user_id, caption) VALUES (%s, %s)", (session['id'], caption))
            post_id = cur.lastrowid
            
            process_mentions(caption, post_id, type='posting')

            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(f"{session['id']}_{post_id}_{file.filename}")
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    ext = filename.rsplit('.', 1)[1].lower()
                    f_type = 'video' if ext in ['mp4', 'mkv', 'avi'] else 'foto'
                    cur.execute("INSERT INTO post_files (post_id, file_path, file_type) VALUES (%s, %s, %s)", (post_id, filename, f_type))
            mysql.connection.commit()
            return redirect(url_for('main.index'))

    posts = get_posts_with_files(cur, mode='following')
    
    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()
    cur.close()
    
    return render_template('main/index.html', posts=posts, current_user=current_user)

@main.route('/explore')
def explore():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    
    query = request.args.get('q')
    if query:
        return redirect(url_for('main.search_results', query=query))
    
    cur = mysql.connection.cursor()
    posts = get_posts_with_files(cur, mode='all')
    
    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()
    cur.close()
    
    return render_template('main/explore.html', posts=posts, current_user=current_user, query=None)

@main.route('/search/<query>')
def search_results(query):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    search_term = '%' + query + '%'
    
    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE username LIKE %s OR full_name LIKE %s", 
                (search_term, search_term))
    users = cur.fetchall()
    
    posts = get_posts_with_files(cur, mode='search', specific_user_id=query)
    
    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()
    cur.close()
    
    return render_template('main/explore.html', posts=posts, users=users, query=query, current_user=current_user)

@main.route('/comment/<int:post_id>', methods=['GET', 'POST'])
def comment_post(post_id):
    if 'loggedin' not in session: 
        if request.method == 'POST': return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        return redirect(url_for('auth.login'))
        
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        content = request.form['content']
        cur.execute("INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)", (session['id'], post_id, content))
        
        process_mentions(content, post_id, type='komentar')
        
        cur.execute("SELECT user_id FROM posts WHERE id = %s", [post_id])
        owner_data = cur.fetchone()
        if owner_data and owner_data[0] != session['id']:
             add_notification(owner_data[0], f"{session['username']} mengomentari postingan Anda.", 'comment', post_id)
        
        mysql.connection.commit()
        
        cur.execute("SELECT username, full_name FROM users WHERE id = %s", [session['id']])
        user_info = cur.fetchone()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'user': user_info[0], 
            'full_name': user_info[1],
            'komentar_baru': content,
            'message': 'Komentar terkirim'
        })

    cur.execute("SELECT caption FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    
    cur.execute("""
        SELECT c.content, u.username, c.created_at, u.profile_pic, u.full_name, c.id, c.user_id
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.post_id = %s ORDER BY c.created_at ASC
    """, [post_id])
    comments = cur.fetchall()

    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()
    
    cur.close()

    return render_template('includes/comment.html', 
                           comments=comments, 
                           post_id=post_id, 
                           caption=post[0] if post else "",
                           current_user=current_user)

@main.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM comments WHERE id = %s", [comment_id])
    comment = cur.fetchone()
    
    if comment and comment[0] == session['id']:
        cur.execute("DELETE FROM comments WHERE id = %s", [comment_id])
        mysql.connection.commit()
    
    cur.close()
    return redirect(request.referrer or url_for('main.index'))

@main.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    if post and post[0] == session['id']:
        cur.execute("SELECT file_path FROM post_files WHERE post_id = %s", [post_id])
        files = cur.fetchall()
        for f in files:
            try: os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], f[0]))
            except: pass
        cur.execute("DELETE FROM posts WHERE id = %s", [post_id])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('main.index'))

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        bio = request.form['bio']
        full_name = request.form['full_name']
        username = request.form['username']
        
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"pfp_{session['id']}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                cur.execute("UPDATE users SET profile_pic = %s WHERE id = %s", (filename, session['id']))
        if 'cover_pic' in request.files:
            file = request.files['cover_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"cover_{session['id']}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                cur.execute("UPDATE users SET cover_pic = %s WHERE id = %s", (filename, session['id']))
        
        cur.execute("UPDATE users SET bio = %s, full_name = %s, username = %s WHERE id = %s", (bio, full_name, username, session['id']))
        mysql.connection.commit()
        session['username'] = username
        return redirect(url_for('main.profile', username=session['username']))
    
    cur.execute("SELECT bio, full_name, username FROM users WHERE id = %s", [session['id']])
    data = cur.fetchone()
    cur.close()
    return render_template('user/edit_profile.html', bio=data[0], full_name=data[1], username=data[2])

@main.route('/follow/<int:user_id>')
def follow_user(user_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    if user_id == session['id']: return redirect(url_for('main.index'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM follows WHERE follower_id = %s AND followed_id = %s", (session['id'], user_id))
    if cur.fetchone():
        cur.execute("DELETE FROM follows WHERE follower_id = %s AND followed_id = %s", (session['id'], user_id))
    else:
        cur.execute("INSERT INTO follows (follower_id, followed_id) VALUES (%s, %s)", (session['id'], user_id))
        add_notification(user_id, f"{session['username']} mulai mengikuti Anda.", 'follow', session['id'])
    mysql.connection.commit()
    return redirect(request.referrer or url_for('main.index'))

@main.route('/like/<int:post_id>', methods=['POST']) 
def like_post(post_id):
    if 'loggedin' not in session: return jsonify({'status': 'error'}), 401
    cur = mysql.connection.cursor()
    user_id = session['id']
    cur.execute("SELECT * FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    existing = cur.fetchone()
    action = ''
    if existing:
        cur.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
        action = 'unliked'
    else:
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        action = 'liked'
        cur.execute("SELECT user_id FROM posts WHERE id = %s", [post_id])
        post_owner = cur.fetchone()
        if post_owner and post_owner[0] != user_id:
            add_notification(post_owner[0], f"{session['username']} menyukai postingan Anda.", 'like', post_id)
    mysql.connection.commit()
    cur.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", [post_id])
    new_count = cur.fetchone()[0]
    cur.close()
    return jsonify({'status': 'success', 'action': action, 'likes': new_count})


@main.route('/chat')
def chat_list():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    my_id = session['id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT u.id, u.username, u.profile_pic, u.full_name 
        FROM users u
        JOIN follows f1 ON u.id = f1.follower_id
        JOIN follows f2 ON u.id = f2.followed_id
        WHERE f1.followed_id = %s AND f2.follower_id = %s
    """, (my_id, my_id))
    mutuals = cur.fetchall()

    cur.execute("""
        SELECT DISTINCT u.id, u.username, u.profile_pic, u.full_name
        FROM users u
        JOIN messages m ON (u.id = m.sender_id OR u.id = m.receiver_id)
        WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.id != %s
    """, (my_id, my_id, my_id))
    history_users = cur.fetchall()

    chat_users = {}
    
    def add_to_dict(user_row):
        u_id = user_row[0]
        if u_id not in chat_users:
            chat_users[u_id] = {
                'id': u_id,
                'username': user_row[1],
                'profile_pic': user_row[2],
                'full_name': user_row[3],
                'last_msg': 'Mulai obrolan baru',
                'last_time': None,
                'unread': 0
            }

    for u in mutuals: add_to_dict(u)
    for u in history_users: add_to_dict(u)

    final_list = []
    for uid, user_data in chat_users.items():
        cur.execute("""
            SELECT message, created_at FROM messages 
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY created_at DESC LIMIT 1
        """, (my_id, uid, uid, my_id))
        last_msg_data = cur.fetchone()
        
        if last_msg_data:
            user_data['last_msg'] = last_msg_data[0] if len(last_msg_data[0]) < 30 else last_msg_data[0][:30] + '...'
            user_data['last_time'] = last_msg_data[1]
        
        cur.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
        """, (uid, my_id))
        unread_count = cur.fetchone()
        user_data['unread'] = unread_count[0] if unread_count else 0
        
        final_list.append(user_data)

    cur.close()

    final_list.sort(key=lambda x: x['last_time'] if x['last_time'] else datetime.min, reverse=True)

    return render_template('chat/chat_list.html', users=final_list)

@main.route('/chat/<int:friend_id>')
def chat_room(friend_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    
    cur.execute("UPDATE messages SET is_read = 1 WHERE sender_id = %s AND receiver_id = %s", (friend_id, session['id']))
    mysql.connection.commit()

    cur.execute("SELECT username, profile_pic, full_name FROM users WHERE id = %s", [friend_id])
    friend = cur.fetchone()
    
    cur.execute("""
        SELECT * FROM messages 
        WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s) 
        ORDER BY created_at ASC
    """, (session['id'], friend_id, friend_id, session['id']))
    messages = cur.fetchall()
    cur.close()
    
    room = f"room_{min(session['id'], friend_id)}_{max(session['id'], friend_id)}"
    return render_template('chat/chat_room.html', messages=messages, friend=friend, friend_id=friend_id, room=room)

@socketio.on('join')
def on_join(data): join_room(data['room'])

@socketio.on('send_message')
def handle_message(data):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (sender_id, receiver_id, message, is_read) VALUES (%s, %s, %s, 0)", (session['id'], data['receiver_id'], data['message']))
    mysql.connection.commit()
    cur.close()
    emit('receive_message', {'message': data['message'], 'sender': session['username']}, room=data['room'])

@main.route('/notifications')
def notifications():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.message, n.created_at, n.is_read, n.type, n.target_id, u.username
        FROM notifications n LEFT JOIN users u ON (n.type='follow' AND n.target_id=u.id)
        WHERE n.user_id=%s ORDER BY n.created_at DESC
    """, [session['id']])
    notifs = cur.fetchall()
    cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s", [session['id']])
    mysql.connection.commit()
    cur.close()
    return render_template('main/notifications.html', notifications=notifs)

@main.route('/<username>')
def profile(username):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, bio, profile_pic, cover_pic, joined_at, full_name FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    if not user: return "User not found", 404
    
    user_id = user[0]
    cur.execute("SELECT COUNT(*) FROM follows WHERE followed_id = %s", [user_id])
    followers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM follows WHERE follower_id = %s", [user_id])
    following = cur.fetchone()[0]

    is_following = False
    if session['id'] != user_id:
        cur.execute("SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = %s", (session['id'], user_id))
        if cur.fetchone(): is_following = True

    posts = get_posts_with_files(cur, mode='user', specific_user_id=user_id)
    
    cur.execute("SELECT id, username, profile_pic, full_name FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()

    cur.close()
    return render_template('user/profile.html', user=user, posts=posts, followers=followers, following=following, is_following=is_following, current_user=current_user)