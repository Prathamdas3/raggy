from typing import Tuple
from app.core import get_logger

logger=get_logger(__name__)

def parse_title_and_summary(content: str) -> Tuple[str, str]:
    """
    Parse title and summary from formatted response
    
    Args:
        content: Response content in format "TITLE: ...\nSUMMARY: ..."
    
    Returns:
        Tuple[str, str]: (title, summary)
        
    Raises:
        ValueError: If content cannot be parsed
    """
    title = ""
    summary = ""
    
    # Try to find TITLE: and SUMMARY: markers (case-insensitive)
    content_upper = content.upper()
    
    if "TITLE:" in content_upper and "SUMMARY:" in content_upper:
        title_start = content_upper.find("TITLE:")
        summary_start = content_upper.find("SUMMARY:")
        
        if title_start < summary_start:
            # Extract title (skip "TITLE:" prefix)
            title = content[title_start + 6 : summary_start].strip()
            # Extract summary (skip "SUMMARY:" prefix)
            summary = content[summary_start + 8 :].strip()
            
            # Clean up common artifacts
            title = title.strip('*"\'').strip()
            summary = summary.strip('*"\'').strip()
            
            if not title or not summary:
                raise ValueError("Title or summary is empty after parsing")
            
            logger.debug(f"Successfully parsed - Title: {title[:50]}..., Summary: {len(summary)} chars")
            return title, summary
        else:
            raise ValueError("Title and summary markers in wrong order")
    else:
        missing = []
        if "TITLE:" not in content_upper:
            missing.append("TITLE:")
        if "SUMMARY:" not in content_upper:
            missing.append("SUMMARY:")
        raise ValueError(f"Missing markers: {', '.join(missing)}")