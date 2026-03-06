# Modrinth Modpack Manager & Changelog Generator

A professional desktop application built with Python and PyQt6 designed to streamline the management of Minecraft modpacks. It allows creators to automatically compare different versions of `.mrpack` files and generate clean, formatted Markdown changelogs or full mod lists in seconds.

![1772814276018](images/readme/1772814276018.avif)

![1772814317296](images/readme/1772814317296.avif)

## Features

- **Dual Input Methods**: Fetch earlier versions directly from the Modrinth API using your Project ID, or load `.mrpack` files locally.
- **Smart Comparison**: Automatically detects added, removed, and updated mods between two modpack versions.
- **Auto-Formatting**: Outputs production-ready Markdown files, perfect for Modrinth or GitHub releases.
- **Session Memory**: Remembers your Modrinth ID and local paths for a faster workflow on your next session.
- **Organized Outputs**: Automatically creates organized output directories for different projects and saves files named after the target version.
- **Modern UI**: Features a clean PyQt6 interface with native Dark and Light mode support.
- **Auto-Installer**: No complex setup required. Running the script will automatically install missing dependencies.

## Prerequisites

- Python 3.8 or higher.

## Installation & Usage

1. Clone this repository:

   ```bash
   git clone [https://github.com/yourusername/modrinth-changelog-generator.git](https://github.com/yourusername/modrinth-changelog-generator.git)
   ```

2. Navigate to the project directory:

```bash
cd modrinth-changelog-generator

```

3. Run the application:

```bash
python src/main.py

```

_Note: If `PyQt6` or `requests` are not installed, the application will install them automatically on its first run._

## How to Use

1. **Load Base Version**: In the left panel, input your Modrinth ID to fetch a published version, or select an older `.mrpack` file from your local drive.
2. **Load Target Version**: Select your newly exported `.mrpack` file.
3. **Select Output Method**: Choose between generating a Diff Changelog (shows only changes) or a Full Mod List.
4. **Generate**: Click "Generate & Save Markdown". The text will be displayed on the right panel, copied to your clipboard, and saved as a `.md` file in the `outputs/` directory.

## License

This project is licensed under the MIT License.
