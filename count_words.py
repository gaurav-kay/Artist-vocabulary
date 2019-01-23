import bs4 as bs
import requests

"""

file 2

comments:
inputs sent by: list of links, artist name
im assuming that i am doing this in django so yeah. im also copying most snippets from my previous one.

"""

artist = "xxxtentacion"
res = requests.get('https://genius.com/xxxtentacion-numb-lyrics')  # https://genius.com/Xxxtentacion-numb-lyrics')  # https://genius.com/Kris-wu-rich-brian-joji-trippie-redd-and-baauer-18-lyrics')
is_feature = False

soup = bs.BeautifulSoup(res.text, 'lxml')  # .encode("utf-8")  # to take care of chinese characters and all xD or while reading file
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

if is_feature:
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
            for j in range(len(square_brackets_content) - len(artist)):
                if artist.lower() == square_brackets_content[j: j + len(artist)].lower():  # to handle different case artists
                    flag = True  # flag = True is to say that the following verse is by the selected artist
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

print(modified_file_contents)

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
    .replace('\n', ' ')

modified_file_contents = modified_file_contents.lower()

print(modified_file_contents)

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
dict_sorted = {}

for word in words_list:
    count = 0
    for i in words_list:  # i is the word which is checked throughout the list
        if word == i:
            count += 1
    dict_unsorted[word] = count  # adding a pair (word, count) to the unsorted dictionary
    # for i in words_list:  """# lmao this screwed up the counting"""
    #     if i is word:
    #         words_list.remove(i)  # removing the word in the pair above from the list to improve efficiency

print(dict_unsorted)

if '' in dict_unsorted:
    dict_unsorted.pop('', None)

sorted_list = sorted(dict_unsorted.items(), key=lambda t: t[1], reverse=True)  # https://www.youtube.com/watch?v=MGD_b2w_GU4

print(sorted_list)
# done (!)
