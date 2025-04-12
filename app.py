from flask import Flask, render_template, request, redirect, url_for
import uuid, json, os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onboarding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ---------- Email Helper Function ----------
def send_email(recipient, subject, body):
    sender_email = "pbhuvanashankar@gmail.com"  # ✅ Your email
    sender_password = "bwqq sely vlmw mnnz"      # ✅ Your Gmail App Password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ---------- JSON Helpers ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ---------- Routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        joining_date = request.form['joining_date']
        token = str(uuid.uuid4())

        data = load_data()
        data[token] = {
            "token": token,
            "email": email,
            "joining_date": joining_date,
            "employee_info": {},
            "hr_info": {},
            "status": "invited"
        }

        save_data(data)

        employee_link = url_for('employee_form', token=token, _external=True)
        hr_link = url_for('hr_form', token=token, _external=True)

        # ✅ Send the employee link directly to their email
        send_email(
            recipient=email,
            subject="📋 Complete Your Onboarding Form",
            body=(
                f"Hi there,\n\n"
                f"Welcome aboard! Please complete your onboarding form using the link below:\n\n"
                f"{employee_link}\n\n"
                f"If you have questions, reach out to your HR team.\n\n"
                f"Best,\nHR Team"
            )
        )

        return render_template('success.html', employee_link=employee_link, hr_link=hr_link)

    return render_template('index.html')

@app.route('/employee/<token>', methods=['GET', 'POST'])
def employee_form(token):
    data = load_data()
    if token not in data:
        return "Invalid or expired link."

    if request.method == 'POST':
        data[token]["employee_info"] = {
            "full_name": request.form["full_name"],
            "dob": request.form["dob"],
            "email": request.form["email"],
            "phone": request.form["phone"],
            "address": request.form["address"],
            "bank_details": request.form["bank_details"],
            "tax_id": request.form["tax_id"],
            "emergency_contact": request.form["emergency_contact"]
        }

        save_data(data)
        return "✅ Thank you! Your information has been submitted."

    return render_template("employee_form.html", token=token)

@app.route('/hr/<token>', methods=['GET', 'POST'])
def hr_form(token):
    data = load_data()
    if token not in data:
        return "Invalid or expired link."

    if request.method == 'POST':
        data[token]["hr_info"] = {
            "employee_id": request.form["employee_id"],
            "job_title": request.form["job_title"],
            "department": request.form["department"],
            "manager_name": request.form["manager_name"],
            "location": request.form["location"]
        }

        data[token]["status"] = "completed"
        save_data(data)

        return "✅ HR info saved successfully."

    return render_template("hr_form.html", token=token)

if __name__ == "__main__":
    app.run(debug=True)
