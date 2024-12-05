"""
Blog Writer Agent for generating blog content from processed data.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
from phi.agent import Agent
from phi.llm.openai import OpenAIChat


class BlogWriterAgent(Agent):
    def __init__(
        self,
        name: str = "Blog Writer Agent",
        description: str = "Generate engaging blog content from processed data",
        llm: Optional[OpenAIChat] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=description,
            llm=llm or OpenAIChat(model="gpt-4"),
            **kwargs,
        )
        
        # Set the system message
        self.system_message = """You are a specialized blog writing agent that creates engaging content from processed eCommerce trend data.

Your responsibilities:
1. Analyze processed content from multiple sources
2. Structure information into a cohesive narrative
3. Write engaging, SEO-friendly blog posts
4. Include proper citations and sources
5. Suggest relevant images and media

Blog Structure:
1. Attention-grabbing headline
2. Engaging introduction
3. Key trend insights
4. Supporting data and examples
5. Industry impact analysis
6. Future predictions
7. Actionable takeaways
8. Conclusion with call-to-action

Example output format:
{
    "blog_post": {
        "title": "10 Game-Changing Furniture Trends Reshaping Home Design in 2024",
        "meta_description": "Discover the latest furniture trends...",
        "sections": [
            {
                "type": "introduction",
                "content": "..."
            }
        ],
        "image_suggestions": [
            {
                "section": "introduction",
                "image_url": "...",
                "caption": "..."
            }
        ],
        "sources": [
            {
                "url": "...",
                "title": "...",
                "cited_for": "..."
            }
        ]
    },
    "metadata": {
        "word_count": 1500,
        "reading_time": "7 minutes",
        "target_keywords": ["..."],
        "timestamp": "2024-01-20T10:30:00Z"
    }
}"""

    def generate_blog(self, processed_data: Dict, query_context: Dict) -> Dict:
        """Generate a blog post from processed data."""
        try:
            # Extract key information
            focus = query_context["components"]["focus"]
            context = query_context["components"]["context"]
            scope = query_context["components"]["scope"]
            
            # Combine all source content
            source_content = []
            for content in processed_data.get("processed_content", []):
                source_content.append({
                    "title": content["title"],
                    "main_text": content["main_text"],
                    "key_points": content["key_points"],
                    "url": content["url"]
                })
            
            # Generate blog structure
            blog_structure = self._create_blog_structure(
                focus=focus,
                context=context,
                scope=scope,
                sources=source_content
            )
            
            # Write each section
            sections = []
            for section in blog_structure["sections"]:
                section_content = self._write_section(
                    section_type=section["type"],
                    section_focus=section["focus"],
                    sources=source_content
                )
                sections.append(section_content)
            
            # Compile final blog post
            blog_post = {
                "title": blog_structure["title"],
                "meta_description": blog_structure["meta_description"],
                "sections": sections,
                "image_suggestions": self._suggest_images(processed_data, sections),
                "sources": self._format_sources(source_content)
            }
            
            # Calculate metadata
            word_count = sum(len(s["content"].split()) for s in sections)
            reading_time = max(1, round(word_count / 200))  # Assume 200 words per minute
            
            return {
                "blog_post": blog_post,
                "metadata": {
                    "word_count": word_count,
                    "reading_time": f"{reading_time} minutes",
                    "target_keywords": blog_structure["keywords"],
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "data": processed_data
            }
    
    def _create_blog_structure(self, focus: str, context: Dict, scope: List[str], sources: List[Dict]) -> Dict:
        """Create the blog post structure."""
        prompt = f"""Create a blog post structure for:
Focus: {focus}
Context: {json.dumps(context)}
Scope: {', '.join(scope)}

Return a JSON object with:
1. title
2. meta_description
3. sections (list of section types and their focus)
4. target keywords

Use the source material themes:
{json.dumps([s['title'] for s in sources], indent=2)}"""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _write_section(self, section_type: str, section_focus: str, sources: List[Dict]) -> Dict:
        """Write a single blog section."""
        prompt = f"""Write a {section_type} section about {section_focus}.

Use these sources:
{json.dumps([{
    'title': s['title'],
    'key_points': s['key_points']
} for s in sources], indent=2)}

Return a JSON object with:
1. type: section type
2. content: the written content
3. sources_used: list of source URLs used"""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _suggest_images(self, processed_data: Dict, sections: List[Dict]) -> List[Dict]:
        """Suggest images for each section."""
        suggestions = []
        available_images = []
        
        # Collect all available images
        for content in processed_data.get("processed_content", []):
            available_images.extend(content.get("images", []))
        
        # Match images to sections
        for section in sections:
            relevant_images = self._find_relevant_images(
                section["content"],
                available_images
            )
            if relevant_images:
                suggestions.append({
                    "section": section["type"],
                    "images": relevant_images[:2]  # Suggest up to 2 images per section
                })
        
        return suggestions
    
    def _find_relevant_images(self, content: str, images: List[Dict]) -> List[Dict]:
        """Find images relevant to the content."""
        prompt = f"""Find relevant images for this content:
{content[:500]}...

Available images:
{json.dumps(images, indent=2)}

Return a JSON array of image objects that would best illustrate this content."""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _format_sources(self, sources: List[Dict]) -> List[Dict]:
        """Format sources for citation."""
        formatted_sources = []
        for source in sources:
            formatted_sources.append({
                "url": source["url"],
                "title": source["title"],
                "cited_for": self._extract_citation_context(source)
            })
        return formatted_sources
    
    def _extract_citation_context(self, source: Dict) -> str:
        """Extract the main points for which a source was cited."""
        key_points = source.get("key_points", [])
        if key_points:
            return "; ".join(key_points[:3])  # Top 3 key points
        return "General information and context"
