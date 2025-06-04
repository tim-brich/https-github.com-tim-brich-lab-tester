from flask import Flask, request, redirect, url_for, render_template_string
import os
import uuid
from queue_worker import enqueue, get_status, get_report

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

INDEX_HTML = """
<h2>Lab Autotester</h2>
<form method="post" action="/upload" enctype="multipart/form-data">
  <p><label>Student name: <input type="text" name="student"></label></p>
  <p><label>Lab ID: <input type="text" name="lab_id"></label></p>
  <p><label>Upload .cpp: <input type="file" name="file"></label></p>
  <button type="submit">Submit</button>
</form>
"""

STATUS_HTML = """
<h3>Job {{job_id}}</h3>
<p>Status: <b>{{status}}</b></p>
{% if status == 'READY' %}
<pre>{{report}}</pre>
{% else %}
<meta http-equiv="refresh" content="3">
<p>Waiting... auto-refreshing.</p>
{% endif %}
<a href="/">Submit another</a>
"""

@app.route("/")
def index():
    return INDEX_HTML

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    lab_id = request.form["lab_id"].strip()

    if not file.filename.endswith(".cpp"):
        return "[ERROR] Only .cpp files are allowed", 400
    if not lab_id:
        return "[ERROR] Lab ID is required", 400

    uid = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_FOLDER, uid + ".cpp")
    file.save(save_path)

    job_id = enqueue(save_path, lab_id)
    return redirect(url_for("job_status", job_id=job_id))

@app.route("/job/<job_id>")
def job_status(job_id):
    status = get_status(job_id)
    report = get_report(job_id) if status == "READY" else ""
    return render_template_string(STATUS_HTML, job_id=job_id,
                                  status=status, report=report)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
