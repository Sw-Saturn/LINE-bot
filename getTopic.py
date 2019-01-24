import MeCab
import sys


mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

def topicParser(text):
    words = []
    node = mecab.parseToNode(text)
    target = ('名詞', )
    while node:
        if node.feature.split(',')[0] in target:
            words.append(node.surface)
        node = node.next
    return words

def main():
    inputText = sys.argv[1]
    output = topicParser(inputText)
    print(output)

if __name__ == '__main__':
    main()
