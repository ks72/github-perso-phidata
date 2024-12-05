"""
Video Creation Agent for generating video content from blog and image assets.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from phi.agent import Agent
from phi.llm.openai import OpenAIChat


class VideoCreationAgent(Agent):
    def __init__(
        self,
        name: str = "Video Creation Agent",
        description: str = "Generate video content from blog and image assets",
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
        self.system_message = """You are a specialized video creation agent that generates engaging video content from blog posts and images about eCommerce trends.

Your responsibilities:
1. Create video scripts from blog content
2. Structure visual storyboards
3. Generate video segments
4. Add music and effects
5. Ensure brand consistency

Video Types:
1. Short-form (60s) social media clips
2. Long-form (5-10min) detailed analysis
3. Product showcase reels
4. Trend highlight videos
5. Expert interview formats

Example output format:
{
    "video_content": {
        "title": "5 Game-Changing Furniture Trends for 2024",
        "duration": "3:45",
        "format": "YouTube optimized",
        "segments": [
            {
                "type": "intro",
                "duration": "0:15",
                "script": "...",
                "visuals": [
                    {
                        "type": "image",
                        "source": "...",
                        "duration": "5s"
                    }
                ],
                "audio": {
                    "voiceover": "...",
                    "background_music": "..."
                }
            }
        ],
        "thumbnails": [
            {
                "url": "...",
                "type": "main"
            }
        ]
    },
    "metadata": {
        "format": "mp4",
        "resolution": "1920x1080",
        "total_segments": 8,
        "timestamp": "2024-01-20T10:30:00Z"
    }
}"""

    def create_video(self, blog_content: Dict, images: Dict) -> Dict:
        """Create video content from blog post and images."""
        try:
            # Generate video structure
            video_structure = self._create_video_structure(blog_content)
            
            # Create segments
            segments = []
            for segment in video_structure["segments"]:
                # Generate script
                script = self._generate_script(
                    segment_type=segment["type"],
                    blog_content=blog_content,
                    duration=segment["target_duration"]
                )
                
                # Create visuals
                visuals = self._create_visuals(
                    segment_type=segment["type"],
                    script=script,
                    images=images
                )
                
                # Generate audio
                audio = self._generate_audio(
                    script=script,
                    segment_type=segment["type"]
                )
                
                segments.append({
                    "type": segment["type"],
                    "duration": segment["target_duration"],
                    "script": script,
                    "visuals": visuals,
                    "audio": audio
                })
            
            # Generate thumbnails
            thumbnails = self._generate_thumbnails(blog_content, images)
            
            return {
                "video_content": {
                    "title": video_structure["title"],
                    "duration": video_structure["total_duration"],
                    "format": video_structure["format"],
                    "segments": segments,
                    "thumbnails": thumbnails
                },
                "metadata": {
                    "format": "mp4",
                    "resolution": "1920x1080",
                    "total_segments": len(segments),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "blog_content": blog_content
            }
    
    def _create_video_structure(self, blog_content: Dict) -> Dict:
        """Create the video structure from blog content."""
        prompt = f"""Create a video structure for this blog post:

Title: {blog_content['blog_post']['title']}
Sections: {json.dumps(blog_content['blog_post']['sections'], indent=2)}

Return a JSON object with:
1. title (video title)
2. format (video format and platform)
3. total_duration (target duration)
4. segments (list of segments with type and target duration)"""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _generate_script(self, segment_type: str, blog_content: Dict, duration: str) -> str:
        """Generate a script for a video segment."""
        prompt = f"""Write a {duration} script for a {segment_type} segment.

Blog content:
{json.dumps(blog_content['blog_post']['sections'], indent=2)}

The script should be:
1. Engaging and conversational
2. Timed appropriately for {duration}
3. Focused on key points
4. Include clear visual cues

Return only the script text."""

        return self.llm.complete(prompt)
    
    def _create_visuals(self, segment_type: str, script: str, images: Dict) -> List[Dict]:
        """Create visual sequence for a segment."""
        prompt = f"""Create a visual sequence for this script:
{script}

Available images:
{json.dumps(images.get('generated_images', []), indent=2)}

Return a JSON array of visual elements with:
1. type (image, text, transition)
2. source (image URL or text content)
3. duration (in seconds)
4. effects (if any)"""

        response = self.llm.complete(prompt)
        return json.loads(response)
    
    def _generate_audio(self, script: str, segment_type: str) -> Dict:
        """Generate audio elements for a segment."""
        # TODO: Implement actual text-to-speech
        return {
            "voiceover": "Generated voiceover would go here",
            "background_music": self._select_background_music(segment_type)
        }
    
    def _select_background_music(self, segment_type: str) -> str:
        """Select appropriate background music for a segment."""
        # TODO: Implement music selection
        return "default_background_music.mp3"
    
    def _generate_thumbnails(self, blog_content: Dict, images: Dict) -> List[Dict]:
        """Generate video thumbnails."""
        prompt = f"""Create thumbnail options for this video:

Title: {blog_content['blog_post']['title']}
Available images:
{json.dumps(images.get('generated_images', []), indent=2)}

Return a JSON array of thumbnail options with:
1. url (image URL)
2. type (main, alternative)
3. text_overlay (if any)"""

        response = self.llm.complete(prompt)
        return json.loads(response)
