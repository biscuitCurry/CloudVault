# CloudVault

A personal cloud file storage web app built with Flask and Amazon S3. Users register, log in, and upload, download, and delete their own files, which are stored in an S3 bucket.

Built as a group project for an AWS cloud computing course at TVETMARA Sungai Petani.

## Features

- User registration and login, with passwords hashed using Werkzeug
- Upload any file type straight to Amazon S3
- Each user's files are kept under their own prefix in the bucket (`username/filename`)
- Downloads use pre-signed S3 URLs that expire after one hour, so the bucket stays private
- Delete files from the dashboard
- Responsive interface with file-type icons

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Storage | Amazon S3 (via boto3) |
| Auth | Flask sessions, Werkzeug password hashing |
| Frontend | HTML, CSS, Jinja2 templates, Tabler Icons |

## Project structure

```
CloudVault/
├── app.py              # Flask routes and S3 logic
├── requirements.txt    # Python dependencies
├── .env.example        # Template for the settings the app needs
├── static/
│   └── style.css
└── templates/
    ├── index.html      # File dashboard
    ├── login.html
    └── register.html
```

## Getting started

### 1. Prerequisites

- Python 3.10 or newer
- An AWS account with an S3 bucket
- An IAM user with an access key that can use that bucket

### 2. Install

```bash
git clone https://github.com/biscuitCurry/CloudVault.git
cd CloudVault

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 3. Configure

Copy `.env.example` to `.env` and fill in your own values:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Random string used to sign Flask sessions |
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | Bucket region, e.g. `ap-southeast-1` |
| `S3_BUCKET_NAME` | Name of your S3 bucket |

`.env` is listed in `.gitignore` and must never be committed.

### 4. Run

```bash
python app.py
```

Open http://127.0.0.1:5000, register an account, and start uploading.

## AWS setup

1. Create an S3 bucket and leave **Block all public access** turned on.
2. Create an IAM user and attach a policy limited to that bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::your-bucket-name"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

3. Create an access key for that user and put it in `.env`.

## Limitations

This is a coursework project, not a production service:

- User accounts are stored in a local `users.json` file rather than a database.
- The app runs on Flask's development server.
- There is no file size limit or file type validation.

## Team

- Mohamad Aliff Irfan Bin Abdullah — [@biscuitCurry](https://github.com/biscuitCurry)
- Muhammad Haikal Bin Mohammad Nazri
- Ammar Afiq Bin Azri
