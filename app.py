from flask import Flask, render_template, request, redirect, url_for
from groq import Groq
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- HOME ----------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------- LOGIN (DEMO MODE) ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username and password:
            return redirect(url_for("style_ai"))
        else:
            error = "Please enter username and password"
    return render_template("login.html", error=error)

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("signup.html")

# ---------- FORGOT ----------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    message = ""
    if request.method == "POST":
        message = "Password reset link sent (demo)."
    return render_template("forgot.html", message=message)

# ---------- STYLE AI ----------
@app.route("/style", methods=["GET", "POST"])
def style_ai():
    result = ""
    image_path = None

    if request.method == "POST":
        gender = request.form.get("gender", "").strip()
        occasion = request.form.get("occasion", "").strip()
        style = request.form.get("style", "").strip()
        season = request.form.get("season", "").strip()

        if not gender or not occasion or not style or not season:
            result = "Please fill all fields."
            return render_template("index.html", result=result)

        # Image upload (demo AI logic)
        image = request.files.get("image")
        skin_tone = "Medium"
        body_type = "Average"
        size = "M"

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

        prompt = (
            "You are an AI fashion stylist.\n"
            f"Gender: {gender}\n"
            f"Occasion: {occasion}\n"
            f"Style: {style}\n"
            f"Season: {season}\n"
            f"Skin tone: {skin_tone}\n"
            f"Body type: {body_type}\n\n"
            "Suggest an outfit under ₹3000.\n"
            "Include:\n"
            "- Suitable colors\n"
            "- Clothing items\n"
            "- Recommended size\n"
            "- Footwear\n"
            "- Accessories\n"
            "- Estimated budget\n\n"
            "Mention platforms: Amazon, Myntra, Flipkart, Zara.\n"
            "Use short bullet points."
        )

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content.replace("\n", "<br>")
        except Exception as e:
            result = f"AI Error: {e}"

    return render_template("index.html", result=result, image=image_path)

if __name__ == "__main__":
    app.run(debug=True)
