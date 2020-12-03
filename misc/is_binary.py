from spacy import displacy
# Check if a question is boolean question


questions = [
             "Is elegant jewelry , finely carved and inlaid furniture , and cosmetic vessels and implements made from a wide range of materials produced?",
             "According to what the passage described, where are pyramids built?",
              "When did Cleopatra give birth to twins fathered by Antony, Alexander Helios and Cleopatra?",
             "Where have archaeological excavations discovered an averlap between the final phase of Late Harappan pottery and the earliest phase of Painted Grey Ware pottery, the latter being associated with the Vedic Culture and dating from around 1200 BCE?",
             "What did the king initiate in particular at Karnak in Thebes, where he dedicated a temple to Amun?",
            "Is it true that his death , certainly well past that of his intended heirs has created succession struggles?",
            'When did the two empires of Southern India , the Western Chalukyas and the Chola dynasty of Tanjore fight many fierce wars to control the fertile region of Vengi?',
            "Does an important inscription on the tomb of Ankhtifi , a nomarch during the early First Intermediate Period describe the pitiful state of the country when famine stalked the land?",
            "What is Egyptian influence reaching into what is today the Sudan?",
            "Is it true that their charge became thus creating local dynasties largely independent from the central authority of the Pharaoh?",
            "Were the pyramids of Giza perfected by King Sneferu?",
            "Who describes the pitiful state of the country when famine stalked the land?",
             "Are flippers, useless for flight in the air become by their vestigial wings?",
             "Who did One Klingon speaker, d'Armond Speers raise to speak Klingon as a first language, whilst the boy's mother communicated with him in English?",
             "Is HTML, JavaScript, and SQL used in a here document)?",
            "Did Egypt's expanding interests in trade goods such as ebony, incense such as myrrh and frankincense, gold, copper and other useful metals inspire the ancient Egyptians?",
             "According to what the passage described, is it true that the Team Rocket trio show signs of goodness, such as care and friendship with their Pokémon and each other despite their constant antagonism as they occasionally put their differences aside and work together with Ash against a common threat, such as in Pokémon: The Movie 2000, where they aid Ash in retrieving the three treasures in order to save the world?",
]

def find_root(sent, return_idx = True):
    for idx,word in enumerate(sent):
        if word.head == word:
            if return_idx:
                return word, idx
            else:
                return word

def is_binary_question(question):
    wh = {'how', 'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'whose'}
    tf = {'is','are','do','does','was','were','did','have','has','had', 'would','will', 'whether','shall', 'should','must','may','might'}

    sent = nlp(question)
    # displacy.render(sent, style='dep', jupyter=True, options={'distance': 90})
    
    ct = 1
    wh_idx = None
    tf_idx = None
    for word in sent:
        if word.text.lower() in wh and not wh_idx:
            wh_idx = ct
        if ((word.text.lower() in tf)) and not tf_idx:
            tf_idx = ct
        ct += 1

    if tf_idx and not wh_idx:
        return True
    elif not tf_idx and wh_idx:
        return False
    elif tf_idx and wh_idx:
        root, root_idx = find_root(sent)
        if root.text.lower() in tf:
            return True
        return False
    else:
        return False

for question in questions:
    print(question)
    if is_binary_question(question):
        print('Binary Question')
    else:
        print('WH Question')
    print('*'*100)
