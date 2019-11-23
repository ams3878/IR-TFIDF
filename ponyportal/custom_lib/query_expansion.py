from .porter import PorterStemmer


def expand_term(term_list, stem_dict):
    new_term_list = []
    ps = PorterStemmer()
    stems = [ps.stem(word) for word in term_list]
    for i in stems:
        term_stem = "/" + i
        if term_stem in stem_dict.keys():
            new_term_list += stem_dict[term_stem]
    if len(new_term_list) == 0:
        return term_list
    return new_term_list
