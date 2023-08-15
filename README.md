# Clutter Cutter

The **Clutter Cutter Script** is a Python tool designed to help you organize and consolidate your media files from a source (src) folder to a destination (dst) folder. It automatically sorts duplicates and unique files, organizes them into specific subfolders, and further arranges media files based on their date modified and metadata.

## Getting Started

1. Clone or download this repository to your local machine.
2. Ensure you have Python 3.x installed.

## Usage

1. Run the script by executing the `ClutterCutter.py` file:

    ```bash
    python ClutterCutter.py
    ```

2. The script will prompt you to provide source and destination folder paths. It will then move all files from the source folder to the destination folder.

3. Duplicates will be identified using hashing and moved to a "Duplicates" subfolder within the destination folder.

4. Unique files will be moved to an "Unique" subfolder within the destination folder.

5. Files within the "Unique" folder will be further categorized into "Audio", "Media", and "Misc" folders.

6. Files within the "Media" folder will be sorted into subfolders based on their year of creation using date modified and metadata.

NOTE: pip install python-magic-bin==0.4.14 to download python magic on Windos

## Customization

If you encounter a missing file format that you want the script to recognize, you can add it in the **constants.py** file.

## Structure

The project is organized as follows:

-   **ClutterCutter.py**: The main script that you run to start the media consolidation process.

-   **constants.py**: Contains file format constants that the script recognizes.

-   **main_helpers.py**: Contains helper functions used in the main script.

-   **metadata_helpers.py**: Contains helper functions responsible for processing metadata and organizing based on date modified.

-   **os_helpers.py**: Contains helper functions related to file system operations and directory traversing.

## Contributing

Feel free to contribute to this project by opening issues or pull requests.

## License

This project is licensed under the MIT License
