from .porter import PorterStemmer
import string

def expand_term(terms, stem_dict):
    new_term_list = []
    ps = PorterStemmer()
    for i in terms:
        term_stem = "/" + ps.stem(i)
        if term_stem in stem_dict.keys():
            new_term_list += stem_dict[term_stem]
        else:
            new_term_list.append(i)
    return new_term_list
