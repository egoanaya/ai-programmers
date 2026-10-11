import os
from openai import OpenAI

# Initialize the client to route to Google Gemini servers using the OpenAI library
client = OpenAI(
    api_key=os.environ["YOUR_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def analyze_sentiment(review):
    """
    Analyze the sentiment of a movie review using structured output.
    Returns a dictionary with 'thought' and 'sentiment' keys.
    """
    prompt = f"""
    Analyze the sentiment of the following movie review. 
    First, write out your thought process analyzing the words and tone. 
    Then, provide the final sentiment.
    
    You must use this exact format:
    thought: [your analysis]
    sentiment: [positive or negative]
    
    Review: "{review}"
    """

    response = client.chat.completions.create(
        model="gemini-3-flash-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content or ""

    thought_result = ""
    sentiment_result = ""
    
    # Convert everything to lowercase first, then split on the full word
    content_clean = content.lower()
    parts = content_clean.split("sentiment:") 
    
    if len(parts) == 2:
        thought_result = parts[0].replace("thought:", "").strip()
        sentiment_result = parts[1].strip()
    else:
        thought_result = content.strip()
        sentiment_result = "unknown"

    result = {
        "thought": thought_result,
        "sentiment": sentiment_result
    }
    
    return result

def main():
    reviews = [
        "This film shouldn't work at all. It doesn't have much of a story and the whole dial up internet thing is incredibly dated. However Hanks and Ryan sell it beautifully.",
        "The movie was terrible. The acting was wooden, the plot made no sense, and I want my two hours back.",
        "An absolute masterpiece! The cinematography was stunning, the acting was superb, and the story kept me engaged from start to finish."
    ]

    for i, review in enumerate(reviews, 1):
        result = analyze_sentiment(review)
        print(f"\nReview {i}:")
        print(f"Thought: {result['thought']}")
        print(f"Sentiment: {result['sentiment']}")

if __name__ == "__main__":
    main()
