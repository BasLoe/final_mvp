from mvp import app
from mvp import db
db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
