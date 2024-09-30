from flask import Flask, request, jsonify
import boto3
import re

app = Flask(__name__)

# AWS Clients
s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ExpensesTable')




def extract_text_from_s3(bucket_name, file_name):
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': file_name}}
    )
    return response


def store_expense_data(user_id, expense_id, amount, date, description):
    table.put_item(
        Item={
            'UserId': user_id,
            'ExpenseId': expense_id,
            'Amount': amount,
            'Date': date,
            'Description': description
        }
    )


# Function to extract total from text
def extract_total_amount(extracted_text):
    total_pattern = re.compile(r'(total|amount due|balance)', re.IGNORECASE)
    amount_pattern = re.compile(r'\$\s?([0-9,.]+)')

    for line in extracted_text:
        if total_pattern.search(line):
            amount_match = amount_pattern.search(line)
            if amount_match:
                return amount_match.group(0)
    return None

# Function to upload receipt to S3 and process it
@app.route('/upload', methods=['POST'])
def upload_receipt():
    file = request.files['file']
    bucket_name = 'et-receipts-bucket'
    s3.upload_fileobj(file, bucket_name, file.filename)

    # Extract text from the receipt
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': file.filename}}
    )

    # Parse the extracted text
    extracted_text = [block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE']
    total_amount = extract_total_amount(extracted_text)

    # Store the extracted data in DynamoDB
    store_expense_data('user123', 'expense456', total_amount, '2024-09-30', 'Sample receipt')

    return jsonify({"Total Amount": total_amount})

if __name__ == "__main__":
    app.run(debug=True)
