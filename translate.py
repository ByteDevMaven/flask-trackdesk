import asyncio
import sys
from googletrans import Translator
import re

# Get the target language from the command line
if len(sys.argv) < 2:
    print("Usage: python translate.py <language_code>")
    sys.exit(1)

language = sys.argv[1] or "es"
file_name = f"./translations/{language}/LC_MESSAGES/messages.po"

translator = Translator()

async def main():
    # Load file
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    translated_lines = []
    current_msgid = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            translated_lines.append(line)
        elif stripped.startswith("msgid"):
            match = re.match(r'msgid\s+"(.*)"', line)
            current_msgid = match.group(1) if match else ""
            translated_lines.append(line)

        elif stripped.startswith("msgstr"):
            if current_msgid:
                translated = await translator.translate(current_msgid, dest=language)
                translated_text = translated.text
            else:
                translated_text = ""
            translated_lines.append(f'msgstr "{translated_text}"\n')

        else:
            translated_lines.append(line)

    # Save translated file
    with open(file_name, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print("Translation complete.")

# Run the async main
asyncio.run(main())