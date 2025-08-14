from flask import Flask, jsonify, render_template, request
import requests

API_URL_ICD10 = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/search")
def api_search():
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit") or 25)
    if not q:
        return jsonify({"items": []})

    try:
        params = {
            "sf": "code,name",
            "terms": q,
            "maxList": max(1, min(50, limit)),
        }
        r = requests.get(API_URL_ICD10, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        # data[3] => list of [code, name]
        items = [{
            "source": "ICD-10-CM",
            "code": code,
            "description": name
        } for code, name in data[3]]
        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"error": "fetch_failed", "detail": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)