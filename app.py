import pytesseract
from PIL import Image
import boto3
import os
from decimal import Decimal

# Initialize S3 and DynamoDB clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Expenses')

# Download receipt from S3
def download_receipt(bucket, file_key, download_path):
    s3.download_file(bucket, file_key, download_path)

# Extract text using Tesseract
def extract_text_from_receipt(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

# Save extracted data to DynamoDB
def save_to_dynamodb(user_id, amount, description, date):
    table.put_item(
        Item={
            'UserId': user_id,
            'ExpenseId': str(uuid.uuid4()),
            'Amount': Decimal(str(amount)),
            'Description': description,
            'Date': date
        }
    )

# Main function to process the receipt
def process_receipt(bucket, file_key):
    download_path = '/tmp/' + file_key
    download_receipt(bucket, file_key, download_path)

    # Use Tesseract to extract text from the receipt
    extracted_text = extract_text_from_receipt(download_path)
    
    # Parse the extracted text to get necessary details (this would require custom logic)
    total_amount = parse_total(extracted_text)
    description = 'Sample description'
    user_id = 'User1'
    date = '2024-09-29'

    # Save the data to DynamoDB
    save_to_dynamodb(user_id, total_amount, description, date)

    return 'Processed successfully!'

def parse_total(text):
    # Implement logic to find the "Total" in the text (as demonstrated in previous steps)
    lines = text.split('\n')
    for line in lines:
        if 'TOTAL' in line.upper() or 'TOTAL PURCHASE' in line.upper():
            try:
                return float(line.split()[-1].replace('$', ''))
            except ValueError:
                continue
    return 0.00

if __name__ == "__main__":
    bucket = 'et-receipts-bucket'
    file_key = 'receipt.jpg'
    process_receipt(bucket, file_key)
