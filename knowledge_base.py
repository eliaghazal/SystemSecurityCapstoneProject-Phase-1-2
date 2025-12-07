import os

def load_words():
    words = set()
    
    # 1. Load from file if exists
    word_file = 'words.txt'
    if os.path.exists(word_file):
        with open(word_file, 'r') as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    # Filter single letters except 'a' and 'i'
                    if len(w) == 1 and w not in ('a', 'i'):
                        continue
                    words.add(w)
    
    # 2. Add default common words if file missing or empty
    if len(words) < 100:
        defaults = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
            'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
            'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up',
            'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time',
            'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
            'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
            'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
            'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were',
            'has', 'had', 'been', 'very', 'much', 'great', 'should', 'before', 'long', 'right', 'used', 'me',
            'between', 'under', 'last', 'never', 'place', 'same', 'another', 'while', 'number', 'part', 'found',
            'world', 'still', 'might', 'must', 'hand', 'off', 'since', 'many', 'does', 'again', 'where', 'why',
            'help', 'talk', 'turn', 'start', 'show', 'hear', 'play', 'run', 'move', 'like', 'live', 'believe',
            'hold', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include',
            'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create',
            'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember',
            'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay',
            'fall', 'cut', 'reach', 'kill', 'remain', 'suggest', 'raise', 'pass', 'sell', 'require', 'report',
            'decide', 'pull', 'return', 'explain', 'hope', 'develop', 'carry', 'break', 'receive', 'agree',
            'support', 'hit', 'produce', 'eat', 'cover', 'catch', 'draw', 'choose', 'cause', 'point', 'listen',
            'realize', 'place', 'close', 'information', 'student', 'system', 'program', 'question', 'work',
            'government', 'country', 'night', 'water', 'thing', 'result', 'business', 'study', 'issue', 'side',
            'group', 'process', 'teacher', 'data', 'research', 'education', 'member', 'law', 'car', 'city',
            'community', 'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information', 'back',
            'parent', 'face', 'others', 'level', 'office', 'door', 'health', 'person', 'art', 'war', 'history',
            'party', 'result', 'change', 'morning', 'reason', 'research', 'girl', 'guy', 'food', 'moment',
            'air', 'force', 'man', 'cat', 'cats', 'love', 'loves'
        }
        words.update(defaults)

    # 3. Add Custom Required Words
    custom_terms = {
        "charbel", "system", "security", "dr"
    }
    words.update(custom_terms)
    
    return words

COMMON_WORDS = load_words()

# Expanded Trigram List for better detection of concatenated text
COMMON_TRIGRAMS = {
    'THE': 1.0, 'AND': 0.9, 'ING': 0.9, 'HER': 0.8, 'HAT': 0.8, 'HIS': 0.8, 'THA': 0.8,
    'ERE': 0.7, 'FOR': 0.7, 'ENT': 0.7, 'ION': 0.7, 'TER': 0.7, 'WAS': 0.7, 'YOU': 0.7,
    'ITH': 0.6, 'VER': 0.6, 'ALL': 0.6, 'WIT': 0.6, 'THI': 0.6, 'TIO': 0.6,
    'NTH': 0.6, 'STH': 0.6, 'OFT': 0.6, 'ETH': 0.6, 'ATE': 0.6, 'OUL': 0.5,
    'MAN': 0.5, 'CAT': 0.5, 'OVE': 0.5, 'VES': 0.5, 'LOV': 0.5 # Added some common patterns
}
