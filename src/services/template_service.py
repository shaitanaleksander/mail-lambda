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
            
            # Use string format to replace placeholders
            rendered_content = template_content.format(**processed_data)
            
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