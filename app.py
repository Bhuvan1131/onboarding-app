from flask import Flask, render_template, request, url_for
import uuid
import smtplib
import os
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import db, OnboardingEntry

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onboarding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ✅ Ensure DB is created (works on Render too)
with app.app_context():
    db.create_all()

# ---------- Email Helper ----------
def send_email(recipient, subject, body):
    sender_email = "pbhuvanashankar@gmail.com"
    sender_password = "bwqq sely vlmw mnnz"

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

# ---------- CSV Helper ----------
def save_to_csv(entry):
    filename = "submissions.csv"

    # Merge keys from both info blocks to get complete header
    fieldnames = ['token', 'email', 'joining_date']
    if entry.employee_info:
        fieldnames += list(entry.employee_info.keys())
    if entry.hr_info:
        fieldnames += list(entry.hr_info.keys())

    # Merge all info into a single row
    row = {
        'token': entry.token,
        'email': entry.email,
        'joining_date': entry.joining_date,
        **(entry.employee_info or {}),
        **(entry.hr_info or {})
    }

    write_headers = not os.path.exists(filename)

    # Load existing rows, replace this token if it exists
    existing_rows = []
    if not write_headers:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_rows = [r for r in reader if r['token'] != entry.token]

    existing_rows.append(row)

    # Write back to file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)

    print(f"✅ Saved/updated token {entry.token} to {filename}")

# ---------- Routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        joining_date = request.form['joining_date']
        token = str(uuid.uuid4())

        entry = OnboardingEntry(
            token=token,
            email=email,
            joining_date=joining_date,
            employee_info={},
            hr_info={},
            status="invited"
        )
        db.session.add(entry)
        db.session.commit()

        employee_link = url_for('employee_form', token=token, _external=True)
        hr_link = url_for('hr_form', token=token, _external=True)

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
    entry = OnboardingEntry.query.filter_by(token=token).first()
    if not entry:
        return "Invalid or expired link."

    if request.method == 'POST':
        entry.employee_info = request.form.to_dict()
        db.session.commit()
        save_to_csv(entry)  # ✅ Save after employee fills
        return "✅ Thank you! Your information has been submitted."

    return render_template("employee_form.html", token=token)

@app.route('/hr/<token>', methods=['GET', 'POST'])
def hr_form(token):
    entry = OnboardingEntry.query.filter_by(token=token).first()
    if not entry:
        return "Invalid or expired link."

    if request.method == 'POST':
        entry.hr_info = request.form.to_dict()
        entry.status = "completed"
        db.session.commit()
        save_to_csv(entry)  # ✅ Save after HR fills
        return "✅ HR info saved successfully."

    return render_template("hr_form.html", token=token)

if __name__ == "__main__":
    app.run(debug=True)
