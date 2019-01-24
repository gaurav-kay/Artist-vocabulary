from flask import Flask, render_template, request, redirect, url_for
import bs4
import requests

app = Flask(__name__)
data = globals()
result = globals()
dicts = []
"""

lesson learnt: i don't think in flask you can have dynamic website where after you enter input the page changes. it has to reroute to another
OKAY SO ACTION IS LIKE A LOOP. okay not really

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
    global data

    data['name_with_spaces'] = name_with_spaces

    name_list = str(name_with_spaces).split(' ')
    link = "https://genius.com/artists/" + "-".join(name_list)

    data['link'] = link
    source_html = requests.get(link)
    soup = bs4.BeautifulSoup(source_html.text, 'lxml')

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
    album_list_soup = bs4.BeautifulSoup(album_list_link_requests_html.text, 'lxml')

    albums_list = album_list_soup.select('.album_link')  # prev comment: in flask implement this with clicking the links

    albums = []
    for i in albums_list:
        albums.append(i.text)

    data['albums_list'] = albums

    return data


def links_generator(selected_album):
    # print(selected_album, end="")
    # print("ok")
    # search_album_modified = selected_album.replace('-', ' ').replace('*', '').replace('?', '').replace('   ', ' ').replace('  ', ' ').replace('(', '').replace(')', '').replace('{', '')
    # search_album_modified_list = selected_album.split(' ')
    # print(selected_album)
    selected_album_link = "-".join(selected_album.split(' '))
    selected_album_link = "https://genius.com/albums/" + "-".join(data['name_with_spaces'].split(' ')) + "/" + selected_album_link
    print("selected = ", selected_album_link)
    # prev comment: this is the point i realise i could've just asked for the album *facepalm*

    selected_album_link_source_html = requests.get(selected_album_link)
    selected_album_link_soup = bs4.BeautifulSoup(selected_album_link_source_html.text, 'lxml')
    # u-display_block is the class that contains all the links of all the songs in the album selected

    songs_in_album = selected_album_link_soup.select('.u-display_block')  # select('.u-display_block')
    # print(songs_in_album)
    # first_song = selected_album_link_soup.select('.u-xx_large_vertical_margins')

    songs_in_album_link_list = []

    for i in songs_in_album:
        # print(type(i))
        # album_list_soup_object = bs4.BeautifulSoup(i, 'lxml')  # .find_all() works on bs4 object
        # print(type(album_list_soup_object))
        if i.has_attr('href'):  # checks is the list element of bs4 object type has attribute of href and then the link lists is appended with the link
            songs_in_album_link_list.append(i['href'])
    # print(songs_in_album_link_list)

    return songs_in_album_link_list


@app.route('/count_words', methods=['GET', 'POST'])
def select_album():
    global data
    if request.method == 'POST':
        selected_album = request.form['selected_album']

        data['selected_album'] = selected_album

        links_of_songs_in_album = links_generator(selected_album)
        # print(selected_album, "selected album is")
        data['song_links'] = links_of_songs_in_album
        # print(links_of_songs_in_album, "links")
        word_counter_driver()
    return render_template('display.html', data=data)


def count_words(link):
    res = requests.get(link)  # https://genius.com/Xxxtentacion-numb-lyrics')  # https://genius.com/Kris-wu-rich-brian-joji-trippie-redd-and-baauer-18-lyrics')

    soup = bs4.BeautifulSoup(res.text, 'lxml')  # .encode("utf-8")  # to take care of chinese characters and all xD or while reading file
    lyrics_soup = soup.select('.lyrics')[0]  # .select return a list of ALL occurrences of .lyrics so the 1st element is considered

    # soup = soup.encode(encoding="utf-8")

    # lyrics is a html tag with lyrics as class. lyrics.text gives the <p> tag etc.

    with open('lyrics_raw.txt', 'w', encoding="utf-8") as f:  # encoding to handle chinese chars etc
        f.write(lyrics_soup.text)
        f.write(" ")  # added this if we're using same file to write multiple songs
        f.close()

    lyrics_list = []  # creating a list as with file reading, writing and reading at the same time is unnecessary
    # filtering and removing non artist verses

    # okay so its tough (not possible) to modify a file in all languages (reading and editing bits without making another file or rewriting so yeah imma make a string of the modified file. link: https://stackoverflow.com/questions/125703/how-to-modify-a-text-file

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
                # print(square_brackets_content + " : " + str(flag))
                if flag:
                    j = len(square_brackets_content) + 1
                    try:
                        while file_contents[i + j] != '[':  # till the start of next verse
                            modified_file_contents += file_contents[i + j]
                            j += 1
                    except IndexError:
                        pass
                    # idk what this does :
                    # print("modified file contents = " + modified_file_contents)
                    # j = 1
                    # while file_contents[i + j] != '[':
                    #     j += 1
                    #
                    # print("x = " + file_contents[i: i + j - 1])
                    # print("x end")
                    # file_contents.replace(file_contents[i: i + j - 1], '')
                    """
                    
                    yay i finished it
                    
                    """
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

    # print(modified_file_contents)

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
        .replace('\n', ' ')

    modified_file_contents = modified_file_contents.lower()

    # print(modified_file_contents)

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
        # for i in words_list:  """# lmao this screwed up the counting"""
        #     if i is word:
        #         words_list.remove(i)  # removing the word in the pair above from the list to improve efficiency

    if len(dicts) >= 2:  # merge
        dicts.append({**dicts.pop(), **dicts.pop()})
    else:
        dicts.append(dict_unsorted)

    # print(dict_unsorted)

    # print(sorted_list)


def word_counter_driver():
    # print("reached")
    for link in data['song_links']:
        count_words(link)
        print("link processed = ", link)

    if len(dicts) >= 2:  # merge
        dicts.append({**dicts.pop(), **dicts.pop()})

    if '' in dicts[0]:
        dicts[0].pop('', None)

    print(len(dicts), "dicts")

    sorted_list = sorted(dicts[0].items(), key=lambda t: t[1], reverse=True)  # https://www.youtube.com/watch?v=MGD_b2w_GU4
    # print(sorted_list)

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


"""

FUCKING DONEEEEEE LETS GOOOOO DATE:24/01/2019 10:34 PM. LMAO HAVE TO STUDY FOR ME Xd

"""
