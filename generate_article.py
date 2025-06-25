import os
import google.generativeai as genai
from bs4 import BeautifulSoup
from datetime import datetime
import random

# --- CONFIGURATION ---
# The script now gets the API key from a GitHub Secret (environment variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BLOG_DIR = "blog"
BLOG_LIST_PATH = os.path.join(BLOG_DIR, "blog.html")
TOPICS_FILE_PATH = "topics.txt"
# New configuration for the prompt file
PROMPT_FILE_PATH = "prompt.txt"
# --- END CONFIGURATION ---

def configure_gemini():
    """Configures the Gemini API with the provided key."""
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not found.")
        exit()
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        exit()

def get_next_post_number():
    """Finds the next available number for a new blog post."""
    try:
        files = os.listdir(BLOG_DIR)
        post_numbers = [int(f.split('-')[-1].split('.')[0]) for f in files if f.startswith('blog-post-') and f.endswith('.html')]
        return max(post_numbers) + 1 if post_numbers else 1
    except FileNotFoundError:
        print(f"Error: The directory '{BLOG_DIR}' was not found.")
        exit()
    except Exception as e:
        print(f"Error reading blog directory: {e}")
        exit()

def load_topics_from_file(file_path):
    """Loads a list of topics from a given text file."""
    print(f"Loading topics from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            topics = [line.strip() for line in f if line.strip()]
        if not topics:
            print(f"Warning: {file_path} is empty or contains no valid topics.")
            return []
        return topics
    except FileNotFoundError:
        print(f"Error: Topics file not found at '{file_path}'. Please create it.")
        return []
    except Exception as e:
        print(f"Error reading topics file: {e}")
        return []

# NEW FUNCTION to load the prompt from a text file
def load_prompt_from_file(file_path):
    """Loads the prompt template from a given text file."""
    print(f"Loading prompt from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        if not prompt:
            print(f"Error: Prompt file '{file_path}' is empty.")
            return None
        return prompt
    except FileNotFoundError:
        print(f"Error: Prompt file not found at '{file_path}'. Please create it.")
        return None
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return None

def generate_content_with_gemini(topic, prompt_template):
    """
    Generates a blog article (title, description, body) using the Gemini API.
    """
    print(f"Generating article for topic: {topic}...")
    model = genai.GenerativeModel('gemini-2.5-pro')

    # MODIFIED: Dynamically insert the topic into the prompt template
    final_prompt = prompt_template.format(topic=topic)

    try:
        response = model.generate_content(final_prompt)
        cleaned_text = response.text.replace('```html', '').replace('```', '').strip()
        parts = cleaned_text.split('---', 2)
        if len(parts) == 3:
            return {
                "title": parts[0].strip(),
                "description": parts[1].strip(),
                "body": parts[2].strip()
            }
        else:
            print("Error: Gemini API did not return the expected format.")
            return None
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None


def create_new_blog_post_file(post_number, content):
    """Creates a new HTML file for the blog post from a template."""
    new_file_path = os.path.join(BLOG_DIR, f"blog-post-{post_number}.html")
    print(f"Creating new file: {new_file_path}...")

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NZVFXWBJJ7"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-NZVFXWBJJ7');
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9886602787991072"
     crossorigin="anonymous"></script>
    <title>{content['title']} | Free Percentage Calculator</title>
    <meta name="description" content="{content['description']}">
    <link rel="canonical" href="https://www.yourwebsite.com/blog/blog-post-{post_number}.html">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.tailwindcss.com/3.4.4?plugins=typography"></script>
    <style>
        :root {{ --apple-blue: #007AFF; --apple-light-gray: #f2f2f7; --apple-card-bg: #ffffff; --apple-text-primary: #1d1d1f; }}
        body {{ background-color: var(--apple-light-gray); color: var(--apple-text-primary); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        .apple-card {{ background-color: var(--apple-card-bg); border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05); }}
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <nav class="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-50">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between h-16">
                <a href="../index.html" class="text-xl font-bold text-slate-800">% Calculator</a>
                <div class="hidden md:flex items-center space-x-8">
                    <a href="../index.html" class="text-slate-600 hover:text-blue-600 transition-colors">Calculator</a>
                    <a href="blog.html" class="text-slate-600 hover:text-blue-600 transition-colors">Blog</a>
                </div>
            </div>
        </div>
    </nav>
    <div class="container mx-auto px-4 py-8 md:py-12 flex-grow">
        <main class="max-w-3xl mx-auto">
            <div class="mb-6">
                <a href="blog.html" class="text-blue-600 hover:underline">&larr; Back to Blog</a>
            </div>
            <article class="apple-card p-6 md:p-8 prose max-w-none prose-slate">
                <h1>{content['title']}</h1>
                {content['body']}
            </article>
        </main>
    </div>
    <footer class="text-center py-6 text-sm text-slate-500">
        &copy; <span id="year"></span> Percentage Calculator. All rights reserved.
    </footer>
    <script>
        document.getElementById('year').textContent = new Date().getFullYear();
    </script>
</body>
</html>
    """

    try:
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print("Successfully created new blog post file.")
    except Exception as e:
        print(f"Error writing to file {new_file_path}: {e}")

def update_blog_list(post_number, content):
    """Adds a new entry to the main blog list page."""
    print(f"Updating {BLOG_LIST_PATH}...")
    try:
        with open(BLOG_LIST_PATH, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        main_content_div = soup.find('main').find('div', class_='grid')
        if not main_content_div:
            print("Error: Could not find the main content grid in blog.html")
            return

        new_article_html = f"""
        <article class="apple-card overflow-hidden">
            <div class="p-6">
                <h2 class="text-xl font-semibold mb-3 text-slate-800">{content['title']}</h2>
                <p class="text-slate-600 mb-4">{content['description']}</p>
                <a href="blog-post-{post_number}.html" class="text-blue-600 hover:underline">Read more &rarr;</a>
            </div>
        </article>
        """
        new_article_soup = BeautifulSoup(new_article_html, 'html.parser')
        main_content_div.insert(0, new_article_soup)

        with open(BLOG_LIST_PATH, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("Successfully updated blog list page.")

    except FileNotFoundError:
        print(f"Error: {BLOG_LIST_PATH} not found.")
    except Exception as e:
        print(f"Error updating blog list: {e}")


def main():
    """Main function to run the script."""
    configure_gemini()
    post_number = get_next_post_number()

    # Load the prompt template from the file
    prompt_template = load_prompt_from_file(PROMPT_FILE_PATH)
    if not prompt_template:
        print("No prompt template found. Exiting.")
        return

    topics = load_topics_from_file(TOPICS_FILE_PATH)
    if not topics:
        print("No topics found. Exiting.")
        return
    
    topic = random.choice(topics)

    # Pass the prompt template to the generation function
    content = generate_content_with_gemini(topic, prompt_template)

    if content:
        create_new_blog_post_file(post_number, content)
        update_blog_list(post_number, content)
        print("\nProcess finished successfully!")

if __name__ == '__main__':
    main()
