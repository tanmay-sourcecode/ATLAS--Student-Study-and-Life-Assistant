import os
import re

SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")

def load_skill(skill_name: str) -> dict:
    """
    Dynamically loads and parses a skill's SKILL.md file.
    Implements progressive disclosure: keeps context light until specific skill is active.
    
    Returns:
        dict: A dictionary containing 'name', 'description', and 'instructions'.
    """
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    
    if not os.path.exists(skill_path):
        return {
            "name": skill_name,
            "description": f"Skill {skill_name} description not found.",
            "instructions": ""
        }
        
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse YAML frontmatter (between --- separators)
        frontmatter = {}
        instructions = content
        
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            yaml_block = match.group(1)
            instructions = match.group(2).strip()
            
            # Simple YAML-like parsing for name and description
            for line in yaml_block.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    frontmatter[key.strip().lower()] = val.strip().strip('"').strip("'")
                    
        return {
            "name": frontmatter.get("name", skill_name),
            "description": frontmatter.get("description", "No description provided."),
            "instructions": instructions
        }
    except Exception as e:
        return {
            "name": skill_name,
            "description": f"Error loading skill: {str(e)}",
            "instructions": ""
        }

def list_available_skills() -> list:
    """Lists all skills available under the skills/ directory by scanning subfolders."""
    if not os.path.exists(SKILLS_DIR):
        return []
        
    skills = []
    for entry in os.listdir(SKILLS_DIR):
        entry_path = os.path.join(SKILLS_DIR, entry)
        if os.path.isdir(entry_path) and os.path.exists(os.path.join(entry_path, "SKILL.md")):
            # Load metadata only (progressive disclosure - level 1)
            metadata = load_skill(entry)
            skills.append({
                "id": entry,
                "name": metadata["name"],
                "description": metadata["description"]
            })
    return skills
