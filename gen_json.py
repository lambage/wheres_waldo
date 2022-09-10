import json
import pathlib


scenes = []
for file in pathlib.Path('data/scenes').glob('*'):
    if file.suffix in ['.png', '.jpg']:
        scenes.append({"filename": str(file), "waldo_location": {"x": 0, "y": 0, "width": 10, "height": 10}})


with open('data/scenes/scenes.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(scenes, ensure_ascii=False, indent="  "))

