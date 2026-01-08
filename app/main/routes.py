from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from flask_socketio import emit, join_room
from app import mysql, socketio 
from app.utils import allowed_file
import os

main = Blueprint('main', __name__)

def add_notification(user_id, message, type='like', target_id=0):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO notifications (user_id, message, type, target_id) VALUES (%s, %s, %s, %s)", 
                (user_id, message, type, target_id))
    mysql.connection.commit()
    cur.close()

def get_posts_with_files(cursor, specific_user_id=None):
    query = """
        SELECT p.id, p.caption, p.user_id, p.created_at, 
               u.username, u.profile_pic,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = %s) as is_liked
        FROM posts p 
        JOIN users u ON p.user_id = u.id
    """
    params = [session['id']]
    
    if specific_user_id:
        query += " WHERE p.user_id = %s"
        params.append(specific_user_id)
        
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
        
        final_posts.append(p_list)
        
    return final_posts

# ---------------------------------------------------

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
            
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{session['id']}_{post_id}_{file.filename}")
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    
                    ext = filename.rsplit('.', 1)[1].lower()
                    f_type = 'video' if ext in ['mp4', 'mkv', 'avi'] else 'foto'
                    
                    cur.execute("INSERT INTO post_files (post_id, file_path, file_type) VALUES (%s, %s, %s)", 
                                (post_id, filename, f_type))
            
            mysql.connection.commit()
            return redirect(url_for('main.index'))

    posts = get_posts_with_files(cur)

    cur.execute("SELECT id, username, profile_pic FROM users WHERE id = %s", [session['id']])
    current_user = cur.fetchone()

    cur.close()
    return render_template('main/index.html', posts=posts, current_user=current_user)

@main.route('/explore')
def explore():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    query = request.args.get('q', '')
    users = []
    posts = []
    
    cur = mysql.connection.cursor()
    if query:
        # Cari User
        cur.execute("SELECT id, username, profile_pic FROM users WHERE username LIKE %s", ('%' + query + '%',))
        users = cur.fetchall()
        
        # Cari Postingan (Perlu join post_files untuk ambil thumbnail gambar pertama)
        cur.execute("""
            SELECT p.id, p.caption, u.username, p.created_at, u.profile_pic,
            (SELECT file_path FROM post_files WHERE post_id = p.id LIMIT 1) as thumbnail
            FROM posts p JOIN users u ON p.user_id = u.id 
            WHERE p.caption LIKE %s ORDER BY p.created_at DESC
        """, ('%' + query + '%',))
        posts = cur.fetchall()
        
    cur.close()
    return render_template('main/explore.html', users=users, posts=posts, query=query)

@main.route('/profile/<username>')
def profile(username):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, username, email, bio, profile_pic, cover_pic, joined_at FROM users WHERE username = %s", [username])
    user = cur.fetchone()
    
    if not user:
        flash('User tidak ditemukan', 'danger')
        return redirect(url_for('main.index'))
    
    user_id = user[0]
    cur.execute("SELECT COUNT(*) FROM follows WHERE followed_id = %s", [user_id])
    followers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM follows WHERE follower_id = %s", [user_id])
    following = cur.fetchone()[0]

    is_following = False
    if session['id'] != user_id:
        cur.execute("SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = %s", (session['id'], user_id))
        if cur.fetchone(): is_following = True

    posts = get_posts_with_files(cur, specific_user_id=user_id)
    
    cur.close()
    return render_template('user/profile.html', user=user, posts=posts, followers=followers, following=following, is_following=is_following)

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        bio = request.form['bio']
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

        cur.execute("UPDATE users SET bio = %s WHERE id = %s", (bio, session['id']))
        mysql.connection.commit()
        return redirect(url_for('main.profile', username=session['username']))
    
    cur.execute("SELECT bio FROM users WHERE id = %s", [session['id']])
    data = cur.fetchone()
    cur.close()
    return render_template('/user/edit_profile.html', bio=data[0])

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
        # Notif Follow: target_id = session['id'] (agar link ke profil pengikut)
        add_notification(user_id, f"{session['username']} mulai mengikuti Anda.", 'follow', session['id'])
    
    mysql.connection.commit()
    cur.execute("SELECT username FROM users WHERE id = %s", [user_id])
    target = cur.fetchone()[0]
    cur.close()
    return redirect(url_for('main.profile', username=target))

@main.route('/like/<int:post_id>', methods=['POST']) 
def like_post(post_id):
    if 'loggedin' not in session:
        return jsonify({'status': 'error', 'message': 'Login dulu bang'}), 401

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
        
        # Notif Like
        cur.execute("SELECT user_id FROM posts WHERE id = %s", [post_id])
        post_owner = cur.fetchone()
        if post_owner and post_owner[0] != user_id:
            add_notification(post_owner[0], f"{session['username']} menyukai postingan Anda.", 'like', post_id)

    mysql.connection.commit()
    
    cur.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", [post_id])
    new_count = cur.fetchone()[0]
    cur.close()
    
    return jsonify({
        'status': 'success', 
        'action': action, 
        'likes': new_count
    })

@main.route('/comment/<int:post_id>', methods=['GET', 'POST'])
def comment_post(post_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        content = request.form['content']
        cur.execute("INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)", 
                    (session['id'], post_id, content))
        
        cur.execute("SELECT user_id FROM posts WHERE id = %s", [post_id])
        owner_data = cur.fetchone()
        if owner_data:
            owner = owner_data[0]
            if owner != session['id']:
                add_notification(owner, f"{session['username']} mengomentari postingan Anda.", 'comment', post_id)
        
        mysql.connection.commit()
        return redirect(url_for('main.comment_post', post_id=post_id)) 

    # Cek Postingan
    cur.execute("SELECT caption FROM posts WHERE id = %s", [post_id])
    post = cur.fetchone()
    
    if not post:
        flash('Postingan tidak ditemukan.', 'danger')
        return redirect(url_for('main.index'))

    cur.execute("""
        SELECT c.content, u.username, c.created_at, u.profile_pic 
        FROM comments c JOIN users u ON c.user_id = u.id 
        WHERE c.post_id = %s ORDER BY c.created_at ASC
    """, [post_id])
    comments = cur.fetchall()
    cur.close()
    return render_template('includes/comment.html', comments=comments, post_id=post_id, caption=post[0])

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

@main.route('/chat')
def chat_list():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, profile_pic FROM users WHERE id != %s", [session['id']])
    users = cur.fetchall()
    cur.close()
    return render_template('chat/chat_list.html', users=users)

@main.route('/chat/<int:friend_id>')
def chat_room(friend_id):
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, profile_pic FROM users WHERE id = %s", [friend_id])
    friend = cur.fetchone()
    
    cur.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = %s AND receiver_id = %s) 
        OR (sender_id = %s AND receiver_id = %s) 
        ORDER BY created_at ASC
    """, (session['id'], friend_id, friend_id, session['id']))
    messages = cur.fetchall()
    cur.close()
    room = f"room_{min(session['id'], friend_id)}_{max(session['id'], friend_id)}"
    return render_template('chat/chat_room.html', messages=messages, friend=friend, friend_id=friend_id, room=room)

@socketio.on('join')
def on_join(data):
    join_room(data['room'])

@socketio.on('send_message')
def handle_message(data):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)", 
                (session['id'], data['receiver_id'], data['message']))
    mysql.connection.commit()
    cur.close()
    emit('receive_message', {'message': data['message'], 'sender': session['username']}, room=data['room'])

@main.route('/notifications')
def notifications():
    if 'loggedin' not in session: return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT n.message, n.created_at, n.is_read, n.type, n.target_id, u.username
        FROM notifications n
        LEFT JOIN users u ON (n.type = 'follow' AND n.target_id = u.id)
        WHERE n.user_id = %s 
        ORDER BY n.created_at DESC
    """, [session['id']])
    notifs = cur.fetchall()

    cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s", [session['id']])
    mysql.connection.commit()

    cur.close()
    return render_template('main/notifications.html', notifications=notifs)