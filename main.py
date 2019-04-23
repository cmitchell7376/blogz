from flask import Flask, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:chuck@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(200))

    def __init__(self,title,text):
        self.title = title
        self.text = text


@app.route('/blog', methods=['POST' , 'GET'])
def blog():
    error_title = ''
    error_text = ''
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_text = request.form['blog_text']

        if blog_title == '':
            error_title = " no title"
            return render_template("newpost.html", error_title = error_title , blog_text = blog_text)

        if blog_text == '':
            error_text = " no text"
            return render_template("newpost.html", error_text = error_text , blog_title = blog_title)
        else:

            blog_entry = Blog(blog_title,blog_text)
            db.session.add(blog_entry)
            db.session.commit()
            list_tmp = Blog.query.all()
            id = str(len(list_tmp)) 
            return redirect('/newpage?id={0}'.format(id))

    blog_entry = Blog.query.all()
    return render_template("blog.html", blog_entry = blog_entry) 

@app.route('/newpage')
def newpage():
    id = int(request.args.get('id'))
    blog_id = Blog.query.filter_by(id = id).all()
    return render_template('page.html', titles = blog_id)

@app.route('/newpost')
def entry():
    return render_template("newpost.html")


if __name__ == '__main__':
    app.run()