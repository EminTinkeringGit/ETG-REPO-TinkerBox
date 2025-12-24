import os
from pathlib import Path
from collections import defaultdict, Counter

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
    # Map EXIF tag ids to names
    EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}
except Exception:
    PIL_AVAILABLE = False
    EXIF_TAGS = {}


def analyze_directory(path):
    """Analyze directory structure, file statistics, and capture info heuristics.

    The function collects basic file-type counts and a lightweight "capture info"
    summary using EXIF (when available) and filename/path heuristics to infer
    whether media came from a phone, camera, screenshot, or was forwarded via
    messaging/email apps.
    """
    if not os.path.isdir(path):
        print(f"Error: {path} is not a valid directory")
        return

    image_exts = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.gif', '.webp'}
    video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.3gp'}

    file_stats = defaultdict(int)
    total_files = 0

    # capture-related stats
    source_counts = Counter()        # phone / camera / screenshot / unknown
    camera_models = Counter()        # "Make Model" -> count
    app_sources = Counter()          # apps or software (WhatsApp, Instagram, Gmail...)
    path_hints = Counter()           # folder-name hints like 'WhatsApp', 'Email'

    phone_makers = {"Apple", "Samsung", "Google", "Huawei", "Xiaomi",
                    "Sony", "LG", "Motorola", "OnePlus", "Nokia"}

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(path):
        root_lower = root.lower()
        for file in files:
            total_files += 1
            # Get file extension
            _, ext = os.path.splitext(file)
            ext = ext.lower() if ext else "no extension"
            file_stats[ext] += 1

            # Only attempt capture heuristics for likely media
            full_path = os.path.join(root, file)
            fname_lower = file.lower()

            # Path/dir hints
            for hint in ("whatsapp", "telegram", "snapchat", "email", "downloads", "dcim", "screenshots"):
                if hint in root_lower or hint in fname_lower:
                    path_hints[hint] += 1

            # Filename patterns
            if any(s in fname_lower for s in ("screenshot", "screen_shot", "screen-shot", "screen shot")):
                source_counts['screenshot'] += 1
                continue

            # If image, try reading EXIF
            if ext in image_exts and PIL_AVAILABLE:
                try:
                    with Image.open(full_path) as img:
                        exif = img._getexif() or {}
                except Exception:
                    exif = {}

                make = None
                model = None
                software = None
                # Normalize tag access
                if exif:
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == 'Camera Maker' and isinstance(value, str):
                            make = value.strip()
                        elif tag == 'Model' and isinstance(value, str):
                            model = value.strip()
                        elif tag == 'Software' and isinstance(value, str):
                            software = value.strip()
                        elif tag in ('ImageDescription', 'UserComment', 'Artist') and isinstance(value, str):
                            # small chance these include forwarded/app info
                            vlow = value.lower()
                            if 'whatsapp' in vlow:
                                app_sources['whatsapp'] += 1
                            if 'instagram' in vlow:
                                app_sources['instagram'] += 1

                if make or model:
                    key = f"{make or ''} {model or ''}".strip()
                    camera_models[key] += 1
                    # classify phone vs camera by make
                    maker_label = make.split()[0] if make else ''
                    if any(pm.lower() in maker_label.lower() for pm in phone_makers):
                        source_counts['phone'] += 1
                    else:
                        source_counts['camera'] += 1
                elif ext in image_exts and not exif:
                    # fallback heuristics for images without exif
                    if fname_lower.startswith('img_') or fname_lower.startswith('vid_') or fname_lower.startswith('dsf') or 'dcim' in root_lower:
                        source_counts['phone'] += 1
                    else:
                        source_counts['unknown'] += 1

                if software:
                    s = software.lower()
                    if 'whatsapp' in s:
                        app_sources['whatsapp'] += 1
                    elif 'instagram' in s:
                        app_sources['instagram'] += 1
                    elif 'snapchat' in s:
                        app_sources['snapchat'] += 1
                    elif any(k in s for k in ('gmail', 'outlook', 'hotmail', 'yahoo', 'mail')):
                        app_sources['email'] += 1
                    else:
                        app_sources[software] += 1

            elif ext in video_exts:
                # video heuristics: filenames, parent dirs, and common prefixes
                if fname_lower.startswith('vid_') or fname_lower.startswith('img_') or 'dcim' in root_lower:
                    source_counts['phone'] += 1
                elif any(k in fname_lower for k in ('screen', 'screenshot', 'screenrecord')):
                    source_counts['screenshot'] += 1
                else:
                    source_counts['unknown'] += 1
            else:
                # non-media files don't contribute to capture heuristics
                pass

    # Display results
    print(f"\n{'='*50}")
    print(f"Directory Analysis: {path}")
    print(f"{'='*50}")
    print(f"Total Files: {total_files}\n")
    print(f"File Types: {len(file_stats)}\n")
    print("Files by Type:")
    print("-" * 50)

    for ext in sorted(file_stats.keys(), key=lambda x: file_stats[x], reverse=True):
        count = file_stats[ext]
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"{ext:20} : {count:6} files ({percentage:5.1f}%)")

    # Capture info summary
    print(f"\n{'='*50}")
    print("Capture Info Summary")
    print("-" * 50)
    # Source counts
    total_captures = sum(source_counts.values())
    print(f"Total Media With Capture Hints: {total_captures}")
    for k, v in source_counts.most_common():
        pct = (v / total_captures * 100) if total_captures > 0 else 0
        print(f"{k:12} : {v:6} ({pct:5.1f}%)")

    # Top camera makes/models
    if camera_models:
        print("\nTop Camera/Device Makes & Models:")
        for k, v in camera_models.most_common(8):
            print(f"{k:30} : {v}")
    else:
        print("\nNo camera/make/model EXIF information found.")

    # App/software sources
    if app_sources:
        print("\nDetected Apps / Software (possible forwards or edits):")
        for k, v in app_sources.most_common(8):
            print(f"{k:20} : {v}")

    # Path hints
    if path_hints:
        print("\nPath/Folder Hints:")
        for k, v in path_hints.most_common(8):
            print(f"{k:12} : {v}")

    print(f"{'='*50}\n")

# Usage
if __name__ == "__main__":
    path = r'C:\Users\sayed\Documents\MEDIA' #input("Enter directory path: ")
    analyze_directory(path)