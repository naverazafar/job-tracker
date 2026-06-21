from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "jobs.json"

STATUSES = ["Saved", "Applied", "Phone Screen", "Interview", "Offer", "Rejected"]

def load_jobs():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_jobs(jobs):
    with open(DATA_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def get_next_id(jobs):
    return max((j["id"] for j in jobs), default=0) + 1

@app.route("/")
def index():
    jobs = load_jobs()
    status_filter = request.args.get("status", "")
    search = request.args.get("search", "").lower()

    filtered = jobs
    if status_filter:
        filtered = [j for j in filtered if j["status"] == status_filter]
    if search:
        filtered = [j for j in filtered if
                    search in j["company"].lower() or
                    search in j["role"].lower() or
                    search in j.get("notes", "").lower()]

    counts = {s: sum(1 for j in jobs if j["status"] == s) for s in STATUSES}
    counts["All"] = len(jobs)

    return render_template("index.html",
                           jobs=filtered,
                           statuses=STATUSES,
                           counts=counts,
                           active_status=status_filter,
                           search=search)

@app.route("/add", methods=["GET", "POST"])
def add_job():
    if request.method == "POST":
        jobs = load_jobs()
        job = {
            "id": get_next_id(jobs),
            "company": request.form["company"].strip(),
            "role": request.form["role"].strip(),
            "location": request.form.get("location", "").strip(),
            "salary": request.form.get("salary", "").strip(),
            "url": request.form.get("url", "").strip(),
            "status": request.form.get("status", "Saved"),
            "notes": request.form.get("notes", "").strip(),
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "date_updated": datetime.now().strftime("%Y-%m-%d"),
        }
        jobs.append(job)
        save_jobs(jobs)
        return redirect(url_for("index"))
    return render_template("form.html", job=None, statuses=STATUSES, action="Add")

@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    jobs = load_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        return redirect(url_for("index"))

    if request.method == "POST":
        job["company"] = request.form["company"].strip()
        job["role"] = request.form["role"].strip()
        job["location"] = request.form.get("location", "").strip()
        job["salary"] = request.form.get("salary", "").strip()
        job["url"] = request.form.get("url", "").strip()
        job["status"] = request.form.get("status", job["status"])
        job["notes"] = request.form.get("notes", "").strip()
        job["date_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_jobs(jobs)
        return redirect(url_for("index"))

    return render_template("form.html", job=job, statuses=STATUSES, action="Edit")

@app.route("/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    jobs = load_jobs()
    jobs = [j for j in jobs if j["id"] != job_id]
    save_jobs(jobs)
    return redirect(url_for("index"))

@app.route("/update_status/<int:job_id>", methods=["POST"])
def update_status(job_id):
    data = request.get_json()
    jobs = load_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)
    if job:
        job["status"] = data["status"]
        job["date_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_jobs(jobs)
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
