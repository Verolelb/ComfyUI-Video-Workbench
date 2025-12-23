\# 🎬 ComfyUI Video Workbench



A powerful Custom Node for ComfyUI that acts as a \*\*mini video editing workbench\*\*. 

It automatically assembles (concatenates) multiple video clips from a folder into a single sequence, handling resolution resizing (crop/fill) and FPS matching intelligently.



\## ✨ Features



\*   \*\*Batch Assembly\*\*: Loads all video files from a specified folder.

\*   \*\*Smart Resizing\*\*: Automatically handles mixed aspect ratios (Vertical TikToks + Horizontal YouTube).

&nbsp;   \*   \*Center Crop / Aspect Fill logic included.\*

\*   \*\*Intelligent Strategies\*\*:

&nbsp;   \*   \*\*Resolution\*\*: Can adapt to the \*First Video\*, the \*Smallest\*, the \*Largest\*, or a \*Custom\* size.

&nbsp;   \*   \*\*FPS\*\*: Can adapt to the \*First Video\*, \*Lowest\*, \*Highest\*, or \*Custom\*.

\*   \*\*Audio Support\*\*: Concatenates audio tracks perfectly.

\*   \*\*Safety Limits\*\*: Duration limit parameter to prevent Out-Of-Memory errors during testing.



\## 📦 Installation



\### Method 1: ComfyUI Manager (Recommended)

1\.  Install \[ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager).

2\.  Search for "Video Workbench" (once indexed) or "Install via Git URL".

3\.  Paste this repository URL.



\### Method 2: Manual

1\.  Go to your `ComfyUI/custom\_nodes/` directory.

2\.  Clone this repo:

&nbsp;   ```bash

&nbsp;   git clone https://github.com/Verolelb/ComfyUI-Video-Workbench.git

&nbsp;   ```

3\.  Install dependencies:

&nbsp;   ```bash

&nbsp;   pip install -r requirements.txt

&nbsp;   ```



\## 🛠️ How to use



1\.  \*\*Directory Path\*\*: Paste the absolute path to your folder containing video clips (e.g., `C:/Users/You/Videos/Vacation`).

2\.  \*\*Sort Strategy\*\*: Choose how to order the clips (Alphabetical, Date, Random).

3\.  \*\*Resolution \& FPS Strategy\*\*:

&nbsp;   \*   Leave on \*\*"First Video"\*\* to let the first clip dictate the settings for the whole timeline.

&nbsp;   \*   Use \*\*"Custom"\*\* to force specific dimensions (e.g., 1080x1920).



\## ❤️ Credits



Created by \*\*Verolelb\*\*.

Powered by \[MoviePy](https://zulko.github.io/moviepy/).

