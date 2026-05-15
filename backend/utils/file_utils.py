import os
import shutil

def cleanup_files(*file_paths):
    """Utility to clean up intermediate files to save disk space."""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                # We could log this, but ignoring for basic cleanup
                pass
