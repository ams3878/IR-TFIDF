import re
from .models import *
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
                        script_tag = script_tag + line
                        if clean_line != '\n':
                            script = script + clean_line
                            line_count += 1
                    line = f.readline()
                    line_list = line.split('>')
                meta = meta + ', lines: ' + str(line_count) + "]\n"
                f_new_tags = open(ep_loc[:-1] + "_tags\\" + str(count) + '.html', 'w')
                f_new_tags.write(meta)
                f_new_tags.write(script_tag)
                f_new_tags.close()
                f_new = open(ep_loc + str(count), 'w')
                f_new.write(meta)
                f_new.write(script)
                q = Document(id=count,
                             title=title,
                             )
                q.save()
                f_new.close()

        except IndexError:
            pass
    f.close()
    print("DONE-adding episodes")


def cleanhtml(raw_html):
    find_name = re.compile('</dd><dd><b>.*?</b>')

    temp = re.match(find_name, raw_html)
    if temp:
        match = temp.group(0).split('<b>')[1].split('</b>')[0]
        raw_html = re.sub(find_name, '%%' + match + '%%',  raw_html)

    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def create_new_chars():
    chars_set = list(Character.objects.all())
    chars = []
    for c in chars_set:
        chars.append(c.id)
    for i in range(243):
        f = open('ponyportal\static\episodes\\' + str(i+1))
        meta = f.readline()
        line = f.readline()
        while line:
            try:
                findname = re.compile('%%.*?%%')
                temp = re.match(findname, line)

                if temp:
                    name = temp.group(0)[2:-2]
                    char = name.split('and')
                    if len(char) > 1 and char[1] not in chars:
                        q = Character(id=re.sub(r'\W+', '', char[1]))
                        q.save()
                        chars.append(char[1])
                    char = char[0].split(',')
                    for c in char:
                        if c not in chars:
                            q = Character(id=re.sub(r'\W+', '', c))
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