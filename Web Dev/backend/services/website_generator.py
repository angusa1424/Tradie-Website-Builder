import jinja2
import os
from datetime import datetime
from ..utils.error_handlers import handle_error

class TradieWebsiteBot:
    def __init__(self):
        self.template_loader = jinja2.FileSystemLoader(
            searchpath=os.path.join(os.path.dirname(__file__), '../templates')
        )
        self.template_env = jinja2.Environment(loader=self.template_loader)
    
    def generate_website(self, business_info):
        """Generate a complete tradie website based on business info"""
        try:
            # Get template
            template = self.template_env.get_template(f"{business_info['template']}.html")
            
            # Prepare template data
            template_data = {
                'business_name': business_info['businessName'],
                'contact_info': {
                    'phone': business_info['phone'],
                    'email': business_info['email'],
                    'address': business_info['address']
                },
                'services': business_info['services'],
                'business_hours': business_info['businessHours'],
                'location': business_info['location'],
                'year': datetime.now().year
            }
            
            # Generate HTML
            html = template.render(**template_data)
            
            # Generate CSS
            css = self.generate_css()
            
            # Generate JS
            js = self.generate_js()
            
            # Combine everything
            complete_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{business_info['businessName']} - Professional {business_info['services'][0]} Services</title>
                <meta name="description" content="Professional {business_info['services'][0]} services in {business_info['location']}. Contact us for all your {business_info['services'][0]} needs.">
                <style>{css}</style>
            </head>
            <body>
                {html}
                <script>{js}</script>
            </body>
            </html>
            """
            
            return complete_html
            
        except Exception as e:
            raise handle_error(e)
    
    def generate_css(self):
        """Generate CSS for tradie website"""
        return """
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #e74c3c;
            --accent-color: #3498db;
            --text-color: #333;
            --light-bg: #f5f6fa;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: var(--text-color);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 40px 0;
            text-align: center;
        }
        
        .hero {
            background-color: var(--light-bg);
            padding: 60px 0;
            text-align: center;
        }
        
        .services {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        
        .service-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .contact-form {
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .business-hours {
            background: var(--light-bg);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .emergency-contact {
            background: var(--secondary-color);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }
        
        footer {
            background: var(--primary-color);
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }
        
        @media (max-width: 768px) {
            .services {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def generate_js(self):
        """Generate JavaScript for tradie website"""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth scrolling
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
            
            // Form validation
            const form = document.querySelector('.contact-form form');
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    // Add form validation logic here
                    alert('Thank you for your message. We will get back to you soon!');
                    form.reset();
                });
            }
            
            // Mobile menu toggle
            const menuToggle = document.querySelector('.menu-toggle');
            const nav = document.querySelector('nav');
            
            if (menuToggle && nav) {
                menuToggle.addEventListener('click', () => {
                    nav.classList.toggle('active');
                });
            }
        });
        """

# Create singleton instance
tradie_bot = TradieWebsiteBot()

def generate_website_html(business_info):
    """Generate complete website HTML"""
    try:
        return tradie_bot.generate_website(business_info)
    except Exception as e:
        raise handle_error(e) 