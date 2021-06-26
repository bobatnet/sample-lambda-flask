import os

from flask import Flask, render_template_string, url_for

app = Flask(__name__)

app.config['APPLICATION_ROOT'] = os.environ.get("APPLICATION_ROOT", "/")


@app.route(f"/home")
@app.route(f"/home/<authcode>")
def home(authcode=None):
    return render_template_string(f"""
        <html><body>
                <a href="{url_for("otherhome")}">Hello world!</a>
        </body></html>
    """)


@app.route(f"/otherhome")
def otherhome():
    return render_template_string("""
        <html><body>
                Hello Earth!
        </body></html>
    """)
