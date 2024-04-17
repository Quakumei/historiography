import time
import re

import click
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

def dump_list_to_file(filename, my_list):
    try:
        # Open the file in write mode
        with open(filename, "w") as file:
            # Iterate over the list and write each element to the file
            for item in my_list:
                file.write(str(item) + "\n")  # Convert item to string and add a newline
        print("List dumped to file successfully.")
    except IOError:
        print("Error: Unable to write to file", filename)


@click.command()
@click.option('--output_filename', '-o', default='out.txt', help='Filename to write extracted links to')
@click.option('--url_to_parse', '-u', help='Url to parse', required=True)
@click.option('--topage', '-p', type=int, required=True, help='Till page with number specified (including)')
def parse_website(output_filename, url_to_parse, topage):
    """
    Simple program to parse a URL and save its content to a file.
    
    OUTPUT_FILENAME is the filename to save the parsed content.
    URL_TO_PARSE is the URL of the webpage to parse.
    """
    click.echo(f"Parsing URL: {url_to_parse}")
    click.echo(f"Output filename: {output_filename}")

    url = url_to_parse
    browser = webdriver.Chrome()
    all_links = []
    all_titles = []
    for i in tqdm(range(1, topage+1)):
        print(i)
        browser.get(url + f'&page={str(i)}')
        time.sleep(2) # wait till load todo: change to tied to element
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            if href.startswith('/article'):
                print(link.get_text())
                print(href)
                all_titles.append(link.get_text())
                all_links.append(f"https://cyberleninka.ru{href}/pdf")
    dump_list_to_file(output_filename, all_links)
    dump_list_to_file(output_filename+'.titles', all_titles)
    click.echo(f"Exported pdf links to {output_filename}")
    click.echo(f"Exported pdf titles to {output_filename+'.titles'}")

if __name__ == '__main__':
    parse_website()

