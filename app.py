from flask import Flask, render_template, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# Define the main route for the directory
@app.route('/')
def home():
    # This will look for 'index.html' in your 'templates' folder
    return render_template('index.html')

# Define the new route for the blog
@app.route('/blog')
def blog():
    # This will look for 'blog.html' in your 'templates' folder
    return render_template('blog.html')

# This is the new route to handle brand suggestions
@app.route('/suggest', methods=['POST'])
def suggest():
    # Get the data sent from the form
    data = request.get_json()
    brand_name = data.get('brand_name')
    brand_website = data.get('brand_website')

    # Print the data to your terminal
    print("--- New Brand Suggestion Received ---")
    print(f"Brand Name: {brand_name}")
    print(f"Website: {brand_website}")
    print("------------------------------------")

    # Send a success response back to the browser
    return jsonify({'status': 'success', 'message': 'Thank you for your suggestion!'})

if __name__ == '__main__':
    app.run(debug=True)