from flask import Flask, render_template, request, jsonify, send_file, make_response
import json
import os
import csv
from datetime import datetime
from io import StringIO, BytesIO
from advanced_review_generator import ReviewGenerator
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)

# File to store reviews
REVIEWS_FILE = "reviews_history.json"

def load_reviews():
    """Load reviews from JSON file"""
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_review(review_data):
    """Save review to JSON file"""
    reviews = load_reviews()
    reviews.append(review_data)
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    """Home page with form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate review via API"""
    try:
        # Get form data
        business_name = request.form.get('business_name')
        business_type = request.form.get('business_type')
        category = request.form.get('category')
        star_rating = int(request.form.get('star_rating'))
        language = request.form.get('language')
        use_case = request.form.get('use_case')
        
        # Validate inputs
        if not all([business_name, business_type, category]):
            return jsonify({'success': False, 'error': 'All fields are required!'})
        
        # Generate review
        generator = ReviewGenerator()
        result = generator.generate_review(
            business_name=business_name,
            business_type=business_type,
            category=category,
            star_rating=star_rating,
            language=language,
            use_case=use_case
        )
        
        if result['success']:
            # Prepare data to save
            review_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'business_name': business_name,
                'business_type': business_type,
                'category': category,
                'star_rating': star_rating,
                'language': language,
                'use_case': use_case,
                'review': result['review'],
                'char_count': result['char_count'],
                'token_usage': result.get('token_usage', {}),
                'method': result['method']
            }
            
            # Save to file
            save_review(review_data)
            
            return jsonify({
                'success': True,
                'review': result['review'],
                'char_count': result['char_count'],
                'token_usage': result.get('token_usage', {}),
                'method': result['method']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/history')
def history():
    """View all generated reviews"""
    reviews = load_reviews()
    return render_template('history.html', reviews=reviews)

@app.route('/health')
def health_check():
    """API Health Check Page"""
    return render_template('health.html')

@app.route('/api/reviews')
def api_reviews():
    """API endpoint to get all reviews"""
    reviews = load_reviews()
    return jsonify(reviews)

@app.route('/download/csv')
def download_csv():
    """Download reviews as CSV file"""
    reviews = load_reviews()
    
    if not reviews:
        return "No reviews to download", 404
    
    # Get selected indices from query parameter
    indices_param = request.args.get('indices', '')
    if indices_param:
        try:
            selected_indices = [int(i) for i in indices_param.split(',')]
            # Reverse the reviews list to match the display order
            reviews_reversed = list(reversed(reviews))
            reviews = [reviews_reversed[i] for i in selected_indices if i < len(reviews_reversed)]
        except (ValueError, IndexError):
            return "Invalid indices", 400
    
    if not reviews:
        return "No reviews selected", 400
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp', 'Business Name', 'Business Type', 'Category',
        'Star Rating', 'Language', 'Use Case', 'Review Text',
        'Character Count', 'Tokens Used', 'Method'
    ])
    
    # Write data
    for review in reviews:
        writer.writerow([
            review.get('timestamp', ''),
            review.get('business_name', ''),
            review.get('business_type', ''),
            review.get('category', ''),
            review.get('star_rating', ''),
            review.get('language', ''),
            review.get('use_case', ''),
            review.get('review', ''),
            review.get('char_count', ''),
            review.get('token_usage', {}).get('total_tokens', 'N/A'),
            review.get('method', '')
        ])
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/download/pdf')
def download_pdf():
    """Download reviews as PDF file"""
    reviews = load_reviews()
    
    if not reviews:
        return "No reviews to download", 404
    
    # Get selected indices from query parameter
    indices_param = request.args.get('indices', '')
    if indices_param:
        try:
            selected_indices = [int(i) for i in indices_param.split(',')]
            # Reverse the reviews list to match the display order
            reviews_reversed = list(reversed(reviews))
            reviews = [reviews_reversed[i] for i in selected_indices if i < len(reviews_reversed)]
        except (ValueError, IndexError):
            return "Invalid indices", 400
    
    if not reviews:
        return "No reviews selected", 400
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12
    )
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("AI Review Generator - Export Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Paragraph(f"Total Reviews: {len(reviews)}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add each review
    for idx, review in enumerate(reviews, 1):
        # Review header
        elements.append(Paragraph(f"Review #{idx}", heading_style))
        
        # Create info table
        data = [
            ['Business Name:', review.get('business_name', 'N/A')],
            ['Type:', review.get('business_type', 'N/A')],
            ['Category:', review.get('category', 'N/A')],
            ['Rating:', '★' * review.get('star_rating', 0)],
            ['Language:', review.get('language', 'N/A')],
            ['Use Case:', review.get('use_case', 'N/A')],
            ['Date:', review.get('timestamp', 'N/A')],
        ]
        
        table = Table(data, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Review text
        elements.append(Paragraph("<b>Review:</b>", normal_style))
        review_text = review.get('review', 'N/A')
        elements.append(Paragraph(review_text, normal_style))
        
        # Stats
        char_count = review.get('char_count', 'N/A')
        tokens = review.get('token_usage', {}).get('total_tokens', 'N/A')
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(f"<i>Characters: {char_count} | Tokens: {tokens}</i>", normal_style))
        
        elements.append(Spacer(1, 0.4*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    if debug_mode:
        print("\n" + "=" * 70)
        print("  🌟 AI REVIEW GENERATOR - Web Interface")
        print("=" * 70)
        print("\n✅ Server starting...")
        print(f"📍 Open your browser and go to: http://localhost:{port}")
        print("💾 Reviews are saved to: reviews_history.json")
        print("\n⚠️  Press CTRL+C to stop the server")
        print("=" * 70 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
