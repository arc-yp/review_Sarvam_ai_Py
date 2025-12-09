# AI Review Generator - Servam AI

This project generates realistic customer reviews using the Servam AI API.

## Features

- Interactive command-line interface
- Generates custom reviews based on business type and name
- Easy to integrate with other web projects
- Uses virtual environment for clean dependency management

## Setup Instructions

### 1. Activate Virtual Environment

**Windows:**

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the Script

```powershell
python review_generator.py
```

## Usage

1. Run the script
2. Enter the business type (e.g., "banana selling shop", "restaurant", "cafe")
3. Enter the business name
4. The AI will generate a realistic review
5. Option to generate another review or exit

## Example

```
📋 Enter the business type: banana selling shop
🏪 Enter the business name: Tropical Banana Paradise

⭐ GENERATED REVIEW ⭐
I recently visited Tropical Banana Paradise and was impressed by the fresh selection...
```

## API Configuration

The script uses Servam AI API with the following endpoint:

- Endpoint: `https://api.servam.ai/v1/chat/completions`
- Model: `gpt-3.5-turbo`

## Integration with Web Projects

This script can be easily integrated into web projects:

1. Import the `generate_review()` function
2. Pass business_type and business_name as parameters
3. Use the returned review text in your application

Example:

```python
from review_generator import generate_review

review = generate_review("restaurant", "Joe's Diner")
print(review)
```

## Notes

- Make sure you have an active internet connection
- The API key is embedded in the script
- For production use, consider storing the API key as an environment variable
