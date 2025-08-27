import os
import logging
from typing import Dict, Any
from src.utils.exceptions import TemplateServiceError

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for loading and rendering email templates."""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template service.
        
        Args:
            templates_dir: Directory containing email templates
        """
        self.templates_dir = templates_dir
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), templates_dir)
        
    def render_template(self, template_name: str, language: str, template_data: Dict[str, Any]) -> str:
        """
        Load and render an email template with provided data.
        
        Args:
            template_name: Name of the template (e.g., 'greeting', 'candidate-interview-scheduled')
            language: Language code (e.g., 'en', 'ua')
            template_data: Dictionary containing data to populate the template
            
        Returns:
            Rendered HTML content as string
            
        Raises:
            EmailProcessingError: If template cannot be loaded or rendered
        """
        try:
            # Load the template
            template_content = self._load_template(template_name, language)
            
            # Render the template with data
            rendered_content = self._render_content(template_content, template_data)
            
            logger.info(f"Successfully rendered template: {template_name} ({language})")
            return rendered_content
            
        except Exception as e:
            error_msg = f"Failed to render template {template_name} ({language}): {str(e)}"
            logger.error(error_msg)
            raise TemplateServiceError(error_msg)
    
    def _load_template(self, template_name: str, language: str) -> str:
        """
        Load template content from file.
        
        Args:
            template_name: Name of the template
            language: Language code
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = os.path.join(self.base_path, template_name, f"{language}.html")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            logger.debug(f"Loaded template from: {template_path}")
            return content
            
        except Exception as e:
            raise Exception(f"Error reading template file {template_path}: {str(e)}")
    
    def _render_content(self, template_content: str, template_data: Dict[str, Any]) -> str:
        """
        Render template content by replacing placeholders with actual data.
        
        Args:
            template_content: Raw template content
            template_data: Data to populate the template
            
        Returns:
            Rendered content with placeholders replaced
        """
        try:
            # Handle special case for skill lists (convert list to HTML)
            processed_data = self._process_template_data(template_data.copy())
            
            # Inline CSS styles for email compatibility
            rendered_content = self._inline_styles(template_content)
            
            # Use string format to replace placeholders
            rendered_content = rendered_content.format(**processed_data)
            
            return rendered_content
            
        except KeyError as e:
            raise Exception(f"Missing template variable: {str(e)}")
        except Exception as e:
            raise Exception(f"Error rendering template: {str(e)}")
    
    def _process_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process template data to handle special cases like skill lists.
        
        Args:
            template_data: Raw template data
            
        Returns:
            Processed template data
        """
        # Handle candidate_skills as a list that needs to be converted to HTML
        if 'candidate_skills' in template_data:
            if isinstance(template_data['candidate_skills'], list):
                skills_html = ''.join([f'<li>{skill}</li>' for skill in template_data['candidate_skills']])
                template_data['candidate_skills'] = skills_html
        
        # Handle other list fields similarly if needed
        if 'interviewer_skills' in template_data:
            if isinstance(template_data['interviewer_skills'], list):
                skills_html = ''.join([f'<li>{skill}</li>' for skill in template_data['interviewer_skills']])
                template_data['interviewer_skills'] = skills_html
        
        # Ensure all values are strings to avoid formatting errors
        for key, value in template_data.items():
            if value is None:
                template_data[key] = ''
            elif not isinstance(value, str):
                template_data[key] = str(value)
        
        return template_data
    
    def _inline_styles(self, template_content: str) -> str:
        """
        Convert external CSS links to inline styles for email compatibility.
        
        Args:
            template_content: HTML content with potential CSS links
            
        Returns:
            HTML content with inlined styles
        """
        # Remove CSS link tags and replace with inline styles
        if '<link rel="stylesheet"' in template_content:
            # Remove the link tag
            import re
            template_content = re.sub(r'<link[^>]*rel="stylesheet"[^>]*>', '', template_content)
            
            # Load and inline the CSS
            template_content = self._apply_greeting_styles(template_content)
        
        return template_content
    
    def _apply_greeting_styles(self, template_content: str) -> str:
        """Apply inline styles for greeting templates with mobile optimization."""
        # Add viewport meta tag for mobile responsiveness
        if '<meta name="viewport"' not in template_content:
            template_content = template_content.replace(
                '<meta charset="UTF-8">',
                '<meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            )
        
        # Replace class-based styling with mobile-optimized inline styles
        template_content = template_content.replace(
            '<div class="greeting-container">',
            '<div style="max-width: 600px; width: 100%; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1); overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Arial, sans-serif; line-height: 1.6; color: #333333;">'
        )
        
        template_content = template_content.replace(
            '<div class="greeting-header">',
            '<div style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 24px 20px 20px; text-align: center; color: white;">'
        )
        
        template_content = template_content.replace(
            '<div class="greeting-logo">',
            '<div style="font-size: 24px; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.5px;">'
        )
        
        template_content = template_content.replace(
            '<p class="greeting-subtitle">',
            '<p style="font-size: 14px; opacity: 0.9; margin: 0;">'
        )
        
        template_content = template_content.replace(
            '<div class="greeting-content">',
            '<div style="padding: 24px 20px 20px;">'
        )
        
        template_content = template_content.replace(
            '<div class="greeting-tips">',
            '<div style="background: #f0f9ff; border-radius: 6px; padding: 16px; margin: 20px 0; border-left: 3px solid #4f46e5;">'
        )
        
        template_content = template_content.replace(
            '<a href="https://skillzzy.com/dashboard" class="greeting-button">',
            '<a href="https://skillzzy.com/dashboard" style="display: inline-block; background: #4f46e5; color: white !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 16px; margin: 16px 0; width: auto; text-align: center;">'
        )
        
        template_content = template_content.replace(
            '<div class="greeting-footer">',
            '<div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">'
        )
        
        template_content = template_content.replace(
            '<p class="greeting-signature">',
            '<p style="color: #374151; font-weight: 600; margin: 20px 0 0;">'
        )
        
        # Style basic elements with mobile optimization
        template_content = template_content.replace('<h1>', '<h1 style="color: #1f2937; font-size: 20px; font-weight: 600; margin: 0 0 16px; text-align: center; line-height: 1.3;">')
        template_content = template_content.replace('<h3>', '<h3 style="color: #1f2937; font-size: 16px; font-weight: 600; margin: 0 0 12px; line-height: 1.3;">')
        template_content = template_content.replace('<p>', '<p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin: 0 0 16px;">')
        template_content = template_content.replace('<li>', '<li style="color: #374151; font-size: 14px; margin: 6px 0; line-height: 1.5;">')
        template_content = template_content.replace('<ul>', '<ul style="padding-left: 20px; margin: 12px 0;">')
        template_content = template_content.replace('<a href="mailto:', '<a style="color: #4f46e5; text-decoration: none; font-weight: 500; word-break: break-word;" href="mailto:')
        
        # Add body styling for mobile
        template_content = template_content.replace('<body>', '<body style="margin: 0; padding: 10px; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Arial, sans-serif; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;">')
        
        return template_content
    
    def list_available_templates(self) -> Dict[str, list]:
        """
        List all available templates and their languages.
        
        Returns:
            Dictionary with template names as keys and list of available languages as values
        """
        templates = {}
        
        if not os.path.exists(self.base_path):
            logger.warning(f"Templates directory not found: {self.base_path}")
            return templates
        
        try:
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                
                # Skip files, only process directories
                if os.path.isdir(item_path) and not item.startswith('.'):
                    languages = []
                    
                    # Check for language files in the template directory
                    for file in os.listdir(item_path):
                        if file.endswith('.html'):
                            language = file.replace('.html', '')
                            languages.append(language)
                    
                    if languages:
                        templates[item] = sorted(languages)
            
            logger.info(f"Found {len(templates)} available templates")
            return templates
            
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return templates