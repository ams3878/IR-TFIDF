
FILENAME = 'All_Transcripts_Edited.html'
DOC_ID_FILE = 'docNames.tsv'

def main():
    season_num = 1
    season_episode = 0
    episodes_per_season = [100, 26, 26, 13, 26, 26, 26, 26, 26, 26]
    episode_lines = []
    episode_name = ''
    episode_words = 0
    with open(DOC_ID_FILE, 'w') as doc_ids:
        with open(FILENAME, 'r') as transcript:
            line = transcript.readline()

            while line:
                if line.find('h2') >= 0:
                    split_line = line.split('title=\"')[1]
                    episode_name = split_line.split('\"')[0]
                    season_episode += 1
                    if season_episode > episodes_per_season[season_num]:
                        season_num += 1
                        season_episode = 1
                        if season_num == 10:
                            season_num = 0
                line = clean_line(line)
                episode_words += len(line.split(' '))
                episode_lines.append(line)
                line = transcript.readline()
                if not line or line.find('h2') >= 0:
                    if len(episode_lines) > 0:

                        episode_id = str(season_num)
                        if season_episode < 10:
                            episode_id += '0'
                        episode_id += str(season_episode)
                        with open('transcripts/' + episode_id+'.txt', 'w') as new_file:
                            new_file.writelines(episode_lines)

                        #   DocId  EpisodeName  WordCount
                        doc_line = "%s\t%s\t%d\n" % (episode_id, episode_name, episode_words)
                        doc_ids.write(doc_line)
                        episode_name = ''
                        episode_lines = []
                        episode_words = 0


def clean_line(line):
    tags = ['dd', 'dl', 'b', 'i']
    for tag in tags:
        line = line.replace('<' + tag + '>', '')
        line = line.replace('</' + tag + '>', '')
    return line


if __name__ == "__main__":
    main()
