"""
Library:     lib_av_manager.py
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
"""
"""
Library:     lib_av_manager.py
Family:      System
Jurisdiction: ["PYTHON", "BEJSON_LIBRARIES"]
Status:      OFFICIAL
Author:      Elton Boehnen
Version:     1.5 OFFICIAL
Date:        2026-05-01
Description: Enhanced AV management with Base64 encoding, slideshow generation,
             and optimized space-saving splitting logic.
"""
import os
import subprocess
import json
import base64

class AVManager:
    def __init__(self, ffmpeg_path="ffmpeg"):
        self.ffmpeg = ffmpeg_path

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr
            return True, result.stdout
        except Exception as e:
            return False, str(e)

    def get_info(self, input_file):
        cmd = f"ffprobe -v quiet -print_format json -show_format -show_streams \"{input_file}\""
        success, output = self.run_command(cmd)
        if success:
            return json.loads(output)
        return None

    def process_with_preset(self, input_file, output_file, preset):
        info = self.get_info(input_file)
        if not info: return False, "Could not probe file."
        
        has_video = any(s.get("codec_type") == "video" for s in info.get("streams", []))
        v_codec = preset.get("v_codec", "libx264")
        a_codec = preset.get("a_codec", "copy")
        crf = preset.get("crf")
        scale = preset.get("scale")
        extra = preset.get("extra", "")
        
        args = []
        if has_video:
            args.append(f"-c:v {v_codec}")
            if crf: args.append(f"-crf {crf}")
            if scale: args.append(f"-vf scale={scale}")
        
        args.append(f"-c:a {a_codec}")
        if extra: args.append(extra)
        
        cmd = f"{self.ffmpeg} -y -i \"{input_file}\" {' '.join(args)} \"{output_file}\""
        return self.run_command(cmd)

    def split_file(self, input_file, output_pattern, segment_time=300):
        """Splits file into N-minute segments (default 5m/300s)."""
        cmd = f"{self.ffmpeg} -y -i \"{input_file}\" -f segment -segment_time {segment_time} -reset_timestamps 1 -c copy \"{output_pattern}\""
        return self.run_command(cmd)

    def to_base64(self, input_file):
        """Converts file to a Base64 string."""
        try:
            with open(input_file, "rb") as f:
                return True, base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return False, str(e)

    def create_slideshow(self, image_file, audio_file, output_file, preset):
        """Combines a static image and audio into a space-efficient video."""
        v_codec = preset.get("v_codec", "libx264")
        a_codec = preset.get("a_codec", "aac")
        crf = preset.get("crf", 30)
        scale = preset.get("scale", "854:480") # Default to 480p for space
        
        # Loop image to match audio duration
        cmd = f"{self.ffmpeg} -y -loop 1 -i \"{image_file}\" -i \"{audio_file}\" -c:v {v_codec} -crf {crf} -vf \"scale={scale},format=yuv420p\" -c:a {a_codec} -shortest \"{output_file}\""
        return self.run_command(cmd)

if __name__ == "__main__":
    print("AV Manager Library - v1.4 OFFICIAL")
