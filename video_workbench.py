import os
import torch
import numpy as np
import random

# Try to import moviepy
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
except ImportError:
    print("❌ Error: 'moviepy' is not installed. Please run: pip install moviepy")

class AutoEditWorkbench:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory_path": ("STRING", {"default": "./input/my_footage", "multiline": False}),
                "sort_strategy": (["alphabetical_asc", "alphabetical_desc", "date_oldest", "date_newest", "random"],),
                
                # --- RESOLUTION SETTINGS ---
                "resolution_strategy": (["First Video", "Smallest (Min Area)", "Largest (Max Area)", "Custom"], {"default": "First Video"}),
                "custom_width": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                "custom_height": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                
                # --- FPS SETTINGS ---
                "fps_strategy": (["First Video", "Lowest FPS", "Highest FPS", "Custom"], {"default": "First Video"}),
                "custom_fps": ("INT", {"default": 24, "min": 1, "max": 120, "step": 1}),
                
                # --- LIMITS ---
                "limit_duration_sec": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO")
    RETURN_NAMES = ("images", "audio")
    FUNCTION = "process_workbench"
    CATEGORY = "VideoTools/Editing"

    def process_workbench(self, directory_path, sort_strategy, 
                          resolution_strategy, custom_width, custom_height, 
                          fps_strategy, custom_fps, 
                          limit_duration_sec):
        
        # --- 1. Validation ---
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        valid_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
        files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
                 if f.lower().endswith(valid_extensions)]

        if not files:
            raise ValueError("No video files found in the directory.")

        # Sorting
        if sort_strategy == "alphabetical_asc": files.sort()
        elif sort_strategy == "alphabetical_desc": files.sort(reverse=True)
        elif sort_strategy == "date_oldest": files.sort(key=os.path.getmtime)
        elif sort_strategy == "date_newest": files.sort(key=os.path.getmtime, reverse=True)
        elif sort_strategy == "random": random.shuffle(files)

        # --- 2. Strategy Analysis (Resolution & FPS) ---
        target_w, target_h = custom_width, custom_height
        target_fps = custom_fps
        
        # Helper to read metadata quickly
        def get_meta(p):
            try:
                with VideoFileClip(p) as c: return {'w': c.w, 'h': c.h, 'fps': c.fps, 'area': c.w*c.h}
            except: return None

        # Check if we need to scan all files
        need_scan = (resolution_strategy not in ["Custom", "First Video"]) or (fps_strategy not in ["Custom", "First Video"])
        
        # Optimization: Apply "First Video" immediately without scanning everything if possible
        if resolution_strategy == "First Video" or fps_strategy == "First Video":
            m = get_meta(files[0])
            if m:
                if resolution_strategy == "First Video": target_w, target_h = m['w'], m['h']
                if fps_strategy == "First Video": target_fps = m['fps']

        # Full scan if needed (Min/Max strategies)
        if need_scan:
            stats = [m for f in files if (m := get_meta(f))]
            if stats:
                if resolution_strategy == "Smallest (Min Area)":
                    s = min(stats, key=lambda x: x['area'])
                    target_w, target_h = s['w'], s['h']
                elif resolution_strategy == "Largest (Max Area)":
                    l = max(stats, key=lambda x: x['area'])
                    target_w, target_h = l['w'], l['h']
                
                if fps_strategy == "Lowest FPS":
                    target_fps = min(stats, key=lambda x: x['fps'])['fps']
                elif fps_strategy == "Highest FPS":
                    target_fps = max(stats, key=lambda x: x['fps'])['fps']

        print(f"🎯 [AutoEdit] Target: {target_w}x{target_h} @ {target_fps:.2f} fps")

        # --- 3. Clip Processing ---
        clips = []
        for file in files:
            try:
                clip = VideoFileClip(file)
                # Aspect Fill / Center Crop Logic
                ratio_target = target_w / target_h
                ratio_clip = clip.w / clip.h
                
                if ratio_clip > ratio_target:
                    # Clip is wider -> Resize Height, Crop Width
                    clip = clip.resize(height=target_h)
                    clip = clip.crop(x1=clip.w/2 - target_w/2, width=target_w)
                else:
                    # Clip is taller -> Resize Width, Crop Height
                    clip = clip.resize(width=target_w)
                    clip = clip.crop(y1=clip.h/2 - target_h/2, height=target_h)
                
                # Finalize
                clip = clip.resize((target_w, target_h))
                clip = clip.set_fps(target_fps)
                clips.append(clip)
            except Exception as e:
                print(f"⚠️ Warning: Skipped {file}. Reason: {e}")

        if not clips:
            raise ValueError("No valid clips could be processed.")

        # --- 4. Concatenation ---
        final_clip = concatenate_videoclips(clips, method="compose")

        # Duration Limit
        if limit_duration_sec > 0 and final_clip.duration > limit_duration_sec:
            final_clip = final_clip.subclip(0, limit_duration_sec)

        # --- 5. Export Video (Tensor) ---
        print("⏳ [AutoEdit] Converting video frames to Tensor...")
        frames = [frame for frame in final_clip.iter_frames()]
        video_np = np.stack(frames)
        video_tensor = torch.from_numpy(video_np).float() / 255.0
        
        # --- 6. Export Audio (Tensor) ---
        audio_dict = None
        if final_clip.audio is not None:
            sr = 44100
            print(f"🔊 [AutoEdit] Processing Audio (Duration: {final_clip.duration}s)...")
            
            try:
                # Sync duration to prevent errors
                final_clip.audio = final_clip.audio.set_duration(final_clip.duration)
                
                # Iterate by 1-second chunks to avoid MemoryError and Numpy compatibility issues
                audio_chunks = []
                for chunk in final_clip.audio.iter_chunks(fps=sr, chunk_duration=1.0):
                    audio_chunks.append(chunk)
                
                if len(audio_chunks) > 0:
                    audio_np = np.vstack(audio_chunks)
                    
                    # Ensure correct shape for ComfyUI
                    if len(audio_np.shape) == 1: # Mono
                        audio_np = audio_np.reshape((-1, 1))
                    
                    # (Samples, Channels) -> (1, Channels, Samples)
                    audio_tensor = torch.from_numpy(audio_np.T).float().unsqueeze(0)
                    audio_dict = {"waveform": audio_tensor, "sample_rate": sr}
                    print("✅ [AutoEdit] Audio ready.")
                else:
                    print("⚠️ [AutoEdit] Audio track was empty.")
                    
            except Exception as e:
                print(f"❌ [AutoEdit] Audio Error: {e}")
        
        # Cleanup resources
        final_clip.close()
        for c in clips: c.close()

        return (video_tensor, audio_dict)

# Mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "AutoEditWorkbench": AutoEditWorkbench
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoEditWorkbench": "🎬 Auto-Edit Workbench"
}