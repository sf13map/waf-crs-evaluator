from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/endpoint", methods=["GET", "POST"])
def post_html():
    if request.method == "POST":
        return jsonify(msg="POST OK", data=request.get_data(as_text=True))
    return "<h1>Hello (GET)</h1>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

