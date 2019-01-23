"""

Author: Gaurav Kashyap (@gaurav_kay) newer implementation of idea.
Date started: 18-01-2019

current comments:

this file generates a list of links of songs in albums which is selected within this file


file 1. start point.
structure:
file 1 (this): sends list of links -> file 2 (count_words.py): makes file etc and generates dictionary of occurrence

"""

# prev comments
# this reads all the songs in the artist page.
# cause this is too much work i'm changing the plan for now, to search within albums

import bs4
import requests

name_with_spaces = input("Enter artist name: ")

name_list = name_with_spaces.split(" ")

# "-".join(list/sequence) joins "-" between the elements into a string
name = "-".join(name_list)

link = "https://genius.com/artists/" + name
print(link)

source_html = requests.get(link)
soup = bs4.BeautifulSoup(source_html.text, 'lxml')

# songs_list = soup.select('.full_width_button')
# a_href_link = songs_list[0].find()  # type: list
# using the code below to find songs page

# list builder
all_links = [i['href'] for i in soup.find_all('a', href=True)]


artist_song_page = all_links[0]
for i in all_links:
    if i[0] is '/':  # artist's song page starts with '/' and is the first occurrence
        artist_song_page = i
        break

artist_song_page_url = "https://genius.com" + artist_song_page

print(artist_song_page_url)

# extracting id for future use

artist_id_list_of_numbers = [i for i in artist_song_page if i.isdigit()]
artist_id = "".join(artist_id_list_of_numbers)
print(artist_id)


# all the albums of the artist:
album_list_link = "https://genius.com/artists/albums?for_artist_page=" + artist_id

album_list_link_requests_html = requests.get(album_list_link)
album_list_soup = bs4.BeautifulSoup(album_list_link_requests_html.text, 'lxml')

albums_list = album_list_soup.select('.album_link')  # prev comment: in flask implement this with clicking the links

for i in albums_list:
    print(i.text)

search_album = input()
# prev comment: remember to remove duplicate songs like in deluxe versions
search_album_modified = search_album.replace('-', ' ').replace('*', '').replace('?', '').replace('   ', ' ').replace('  ', ' ').replace('(', '').replace(')', '').replace('{', '')
search_album_modified_list = search_album_modified.split(' ')
selected_album_link = "-".join(search_album_modified_list)
selected_album_link = "https://genius.com/albums/" + name + "/" + selected_album_link

# prev comment: this is the point i realise i could've just asked for the album *facepalm*

selected_album_link_source_html = requests.get(selected_album_link)
selected_album_link_soup = bs4.BeautifulSoup(selected_album_link_source_html.text, 'lxml')

# u-display_block is the class that contains all the links of all the songs in the album selected

songs_in_album = selected_album_link_soup.select('.u-display_block')

# first_song = selected_album_link_soup.select('.u-xx_large_vertical_margins')

songs_in_album_link_list = []

for i in songs_in_album:
    print(type(i))
    # album_list_soup_object = bs4.BeautifulSoup(i, 'lxml')  # .find_all() works on bs4 object
    # print(type(album_list_soup_object))
    if i.has_attr('href'):  # checks is the list element of bs4 object type has attribute of href and then the link lists is appended with the link
        songs_in_album_link_list.append(i['href'])
