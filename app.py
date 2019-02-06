from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
data = None
result = None
dicts = []
"""

"data" is used for transferring data between the files

data {
    'name_with_spaces': "",
    'link': "",
    'artist_id': "",
    'albums_list': [""],
    'selected_album' = "",
    'song_links': [""] 
    'result': [("", "")]
}

"""


@app.route('/', methods=['GET', 'POST'])
@app.route('/select_artist', methods=['GET', 'POST'])
def select_artist():
    if request.method == 'POST':
        global data
        name_with_spaces = request.form['name_with_spaces']
        data = find_data(name_with_spaces)
        return render_template('select_album.html', data=data)
    else:
        return render_template('select_artist.html')


def find_data(name_with_spaces):

    data['name_with_spaces'] = name_with_spaces

    name_list = str(name_with_spaces).split(' ')
    link = "https://genius.com/artists/" + "-".join(name_list)

    data['link'] = link
    source_html = requests.get(link)
    soup = BeautifulSoup(source_html.text, 'lxml')

    all_links = [i['href'] for i in soup.find_all('a', href=True)]
    artist_song_page = all_links[0]
    for i in all_links:
        if i[0] is '/':  # artist's song page starts with '/' and is the first occurrence
            artist_song_page = i
            break

    artist_song_page_url = "https://genius.com" + artist_song_page

    # extracting id for future use
    artist_id_list_of_numbers = [i for i in artist_song_page if i.isdigit()]
    artist_id = "".join(artist_id_list_of_numbers)

    data['artist_id'] = artist_id
    album_list_link = "https://genius.com/artists/albums?for_artist_page=" + artist_id

    album_list_link_requests_html = requests.get(album_list_link)
    album_list_soup = BeautifulSoup(album_list_link_requests_html.text, 'lxml')

    albums_list = album_list_soup.select('.album_link')  # prev comment: in flask implement this with clicking the links

    albums = []
    for i in albums_list:
        albums.append(i.text)

    data['albums_list'] = albums

    return data


def links_generator(selected_album):
    selected_album_link = "-".join(selected_album.split(' '))
    selected_album_link = "https://genius.com/albums/" + "-".join(data['name_with_spaces'].split(' ')) + "/" + selected_album_link
    print("selected = ", selected_album_link)

    selected_album_link_source_html = requests.get(selected_album_link)
    selected_album_link_soup = BeautifulSoup(selected_album_link_source_html.text, 'lxml')
    # u-display_block is the class that contains all the links of all the songs in the album selected

    songs_in_album = selected_album_link_soup.select('.u-display_block')  # select('.u-display_block')
    # first_song = selected_album_link_soup.select('.u-xx_large_vertical_margins')

    songs_in_album_link_list = []

    for i in songs_in_album:
        if i.has_attr('href'):  # checks is the list element of bs4 object type has attribute of href and then the link lists is appended with the link
            songs_in_album_link_list.append(i['href'])

    return songs_in_album_link_list


@app.route('/count_words', methods=['GET', 'POST'])
def select_album():
    global data
    if request.method == 'POST':
        selected_album = request.form['selected_album']

        data['selected_album'] = selected_album

        links_of_songs_in_album = links_generator(selected_album)
        data['song_links'] = links_of_songs_in_album
        word_counter_driver()
    return render_template('display.html', data=data)


def count_words(link):
    res = requests.get(link)

    soup = BeautifulSoup(res.text, 'lxml')  # .encode("utf-8")  # to take care of chinese characters and all xD or while reading file
    lyrics_soup = soup.select('.lyrics')[0]  # .select return a list of ALL occurrences of .lyrics so the 1st element is considered

    # lyrics is a html tag with lyrics as class. lyrics.text gives the <p> tag etc.

    with open('lyrics_raw.txt', 'w', encoding="utf-8") as f:  # encoding to handle chinese chars etc
        f.write(lyrics_soup.text)
        f.write(" ")  # added this if we're using same file to write multiple songs
        f.close()

    lyrics_list = []  # creating a list as with file reading, writing and reading at the same time is unnecessary

    # filtering and removing non artist verses
    modified_file_contents = ""

    with open('lyrics_raw.txt', 'r', encoding="utf-8") as f:
        file_contents = f.read()  # f.read() gives a string

    if is_feature(file_contents):
        for i in range(len(file_contents)):
            # filter 1: removing other artists
            if file_contents[i] == '[':
                flag = False
                j = 0
                while True:
                    if file_contents[i + j] == ']':
                        break
                    else:
                        j += 1
                square_brackets_content = file_contents[i: i + j + 1]  # genius has everything in sq brackets
                del j
                artist = data['name_with_spaces']
                for j in range(len(square_brackets_content) - len(artist)):
                    if artist.lower() == square_brackets_content[j: j + len(artist)].lower():  # to handle different case artists
                        flag = True
                        break  # flag = True is to say that the following verse is by the selected artist
                if flag:
                    j = len(square_brackets_content) + 1
                    try:
                        while file_contents[i + j] != '[':  # till the start of next verse
                            modified_file_contents += file_contents[i + j]
                            j += 1
                    except IndexError:
                        pass

    else:
        for i in range(len(file_contents)):
            if file_contents[i] == '[':
                j = 0  # j is length of square bracket content
                while True:
                    if file_contents[i + j] == ']':
                        j += 1  # to remove the current '['
                        break
                    else:
                        j += 1
                try:
                    # starting from j skips the square bracket content
                    while file_contents[i + j] != '[':  # till the start of next verse
                        modified_file_contents += file_contents[i + j]
                        j += 1
                except IndexError:
                    pass

    # now to remove them annotations like comma, apostrophes etc
    modified_file_contents = modified_file_contents.replace('-', ' ')\
        .replace('*', '')\
        .replace('?', '')\
        .replace('   ', ' ')\
        .replace('  ', ' ')\
        .replace('(', '')\
        .replace(')', '')\
        .replace('{', '')\
        .replace('\'', '')\
        .replace(',', '')\
        .replace('-', '')\
        .replace('!', '')\
        .replace('\"', '')\
        .replace('--', '')\
        .replace('.', '')\
        .replace(',', '')\
        .replace('\n', ' ')

    modified_file_contents = modified_file_contents.lower()

    with open('lyrics_raw.txt', 'w', encoding="utf-8") as f:
        f.write(modified_file_contents)
        f.write(" ")

    """
    
    at this point the file is ready to be counted
    
    """

    # making the list
    words_list = modified_file_contents.split(" ")

    for i in words_list:
        if i == '' or i == ' ':
            words_list.remove(i)  # removing nonsense from the split

    dict_unsorted = {}

    for word in words_list:
        count = 0
        for i in words_list:  # i is the word which is checked throughout the list
            if word == i:
                count += 1
        dict_unsorted[word] = count  # adding a pair (word, count) to the unsorted dictionary

    if len(dicts) >= 2:  # merge
        dicts.append({**dicts.pop(), **dicts.pop()})
    else:
        dicts.append(dict_unsorted)


def word_counter_driver():
    for link in data['song_links']:
        count_words(link)
        print("link processed = ", link)

    if len(dicts) >= 2:  # merge
        dicts.append({**dicts.pop(), **dicts.pop()})

    if '' in dicts[0]:
        dicts[0].pop('', None)

    sorted_list = sorted(dicts[0].items(), key=lambda t: t[1], reverse=True)

    data['result'] = sorted_list


def is_feature(file_contents):
    flag = False
    for i in range(int(len(file_contents))):
        if file_contents[i] == '[':
            j = 0
            while True:
                if file_contents[i + j] == ']':
                    break
                else:
                    j += 1
            square_brackets_content = file_contents[i: i + j + 1]  # genius has everything in sq brackets
            del j
            artist = data['name_with_spaces']
            for j in range(len(square_brackets_content) - len(data['name_with_spaces'])):
                if artist.lower() == square_brackets_content[j: j + len(data['name_with_spaces'])].lower():  # to handle different case artists
                    flag = True
                    break  # flag = True is to say that the following verse is by the selected artist
        else:
            i += 1
    if flag:
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(debug=True)
