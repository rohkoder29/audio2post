from playwright.sync_api import sync_playwright
from jinja2 import Environment, FileSystemLoader
import os

def render_html_to_image(html_content, output_path, width=1080, height=1080):
    """
    Renders HTML content to an image using Playwright.
    """
    try:
        print(f"Rendering to {output_path}...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            
            # Playwright needs a way to load the HTML. We can use set_content.
            # However, for local assets (if we add them later), we might need to handle base_url or file paths.
            # For now, everything is inline in the template (except google fonts).
            page.set_content(html_content, wait_until="networkidle")
            
            page.screenshot(path=output_path)
            browser.close()
            
        print(f"Successfully rendered {output_path}")
        return output_path
    except Exception as e:
        print(f"Rendering failed: {e}")
        return None

def generate_quote_card_html(quote, author, theme="dark"):
    """
    Populates the text into a Jinja2 template.
    """
    template_dir = os.path.join(os.getcwd(), "src", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("quote_card.html")
    
    return template.render(quote=quote, author=author, theme=theme)

def create_visual_assets(quotes, output_dir):
    """
    Generates images for a list of quotes.
    quotes: list of {'text': '...', 'author': '...'}
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    created_files = []
    
    for i, q in enumerate(quotes):
        html = generate_quote_card_html(q['text'], q['author'])
        output_path = os.path.join(output_dir, f"quote_{i+1}.png")
        if render_html_to_image(html, output_path):
            created_files.append(output_path)
            
    return created_files
