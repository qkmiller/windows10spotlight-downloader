import requests
import os
import itertools
from multiprocessing import Pool

def get_sitemap():
    r = requests.get("https://windows10spotlight.com/post-sitemap.xml")
    if r.status_code != 200:
        return
    return r.text

def parse_sitemap(sitemap):
    links = []
    for line in sitemap.split("\n"):
        if "<loc>" in line:
            link = line.split("<loc>")[1].split("</loc>")[0]
            print(link)
            links.append(link)
    return links[:-1]

def filter_name(name):
    filter_map = {
            "\"": "",
            "'": "",
            ";": "",
            "<": "",
            ">": "",
            ".": "",
            ",": "",
            " ": "_",
            "/": "_",
            "\\": "_",
            ":": "_",
            "?": "",
            "!": "",
            "@": "",
            "#": "",
            "$": "",
            "%": "",
            "^": "",
            "&": "",
            "*": "",
            "(": "",
            ")": ""
            }
    for f in filter_map:
        name = name.replace(f, filter_map[f])
    return name

def get_image_info(link):
    image = {}
    r = requests.get(link)
    if r.status_code != 200:
        return
    split = r.text.split("\n")
    image["url"]    = split[12].split("href=\"")[1].split("\"")[0]
    image["title"]  = filter_name(split[6].split("<h1>")[1].split("</h1>")[0])
    print("{} - {}".format(image["url"], image["title"]))
    return image

def build_images(links):
    pool = Pool()
    images = pool.map(get_image_info, links)
    pool.close()
    pool.join()
    return images

def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)

def download_image(path, image):
    r = requests.get(image["url"])
    if r.status_code != 200:
        print("Could not download: {}".format(image["url"]))
        return
    file_path = "{}/{}.jpg".format(path, image["title"])
    with open(file_path, "wb") as image_file:
        image_file.write(r.content)
    print(file_path)

def start(path, images):
    pool = Pool()
    pool.starmap(download_image, zip(itertools.repeat(path), images))
    pool.close()
    pool.join()
#    for image in images:
#        download_image(path, image)



if __name__ == "__main__":
    path = "./spotlight_images"
    sitemap = get_sitemap()
    if sitemap is None:
        print("Error: Could not get the sitemap!")
        exit(1)
    print("Getting site map...")
    links = parse_sitemap(sitemap)
    if len(links) == 0:
        print("Error: Could not parse the sitemap!")
        exit(1)
    images = build_images(links)
    if len(images) == 0:
        print("Error: Could not collect image information!")
        exit(1)
    check_path(path)
    start(path, images)
