"""Rename OSINT category titles to beginner-friendly labels."""
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parent.parent / "student.html"

TITLES = {
 "OSINT: Username": "Username Search",
 "OSINT: Email Address": "Email Search",
 "OSINT: Domain Name": "Domain Search",
 "OSINT: Cloud Infrastructure": "Cloud Infrastructure Search",
 "OSINT: IP & MAC Address": "IP Address Search",
 "OSINT: Images / Videos / Docs": "Image & Video Search",
 "OSINT: Social Networks": "Social Network Search",
 "OSINT: Instant Messaging": "Messaging Search",
 "OSINT: People Search Engines": "People Search",
 "OSINT: Dating": "Dating Search",
 "OSINT: Telephone Numbers": "Phone Number Search",
 "OSINT: Public Records": "Public Records Search",
 "OSINT: Compliance & Risk Intelligence": "Compliance & Risk Search",
 "OSINT: Business Records": "Business Records Search",
 "OSINT: Transportation": "Vehicle & Transport Search",
 "OSINT: Geolocation Tools / Maps": "Maps & Location Search",
 "OSINT: Search Engines": "Search Engines",
 "OSINT: Online Communities": "Forum & Community Search",
 "OSINT: Archives": "Web Archives",
 "OSINT: Language Translation": "Translation Tools",
 "OSINT: Mobile OSINT": "Mobile Search Tools",
 "OSINT: Dark Web": "Dark Web Search",
 "OSINT: Disinformation & Media Verification": "Fact-Check & Media Tools",
 "OSINT: Blockchain & Cryptocurrency": "Crypto Search",
 "OSINT: Classifieds": "Classifieds Search",
 "OSINT: Encoding / Decoding": "Encoding & Decoding Tools",
 "OSINT: Tools": "Research Toolkit",
 "OSINT: AI Tools": "AI Research Tools",
 "OSINT: Malicious File Analysis": "Malware & File Analysis",
 "OSINT: Cyber Threat Intelligence": "Threat Intelligence",
 "OSINT: OpSec": "Privacy & Safety Tools",
 "OSINT: Documentation / Evidence Capture": "Evidence Collection",
 "OSINT: Training": "Research Training",
}

BEGINNER_TITLES_BY_SOURCE = {
 "Username": "Username Search",
 "Email Address": "Email Search",
 "Domain Name": "Domain Search",
 "Cloud Infrastructure": "Cloud Infrastructure Search",
 "IP & MAC Address": "IP Address Search",
 "Images / Videos / Docs": "Image & Video Search",
 "Social Networks": "Social Network Search",
 "Instant Messaging": "Messaging Search",
 "People Search Engines": "People Search",
 "Dating": "Dating Search",
 "Telephone Numbers": "Phone Number Search",
 "Public Records": "Public Records Search",
 "Compliance & Risk Intelligence": "Compliance & Risk Search",
 "Business Records": "Business Records Search",
 "Transportation": "Vehicle & Transport Search",
 "Geolocation Tools / Maps": "Maps & Location Search",
 "Search Engines": "Search Engines",
 "Online Communities": "Forum & Community Search",
 "Archives": "Web Archives",
 "Language Translation": "Translation Tools",
 "Mobile OSINT": "Mobile Search Tools",
 "Dark Web": "Dark Web Search",
 "Disinformation & Media Verification": "Fact-Check & Media Tools",
 "Blockchain & Cryptocurrency": "Crypto Search",
 "Classifieds": "Classifieds Search",
 "Encoding / Decoding": "Encoding & Decoding Tools",
 "Tools": "Research Toolkit",
 "AI Tools": "AI Research Tools",
 "Malicious File Analysis": "Malware & File Analysis",
 "Cyber Threat Intelligence": "Threat Intelligence",
 "OpSec": "Privacy & Safety Tools",
 "Documentation / Evidence Capture": "Evidence Collection",
 "Training": "Research Training",
}


def beginner_title(source_name: str) -> str:
 return BEGINNER_TITLES_BY_SOURCE.get(source_name, source_name)


def main():
 text = HTML_PATH.read_text(encoding="utf-8")
 count = 0
 for old, new in TITLES.items():
 needle = f'<h3 class="category-title">{old}</h3>'
 repl = f'<h3 class="category-title">{new}</h3>'
 if needle in text:
 text = text.replace(needle, repl)
 count += 1
 HTML_PATH.write_text(text, encoding="utf-8", newline="\n")
 print(f"Updated {count} category titles.")


if __name__ == "__main__":
 main()
