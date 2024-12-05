"""Tools for generating various types of content."""
from typing import Dict, Any, List, Optional
import os
import json
from openai import OpenAI

class ContentGenerationTool:
    """Tool for generating various types of content using OpenAI's APIs."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def generate_blog_post(self, topic: str, research_data: List[Dict[str, Any]], 
                          style: str = "informative", max_length: int = 1000) -> Dict[str, Any]:
        """
        Generate a blog post from research data.
        
        Args:
            topic: The main topic of the blog post
            research_data: List of dictionaries containing research information
            style: Writing style to use (e.g., "informative", "casual", "professional")
            max_length: Maximum length of the blog post in words
            
        Returns:
            Dictionary containing the generated blog post content and metadata
        """
        try:
            # Prepare the prompt
            prompt = self._prepare_blog_prompt(topic, research_data, style, max_length)
            
            # Generate the blog post
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional blog writer specializing in e-commerce trends."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract and structure the content
            content = response.choices[0].message.content
            
            return {
                'topic': topic,
                'content': content,
                'style': style,
                'word_count': len(content.split())
            }
        except Exception as e:
            print(f"Error generating blog post: {str(e)}")
            return {'error': str(e)}
            
    def generate_image_prompt(self, context: str, style: str = "digital art") -> str:
        """
        Generate an image prompt for DALL-E based on context.
        
        Args:
            context: The context to base the image on
            style: The desired art style
            
        Returns:
            A detailed prompt for image generation
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed image generation prompts."},
                    {"role": "user", "content": f"Create a detailed DALL-E prompt for an image about: {context}. Style: {style}"}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating image prompt: {str(e)}")
            return ""
            
    def generate_image(self, prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
        """
        Generate an image using DALL-E.
        
        Args:
            prompt: The image generation prompt
            size: Size of the image to generate
            
        Returns:
            Dictionary containing the generated image URL and metadata
        """
        try:
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size=size
            )
            
            return {
                'url': response.data[0].url,
                'prompt': prompt,
                'size': size
            }
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return {'error': str(e)}
            
    def generate_video_script(self, blog_content: str, duration: int = 60) -> Dict[str, Any]:
        """
        Generate a video script from blog content.
        
        Args:
            blog_content: The blog post content to convert
            duration: Target duration in seconds
            
        Returns:
            Dictionary containing the script segments and metadata
        """
        try:
            prompt = f"""Create a video script from this blog content that will be approximately {duration} seconds long.
            Include segments with timing, narration text, and visual descriptions.
            Blog content: {blog_content}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional video script writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'script': response.choices[0].message.content,
                'duration': duration,
                'source_content': blog_content[:100] + "..."  # Truncated for brevity
            }
        except Exception as e:
            print(f"Error generating video script: {str(e)}")
            return {'error': str(e)}
            
    def _prepare_blog_prompt(self, topic: str, research_data: List[Dict[str, Any]], 
                           style: str, max_length: int) -> str:
        """Prepare a detailed prompt for blog post generation."""
        research_summary = "\n".join([
            f"- {item.get('title', '')}: {item.get('snippet', '')}"
            for item in research_data[:5]  # Use top 5 research items
        ])
        
        return f"""Write a {style} blog post about {topic}.
        Maximum length: {max_length} words
        
        Research data to incorporate:
        {research_summary}
        
        The blog post should be engaging, well-structured, and include:
        1. An attention-grabbing introduction
        2. Main points supported by the research data
        3. Practical insights or takeaways
        4. A conclusion that summarizes key points
        
        Style guide:
        - Tone: {style}
        - Use subheadings to organize content
        - Include relevant statistics and examples
        - Make it actionable for readers
        """
