import argparse

from mkdict.scrape import download_pages

DEST_DIR = 'pages'

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Download pages by index or range.')
    parser.add_argument('indexes', type=str, help='Comma-separated list of single indexes or ranges (e.g., "1,2,10-20,22,30-50").')
    args = parser.parse_args()

    download_pages(args.indexes, DEST_DIR)
