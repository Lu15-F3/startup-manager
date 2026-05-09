# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-05-09
### Added
- **Multi-language Support**: Automatic detection of system language (PT-BR/EN).
- **Language Toggle**: Manual button in the UI to switch between Portuguese and English.
- **App Arguments**: New field to add custom execution arguments (e.g., `--minimized`, `--tray`).
- **Dynamic ToolTips**: Added localized tooltips for the arguments input field.
- **Enhanced UI**: Added "Move Up" and "Move Down" buttons for reordering the startup queue.

### Changed
- **Professional Naming**: Renamed the internal startup script from `atraso_apps.sh` to `startup-launcher.sh` for better system compatibility.
- **UI Refresh**: Updated the interface with a modern "Fusion" style and Catppuccin-inspired color palette.
- **Improved App Discovery**: Optimized the scanning of `.desktop` files across RPM, Flatpak, and AppImage paths.

### Fixed
- **Placeholder Alignment**: Fixed an issue where the arguments field showed the wrong placeholder text in certain languages.
- **WM_CLASS/Icon**: Ensured the application is correctly identified by task managers for proper icon display.

## [1.0.0] - Initial Release
### Added
- **Core Logic**: Basic scanning of installed applications from `/usr/share/applications`.
- **Startup Script Generation**: Creation of a Bash script to handle application delays.
- **Autostart Integration**: Automatic creation of `.desktop` files in `~/.config/autostart`.
- **Basic UI**: Simple list-based interface for selecting apps and defining delay times in seconds.
- **Config Persistence**: Saving and loading the startup queue using a JSON file in `~/.config/startup_manager/`.
- **Uninstall System**: Built-in "Clear Everything" function to remove all generated files and autostart entries.

---
*Note: This project follows Semantic Versioning.*