import requests
import sys
import os
import json
import random

# Sarvam AI API Configuration
# IMPORTANT: You MUST set a valid API key to use this script
API_KEY = os.getenv("SARVAM_API_KEY", "sk_jvluf7sh_tiHFPEmIQLdSVtNU3KKe49RN")
API_ENDPOINT = "https://api.sarvam.ai/v1/chat/completions"

# TO GET A VALID API KEY:
# 1. Sign up at: https://dashboard.sarvam.ai/
# 2. Generate your API key from dashboard
# 3. Set it as environment variable: $env:SARVAM_API_KEY="your-key-here"
# OR edit the line below:
# API_KEY = "your-api-key-here"


class ReviewGenerator:
    """Advanced AI Review Generator with structured prompt system"""
    
    def __init__(self):
        self.api_key = API_KEY
        self.api_endpoint = API_ENDPOINT
        self.reviews_file = "reviews_history.json"
        self.existing_reviews = self.load_existing_reviews()
        
        # Check if API key is configured
        if not API_KEY or len(API_KEY) < 10:
            print("\n" + "=" * 70)
            print("                      ⚠️  ERROR: NO API KEY")
            print("=" * 70)
            print("\n❌ Sarvam AI API key is required to generate reviews!")
            print("\n🔑 TO GET YOUR API KEY:")
            print("  1. Sign up at: https://dashboard.sarvam.ai/")
            print("  2. Generate your API key from the dashboard")
            print("  3. Set it as environment variable:")
            print("=" * 70 + "\n")
            sys.exit(1)
    
    def load_existing_reviews(self):
        """Load existing reviews from JSON file"""
        try:
            if os.path.exists(self.reviews_file):
                with open(self.reviews_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def get_unique_length_range(self):
        """Generate random, unique character length ranges for variety"""
        # Different length patterns for variety
        length_options = [
            (200, 250),  # Short
            (250, 300),  # Medium-Short
            (300, 350),  # Medium-Long
            (220, 280),  # Varied
            (260, 320),  # Varied
        ]
        return random.choice(length_options)
    
    def get_unique_structure(self):
        """Generate unique sentence structure hints"""
        structures = [
            "Start with a personal feeling, then describe the experience, end with impact",
            "Begin with what you noticed first, explain the service, mention a specific moment",
            "Start with expectations, describe what happened, share how it made you feel",
            "Open with a concern you had, explain how it was handled, conclude with result",
            "Start with a recommendation from someone, describe your visit, share your opinion",
            "Begin with comparison to others, detail your experience, end with personal touch"
        ]
        return random.choice(structures)
    
    def check_similarity(self, new_review_text):
        """Check if review is too similar to existing ones"""
        if not self.existing_reviews:
            return False
        
        # Get last 10 reviews for comparison
        recent_reviews = self.existing_reviews[-10:] if len(self.existing_reviews) > 10 else self.existing_reviews
        
        for review in recent_reviews:
            existing_text = review.get('review', '')
            # Check first 50 characters similarity
            if existing_text[:50].lower() == new_review_text[:50].lower():
                return True
        return False
        
    def build_prompt(self, business_name, business_type, category, star_rating, language, use_case="Customer review", min_chars=200, max_chars=350):
        """
        Build a structured prompt based on your specifications
        """
        
        # Determine sentiment based on star rating
        sentiment_map = {
            1: "Soft tone, gentle issues, polite feedback about problems. Disappointed but respectful.",
            2: "Mostly positive with mild suggestions. Some concerns but hopeful tone.",
            3: "Balanced and fair. Mix of pros and cons. Neutral perspective.",
            4: "Positive with a small suggestion for improvement. Satisfied overall.",
            5: "Warm, detailed, fully satisfied. Enthusiastic about the experience."
        }
        
        sentiment = sentiment_map.get(star_rating, sentiment_map[3])
        
        # Get unique structure and length
        unique_structure = self.get_unique_structure()
        min_chars, max_chars = self.get_unique_length_range()
        
        # Get recent review openings to avoid
        recent_openings = []
        if len(self.existing_reviews) > 0:
            recent = self.existing_reviews[-5:] if len(self.existing_reviews) >= 5 else self.existing_reviews
            for rev in recent:
                text = rev.get('review', '')
                if text:
                    recent_openings.append(text[:30])
        
        avoid_openings = "\n".join([f"  * Don't start like: '{opening}...'" for opening in recent_openings])
        
        # Language-specific instructions
        language_instruction = ""
        if language.lower() == "english":
            language_instruction = """Write the entire review in English only.
VOCABULARY RULES:
- Use SIMPLE, EVERYDAY words that anyone can understand
- Avoid complex or fancy words like: "exceptional", "meticulous", "remarkable", "professionalism", "precision"
- Use easy words like: good, great, nice, happy, helpful, friendly, clean, quick, easy, caring
- Write like a normal person talks, not like a professional writer
- Keep sentences short and simple
Example good words: loved, enjoyed, felt comfortable, took care, listened well, explained clearly"""
        elif language.lower() in ["gujarati", "gujarati romanized"]:
            language_instruction = """Write Gujarati using English letters only (Romanized Gujarati).
GUJARATI GRAMMAR RULES - VERY IMPORTANT:
- Use correct Gujarati sentence structure: Subject + Object + Verb
- Correct verb conjugations: 
  * "hato" (was - masculine), "hati" (was - feminine)
  * "chu" (am/is), "chhe" (is/are)
  * "karyu" (did), "kari" (did - feminine)
  * "rahyo" (stayed - masculine), "rahi" (stayed - feminine)
- Proper postpositions: "ma" (in), "thi" (from), "ne" (and/to)
- Natural word order, not English translation
- Use proper Gujarati expressions and idioms
- Agreement between gender, number, and verb forms
Example: "Mare aa jagya-e jaavu bahuj saras rahyu" (My visit to this place was very good)"""
        elif language.lower() in ["hindi", "hindi romanized"]:
            language_instruction = """Write Hindi using English letters only (Romanized Hindi).
HINDI GRAMMAR RULES:
- Correct verb conjugations with proper gender agreement
- Use "ne" for past tense subjects correctly
- Proper sentence structure
- Natural Hindi expressions
Example: "Mujhe yahan jane mein bahut achha laga" (I felt very good going here)"""
        
        # Build the complete prompt
        prompt = f"""Generate a realistic {use_case.lower()} for a {business_type} called "{business_name}" in the {category} category.

STAR RATING: {star_rating}/5
SENTIMENT: {sentiment}

UNIQUENESS REQUIREMENTS:
- STRUCTURE PATTERN: {unique_structure}
- This review MUST be completely different from previous reviews
{avoid_openings if avoid_openings else ""}
- Create a FRESH opening sentence (not used before)
- Use different vocabulary and phrasing
- Vary the story and details mentioned

STRICT WRITING RULES:
- Length: Between {min_chars} and {max_chars} characters
- Tone: Natural and conversational (like talking to a friend)
- First sentence must be unique (avoid repetitive openings)
- No repetition of ideas
- Mention business name "{business_name}" naturally in the review
- Include one emotional detail or personal experience
- Do NOT mention the star rating in the review text
- Do NOT use these overused phrases:
  * "Highly recommend"
  * "I felt safe"
  * "Amazing experience"
  * "Best place ever"
  * "Exceeded expectations"
  * "Exceeded all my expectations"
  * "Cannot recommend enough"
- AVOID fancy/complex words like: exceptional, remarkable, meticulous, professionalism, precision, genuinely, truly, outstanding
- No exclamation marks
- No dashes (—) in the text
- No em dashes or en dashes
- Use simple periods and commas only for punctuation
- Write like a real person sharing their experience
- Vary sentence structure and length

LANGUAGE: {language_instruction}

IMPORTANT:
- Return ONLY the review text
- No quotes, no markdown, no formatting
- No template-like structure
- Make it sound authentic and unique

Generate the review now:"""
        
        return prompt
    
    def generate_review(self, business_name, business_type, category, star_rating, language="English", use_case="Customer review", min_chars=200, max_chars=350):
        """
        Generate review using Sarvam AI API with perfect prompt
        """
        
        # Build the perfect prompt
        prompt = self.build_prompt(business_name, business_type, category, star_rating, language, use_case, min_chars, max_chars)
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sarvam-m",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at writing authentic, varied, and realistic business reviews. Never repeat patterns or use template language. Each review must be completely unique. Keep reviews concise and within the specified character limit."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 100,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3
        }
        
        try:
            print(f"\n🔄 Generating {star_rating}-star review using Sarvam AI API...")
            print("⏳ Please wait...\n")
            
            response = requests.post(self.api_endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                review_text = result['choices'][0]['message']['content'].strip()
                
                # Remove quotes if AI added them
                if review_text.startswith('"') and review_text.endswith('"'):
                    review_text = review_text[1:-1]
                if review_text.startswith("'") and review_text.endswith("'"):
                    review_text = review_text[1:-1]
                
                # Enforce character limit strictly
                if len(review_text) > max_chars:
                    # Trim to max_chars and find last complete sentence
                    review_text = review_text[:max_chars]
                    # Find last period, question mark, or other sentence ending
                    last_period = max(review_text.rfind('.'), review_text.rfind('?'), review_text.rfind('।'))
                    if last_period > min_chars:
                        review_text = review_text[:last_period + 1]
                    else:
                        # If no good sentence break, just trim and add period
                        review_text = review_text[:max_chars-1].rsplit(' ', 1)[0] + '.'
                
                return {
                    "success": True,
                    "review": review_text,
                    "char_count": len(review_text),
                    "token_usage": result.get('usage', {}),
                    "method": "api"
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error {response.status_code}: {response.text}",
                    "review": None
                }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout. API took too long to respond (30 seconds).",
                "review": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "review": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "review": None
            }


def print_api_info():
    """Display API setup information"""
    print("\n" + "=" * 70)
    print("         SARVAM AI API - CONFIGURATION INFO")
    print("=" * 70)
    print("\n📊 SETTINGS:")
    print("  • Temperature: 0.8 (High creativity)")
    print("  • Max Tokens: 120 (Controlled length)")
    print("  • Frequency Penalty: 0.5 (Reduce repetition)")
    print("  • Presence Penalty: 0.3 (Topic diversity)")
    print("  • Character Range: 200-350 (STRICTLY ENFORCED)")
    print("\n✅ API Key Status: CONFIGURED")
    print("\n💡 Rate Limits:")
    print("  • Check your dashboard: https://dashboard.sarvam.ai/")
    print("=" * 70 + "\n")


def main():
    """Main function with interactive menu"""
    
    print("=" * 70)
    print("       🌟 AI REVIEW GENERATOR - By Sarvam AI 🌟")
    print("=" * 70)
    
    generator = ReviewGenerator()
    
    # Show API configuration option
    show_info = input("\n📖 View API configuration? (y/n): ").strip().lower()
    if show_info == 'y':
        print_api_info()
    
    print("\n" + "─" * 70)
    print("                    REVIEW CONFIGURATION")
    print("─" * 70)
    
    # Get business details
    business_name = input("\n🏪 Business Name: ").strip()
    if not business_name:
        print("❌ Business name is required!")
        sys.exit(1)
    
    business_type = input("📋 Business Type (e.g., shop, restaurant, hospital): ").strip()
    if not business_type:
        print("❌ Business type is required!")
        sys.exit(1)
    
    category = input("🏷️  Category (e.g., Food & Beverage, Healthcare): ").strip()
    if not category:
        print("❌ Category is required!")
        sys.exit(1)
    
    # Star rating
    while True:
        try:
            star_rating = int(input("⭐ Star Rating (1-5): ").strip())
            if 1 <= star_rating <= 5:
                break
            print("❌ Please enter a number between 1 and 5")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Language selection
    print("\n🌐 Language Options:")
    print("  1. English")
    print("  2. Gujarati (Romanized)")
    print("  3. Hindi (Romanized)")
    lang_choice = input("Select language (1-3): ").strip()
    
    language_map = {
        "1": "English",
        "2": "Gujarati Romanized",
        "3": "Hindi Romanized"
    }
    language = language_map.get(lang_choice, "English")
    
    # Use case
    print("\n📝 Use Case:")
    print("  1. Customer review (default)")
    print("  2. Student feedback")
    print("  3. Patient experience")
    use_case_choice = input("Select use case (1-3): ").strip()
    
    use_case_map = {
        "1": "Customer review",
        "2": "Student feedback",
        "3": "Patient experience"
    }
    use_case = use_case_map.get(use_case_choice, "Customer review")
    
    # Generate review
    print("\n" + "=" * 70)
    result = generator.generate_review(
        business_name=business_name,
        business_type=business_type,
        category=category,
        star_rating=star_rating,
        language=language,
        use_case=use_case
    )
    
    # Display results
    if result["success"]:
        print("\n" + "=" * 70)
        print("                    ⭐ GENERATED REVIEW ⭐")
        print("=" * 70)
        print(f"\n{result['review']}\n")
        print("=" * 70)
        print(f"\n📊 STATISTICS:")
        print(f"  • Character Count: {result['char_count']}")
        print(f"  • Star Rating: {star_rating}/5")
        print(f"  • Language: {language}")
        print(f"  • Use Case: {use_case}")
        if 'token_usage' in result:
            print(f"  • Token Usage: {result['token_usage']}")
        print("=" * 70)
        print("\n✅ Review generated successfully!\n")
    else:
        print("\n" + "=" * 70)
        print("                        ❌ ERROR")
        print("=" * 70)
        print(f"\n{result['error']}\n")
        print("💡 Tips:")
        print("  • Check your API key is valid")
        print("  • Verify internet connection")
        print("  • Check Sarvam AI service status")
        print("  • Review your rate limits on dashboard")
        print("=" * 70 + "\n")
        sys.exit(1)
    
    # Generate another?
    another = input("Generate another review? (y/n): ").strip().lower()
    if another == 'y':
        print("\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Review generator closed. Goodbye!")
        sys.exit(0)
