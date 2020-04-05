from flask import Flask, session, render_template, request, redirect, url_for
import pymysql
from hashlib import md5


app = Flask(__name__)

#initialize the connection to the server and database
db = pymysql.connect("localhost", "root", "", "nno511")
cursor = db.cursor() #cursor object to perform operations in the database

app = Flask(__name__)

logged_in = None

@app.route('/signin', methods=['GET', 'POST'])
def signIn():
    '''
    Sign in page for logging in to create, read, update and delete records.
    Defaults - username:admin, password :admin
    '''
    global logged_in
    status = None
    
    if request.method == 'POST':
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        for row in results:
            print(row[1])
            if request.form['username'] != row[1] or md5(request.form['password'].encode()).hexdigest() != row[2]: #with hashing the password
                status = 'Invalid Credentials. Please try again.'
                logged_in = False
            else: #case log in successful
                logged_in = True
                return redirect('posts')
    return render_template('index.html', status=status)


@app.route('/posts', methods=['GET', 'POST'])
def addPost():
    '''
    Carry out CRUD operations on the database, create blog post.
    Using pymysql to interact with the database created.
    '''
    if logged_in != None:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            content = request.form['content']

            try:
                sql = "INSERT INTO blogposts (blog_title, author, blog_content) VALUES(%s, %s, %s)"
                cursor.execute(sql, (title, author, content))
                db.commit()
            except Exception as e:
                print(e)
            
            return redirect('/home')

        return render_template('posts.html', logged_in=True)


@app.route('/home')
@app.route('/')
def showPosts():
    '''
    The website that will show the blogposts for reading.
    Displays the titile, blogpost, authors and date posted.
    '''
    author = session.get('author')
    show = False
    if logged_in:
        show = True
    sql = "SELECT * FROM blogposts ORDER BY blog_date DESC" #show posts from the lastest one
    cursor.execute(sql)
    results = cursor.fetchall()
    
    return render_template('home.html', posts=results, author=author, show_hidden=show)


@app.route('/posts/delete/<int:id>')
def deletePost(id):
    '''
    Choose the post id from the database and delete it.
    '''
    if logged_in != None:
        cursor.execute("DELETE FROM blogposts WHERE blog_id=%s", id)
        db.commit()
        return redirect('/home')


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def editPost(id):
    '''
    Based on the selected post, get its id from the database.
    Repopulate the add post form and edit it
    '''
    if logged_in != None:
        cursor.execute("SELECT * FROM blogposts WHERE blog_id = %s", id) #returns a tupule
        post = cursor.fetchall()[0]
        print(post)
        post = list(post)
        if request.method == 'POST':       
            post[1] = request.form['title']
            post[2] = request.form['content']
            sql = "UPDATE blogposts SET blog_title = %s, blog_content = %s WHERE blog_id = %s"
            cursor.execute(sql, (post[1], post[2], post[0]))
            db.commit()
            return redirect('/home')
        else:
            return render_template('edit.html', post=post)


@app.route('/logout')
def logOut():
    global logged_in
    if logged_in != None:
        logged_in = None
        return redirect('/home')
    else:
        return redirect('/home')
if __name__ == '__main__':
    app.run(debug=True)