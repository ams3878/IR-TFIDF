from .porter import PorterStemmer
import string

def expand_term(term_string, stem_dict):
    term_string = term_string.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    new_term_list = []
    ps = PorterStemmer()
    for i in term_string.split():
        term_stem = "/" + ps.stem(i)
        if term_stem in stem_dict.keys():
            new_term_list += stem_dict[term_stem]
        else:
            new_term_list.append(i)
    return new_term_list
