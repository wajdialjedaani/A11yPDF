import os

from portal import create_app

app = create_app()

if __name__ == "__main__":
    # port = int(os.environ.get('PORT',8000))
    app.run(host='0.0.0.0',debug=True)
