# 📝 Blog Platform using AWS services


---

## 🚀 Features

- ✅ **User Registration & Login** using AWS Cognito  
- 📦 **Create / Read / Update / Delete (CRUD)** blog posts with DynamoDB  
- 🖼️ **Image uploads** to AWS S3  
- 🔐 Secret Hash support for Cognito auth with client secret  
- 📅 Timestamps for created and updated posts

---

## 🛠️ Tech Stack

- **Python**
- **Flask**
- **HTML, CSS, JS**
- **AWS Cognito** (Auth)
- **AWS S3** (Media Storage)
- **AWS DynamoDB** (Database)
- **Boto3** (AWS SDK for Python)

---


---

## 🔧 Configuration

Create an `aws_config.py` file with the following variables:

```python
AWS_ACCESS_KEY = 'your-aws-access-key'
AWS_SECRET_KEY = 'your-aws-secret-key'
AWS_REGION = 'your-region'  # e.g., 'us-east-1'

COGNITO_USER_POOL_ID = 'your-user-pool-id'
COGNITO_CLIENT_SECRET = 'your-client-secret'
DYNAMODB_TABLE_NAME = 'your-dynamodb-table-name'
S3_BUCKET_NAME = 'your-s3-bucket-name'



# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Flask server
python app.py


