"""
Image Creation Agent for generating visuals from blog content.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from phi.agent import Agent
from phi.llm.openai import OpenAIChat


class ImageCreationAgent(Agent):
    def __init__(
        self,
        name: str = "Image Creation Agent",
        description: str = "Generate visuals for blog content",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Initialize API key
        self.dalle_api_key = os.getenv("OPENAI_API_KEY")
        if not self.dalle_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Set the system message
        self.system_message = """You are a specialized image creation agent that generates visuals for blog content about eCommerce trends.

Your responsibilities:
1. Analyze blog content to identify image needs
2. Generate appropriate prompts for DALL-E
3. Create visually appealing and relevant images
4. Ensure brand safety and style consistency
5. Optimize images for web use

Image Types:
1. Hero images for headers
2. Section illustrations
3. Data visualizations
4. Product mockups
5. Trend collages

Example output format:
{
    "generated_images": [
        {
            "section": "introduction",
            "type": "hero",
            "prompt": "Modern minimalist living room with sustainable furniture...",
            "style": "photorealistic",
            "dimensions": "1920x1080",
            "image_url": "...",
            "alt_text": "..."
        }
    ],
    "metadata": {
        "total_images": 5,
        "styles_used": ["photorealistic", "flat design"],
        "timestamp": "2024-01-20T10:30:00Z"
    }
}"""

    def generate_images(self, blog_content: Dict) -> Dict:
        """Generate images for blog content."""
        try:
            # Extract image needs from blog content
            image_needs = self._analyze_image_needs(blog_content)
            
            # Generate images for each need
            generated_images = []
            styles_used = set()
            
            for need in image_needs:
                # Generate DALL-E prompt
                prompt = self._generate_prompt(
                    section_type=need["section"],
                    content=need["content"],
                    style=need["style"]
                )
                
                # Call DALL-E API (mocked for now)
                image_url = self._generate_image(prompt, need["dimensions"])
                
                # Store result
                generated_images.append({
                    "section": need["section"],
                    "type": need["type"],
                    "prompt": prompt,
                    "style": need["style"],
                    "dimensions": need["dimensions"],
                    "image_url": image_url,
                    "alt_text": need["alt_text"]
                })
                
                styles_used.add(need["style"])
            
            return {
                "generated_images": generated_images,
                "metadata": {
                    "total_images": len(generated_images),
                    "styles_used": list(styles_used),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "blog_content": blog_content
            }
    
    def _analyze_image_needs(self, blog_content: Dict) -> List[Dict]:
        """Analyze blog content to determine image needs."""
        prompt = f"""Analyze this blog content and determine image needs:

Title: {blog_content['blog_post']['title']}
Sections: {json.dumps(blog_content['blog_post']['sections'], indent=2)}

Return a JSON array of image needs with:
1. section (which section needs the image)
2. type (hero, illustration, etc.)
3. style (photorealistic, flat design, etc.)
4. dimensions (size based on type)
5. alt_text (accessibility description)
6. content (key elements to include)"""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _generate_prompt(self, section_type: str, content: str, style: str) -> str:
        """Generate a DALL-E prompt for the image."""
        prompt = f"""Create a DALL-E prompt for:
Section type: {section_type}
Content focus: {content}
Style: {style}

The prompt should be detailed and specific, including:
1. Main subject matter
2. Style and mood
3. Colors and lighting
4. Composition
5. Any specific details

Return only the prompt text."""

        return self.llm.complete(prompt)
    
    def _generate_image(self, prompt: str, dimensions: str) -> str:
        """Generate an image using DALL-E (mocked for now)."""
        # TODO: Implement actual DALL-E API call
        # For now, return a placeholder URL
        width, height = map(int, dimensions.split("x"))
        return f"https://via.placeholder.com/{width}x{height}"
    
    def optimize_image(self, image_url: str, target_size: str) -> str:
        """Optimize an image for web use."""
        # TODO: Implement image optimization
        # For now, return the original URL
        return image_url
