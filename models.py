import boto3
import uuid
from datetime import datetime
import aws_config
import hmac
import hashlib
import base64
import botocore.exceptions

class DynamoDBManager:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb', 
            region_name=aws_config.AWS_REGION,
            aws_access_key_id=aws_config.AWS_ACCESS_KEY,
            aws_secret_access_key=aws_config.AWS_SECRET_KEY
        )
        self.table = self.dynamodb.Table(aws_config.DYNAMODB_TABLE_NAME)
    
    def create_post(self, title, content, author, image_url=None):
        post_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        item = {
            'post_id': post_id,
            'title': title,
            'content': content,
            'author': author,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        if image_url:
            item['image_url'] = image_url
            
        self.table.put_item(Item=item)
        return post_id
    
    def get_post(self, post_id):
        response = self.table.get_item(Key={'post_id': post_id})
        return response.get('Item')
    
    def get_all_posts(self):
        response = self.table.scan()
        return response.get('Items', [])
    
    def update_post(self, post_id, title, content, image_url=None):
        update_expression = "SET title = :title, content = :content, updated_at = :updated_at"
        expression_values = {
            ':title': title,
            ':content': content,
            ':updated_at': datetime.now().isoformat()
        }
        
        if image_url:
            update_expression += ", image_url = :image_url"
            expression_values[':image_url'] = image_url
            
        self.table.update_item(
            Key={'post_id': post_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
    
    def delete_post(self, post_id):
        self.table.delete_item(Key={'post_id': post_id})


class S3Manager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            region_name=aws_config.AWS_REGION,
            aws_access_key_id=aws_config.AWS_ACCESS_KEY,
            aws_secret_access_key=aws_config.AWS_SECRET_KEY
        )
        self.bucket_name = aws_config.S3_BUCKET_NAME
    
    def upload_image(self, file_obj, filename):
        """Upload an image to S3 bucket"""
        file_id = str(uuid.uuid4())
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        new_filename = f"{file_id}.{ext}"
        
        self.s3.upload_fileobj(
            file_obj,
            self.bucket_name,
            new_filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': f'image/{ext}'}
        )
        
        return f"https://{self.bucket_name}.s3.amazonaws.com/{new_filename}"


class CognitoManager:
    def __init__(self):
        self.client = boto3.client(
            'cognito-idp',
            region_name=aws_config.AWS_REGION  # Use the region from your config
        )
        self.user_pool_id = aws_config.COGNITO_USER_POOL_ID  # Use the actual variable
        self.client_id = aws_config.COGNITO_APP_CLIENT_ID
        self.client_secret = aws_config.COGNITO_CLIENT_SECRET  # Add this to your aws_config.py
    
    def get_secret_hash(self, username):
        # This creates the secret hash required by Cognito
        message = username + self.client_id
        dig = hmac.new(
            key=self.client_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()
    
    def register_user(self, username, email, password):
        try:
            # Include the SECRET_HASH in the sign up request
            response = self.client.sign_up(
                ClientId=self.client_id,
                SecretHash=self.get_secret_hash(username),  # This was missing
                Username=username,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    }
                ]
            )
            return True, response
        except botocore.exceptions.ClientError as e:
            return False, str(e)
    
    def confirm_user(self, username, confirmation_code):
        try:
            # Include the SECRET_HASH in the confirm request too
            response = self.client.confirm_sign_up(
                ClientId=self.client_id,
                SecretHash=self.get_secret_hash(username),  # This was missing
                Username=username,
                ConfirmationCode=confirmation_code
            )
            return True, response
        except botocore.exceptions.ClientError as e:
            return False, str(e)
    
    def login_user(self, username, password):
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password,
                    'SECRET_HASH': self.get_secret_hash(username)  # ✅ Move it here
                }
            )
            return True, response
        except botocore.exceptions.ClientError as e:
            return False, str(e)
