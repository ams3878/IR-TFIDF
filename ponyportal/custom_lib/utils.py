import re
from math import ceil
from ..models import *
from copy import deepcopy
# ----------------------------------------------------------
#
# Get all the episodes from master text
#
# ----------------------------------------------------------


def create_episode_files(master, ep_loc):
    f = open(master)
    line = f.readline()
    line_list = line.split('>')

    count = 0
    while line:
        meta = "meta[ "
        script = ''
        script_tag = ''
        script_html = ''
        try:
            if line_list[0].split()[0] == '<h2':
                count += 1
                line_count = 0
                title = line_list[2][:-3]
                meta = meta + "title:" + title
                line = f.readline()
                line_list = line.split('>')
                while line:
                    try:
                        if line_list[0].split()[0] == '<h2':
                            break
                    except IndexError:
                        pass
                    if line != '':
                        clean_line = cleanhtml(line)
                        script_html = script_html + line
                        if clean_line[1] != '\n':
                            line_count += 1
                            script_tag = script_tag + clean_line[1]
                        if clean_line[0] != '\n':
                            script = script + clean_line[0]
                    line = f.readline()
                    line_list = line.split('>')
                meta = meta + ', lines: ' + str(line_count) + "]\n"
                f_new_tags = open(ep_loc[:-1] + "_tags\\" + str(count), 'w')
                f_new_tags.write(meta)
                f_new_tags.write(script_tag)
                f_new_tags.close()
                f_new_html = open(ep_loc[:-1] + "_html\\" + str(count) + '.html', 'w')
                f_new_html.write(meta)
                f_new_html.write(script_html)
                f_new_html.close()
                f_new = open(ep_loc + str(count), 'w')
                f_new.write(meta)
                f_new.write(script)
                f_new.close()
                season = get_season(count)
                season_obj = Season.objects.filter(id=season)
                if not season_obj:
                    q = Season(id=season)
                    q.save()
                    season_obj = Season.objects.filter(id=season)
                doc_obj = Document.objects.filter(id=count)
                if not doc_obj:
                    if season >= 10:
                        script_type = 'feature'
                    else:
                        script_type = 'episode'
                    q = Document(id=count,
                                 title=title,
                                 script_type=script_type,
                                 )
                    q.save()
                    doc_obj = Document.objects.filter(id=count)
                season_doc_obj = SeasonToDocument.objects.filter(episode=doc_obj[0], season=season_obj[0])
                if not season_doc_obj:
                    q = SeasonToDocument(episode=doc_obj[0], season=season_obj[0])
                    q.save()
                f_new.close()

        except IndexError:
            pass
    f.close()
    print("DONE-adding episodes")


def get_pos_index(filename):
    index = {}
    with open('ponyportal\static\ponyportal\\' + filename, 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[1:-1]
            posting_dict = {}
            for posting in posting_list:
                posting = posting.split(':')
                try:
                    posting_dict[int(posting[0])].append(int(posting[1]))
                except KeyError:
                    posting_dict[int(posting[0])] = [int(posting[1])]
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index


def get_bigrams(filename):
    index = {}
    with open('ponyportal\static\ponyportal\\' + filename, 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[1:-1]
            posting_dict = {}
            for posting in posting_list:
                posting = posting.split(':')
                posting_dict[posting[0]] = posting[1]
            index[line[0]] = posting_dict
            line = index_file.readline()
    return index


def get_index(filename):
    index = {}
    with open('ponyportal\static\ponyportal\\' + filename, 'r') as index_file:
        line = index_file.readline()
        while line:
            line = line.split('\t')
            posting_list = line[2:]
            posting_dict = {'docs': {}}
            for posting in posting_list:
                posting = posting.split(':')
                posting_dict['docs'][posting[0]] = int(posting[1])
            posting_dict['count'] = str(line[1])
            index[line[0]] = posting_dict

            line = index_file.readline()
    return index


def get_stems(filename):
    stems = {}
    with open('ponyportal\static\ponyportal\\' + filename, 'r') as stem_file:
        line = stem_file.readline()
        while line:
            line = line.split('\t')
            stems[line[0]] = line[1:-1]
            line = stem_file.readline()
    return stems


def cleanhtml(raw_html):
    find_name = re.compile('</dd><dd><b>.*?</b>')

    temp = re.match(find_name, raw_html)
    tagged = raw_html
    if temp:
        match = temp.group(0).split('<b>')[1].split('</b>')[0]
        tagged = re.sub(find_name, '%%' + match + '%%',  raw_html)

    cleanr = re.compile('<.*?>')
    taggedtext = re.sub(cleanr, '', tagged)
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext, taggedtext


def create_new_chars():
    chars_set = list(Character.objects.all())
    chars = []
    for c in chars_set:
        chars.append(c.id)
    for i in range(243):
        f = open('ponyportal\static\episodes_tags\\' + str(i+1))
        meta = f.readline()
        line = f.readline()
        while line:
            try:
                findname = re.compile('%%.*?%%')
                temp = re.match(findname, line)

                if temp:
                    name = temp.group(0)[2:-2]
                    char = re.sub(r'\bbut.*', '', name)
                    char = re.sub(r'\bexcept.*', '', char)
                    char = (re.sub(r'\band\b', ',', char)).split(',')
                    for c in char:
                        if c not in chars:
                            q = Character(id=re.sub(r'[^\w\s]', '', c))
                            q.save()
                            chars.append(c)
            except IndexError:
                pass
            line = f.readline()


def create_char_episode():
    for i in range(243):
        f = open('ponyportal\static\episodes\\' + str(i+1))
        line = f.readline()
        meta = f.readline()
        doc_obj = Document.objects.filter(id=i + 1)[0]
        while line:
            try:
                findname = re.compile('%%.*?%%')
                temp = re.match(findname, line)

                if temp:
                    name = temp.group(0)[2:-2]
                    char = name.split('and')
                    if len(char) > 1 and char[1]:
                        char_name = re.sub(r'\W+', '', char[1])
                        char_obj = Character.objects.filter(id=char_name)[0]
                        if not CharacterToDocument.objects.filter(character=char_obj, episode=doc_obj):
                            q = CharacterToDocument(character=char_obj, episode=doc_obj)
                            q.save()
                    char = char[0].split(',')
                    for c in char:
                        char_name = re.sub(r'\W+', '', c)
                        char_obj = Character.objects.filter(id=char_name)[0]
                        if not CharacterToDocument.objects.filter(character=char_obj, episode=doc_obj):
                            char_obj = Character.objects.filter(id=char_name)[0]
                            doc_obj = Document.objects.filter(id=i+1)[0]
                            q = CharacterToDocument(character=char_obj, episode=doc_obj)
                            q.save()
            except IndexError:
                pass
            line = f.readline()
    print("Done adding chars to docs")


def get_lines_keywords_better(terms, episode):
    f = open('ponyportal\static\episodes\\' + str(episode), 'r')
    lines = f.read()
    print(lines)
    for i in terms:
        lines = lines.replace(i, "<b>"+i+"</b>")
    f.close()
    return lines


def get_lines_keywords(terms, episode):
    f = open('ponyportal\static\episodes\\' + str(episode), 'r')
    stopword_list = get_stopwords()
    terms = [x for x in terms if x not in stopword_list]

    matched_lines = []
    for line in f:
        temp_line = line.lower()
        for i in terms:
            space_i = " " + i + " "
            temp_line = temp_line.replace(space_i, " <b>" + i + "</b> ")
        if line.lower() != temp_line:
            matched_lines.append(temp_line)
    f.close()
    return matched_lines[0:5]


def get_stopwords():
    f = open('ponyportal\static\ponyportal\stopwords.txt', 'r')
    line = f.read()
    f.close()
    return line.split(',')


def get_season(episode):
    if episode <= 52:
        return ceil(episode / 26)
    elif episode <= 65:
        return 3
    elif episode <= 221:
        return 3 + ceil((episode - 65) / 26)
    elif episode <= 239:
        return 10
    else:
        return episode - 239 + 10
