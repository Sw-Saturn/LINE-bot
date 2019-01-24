import re
import MeCab
import sqlite3
import os
import random
import getTopic

class prepareChain(object):
    BEGIN = u"__BEGIN_SENTENCE__"
    END = u"__END_SENTENCE__"

    DB_PATH = "chain.db"
    DB_SCHEMA_PATH = "schemaTw.sql"

    def __init__(self,text):
        self.mecab = MeCab.Tagger ('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
        self.text = text

    def _divide(self,text):
        delimiter = u"。|．|,|\."
        text=re.sub(r"({0})".format(delimiter), r"\1\n", text)
        sentences = text.splitlines()
        # 前後の空白文字を削除
        sentences = [sentence.strip() for sentence in sentences]
        return sentences

    def _extract_word(self,sentence):
        # print(sentence)
        word = []
        self.mecab.parse('')
        # node = self.mecab.parseToNode(sentence)
        # while node:
        #     # if node.posid != 0:
        #     word.append(node.surface)
        #         print(node.surface)
        #     node = node.next
        for chunk in self.mecab.parse(sentence).splitlines()[:-1]:
            (surface,feature) = chunk.split('\t')
            word.append(surface)
        # print(word)
        return word

    def _make_dict(self,analyzed):
        # print(analyzed)
        if len(analyzed)<3:
            return {}
        dictMarkov = []
        dictMarkov.insert(0,[prepareChain.BEGIN,analyzed[0],analyzed[1]])
        for i in range(len(analyzed)-2):
            dictMarkov.append([analyzed[i],analyzed[i+1],analyzed[i+2]])
            # print(dictMarkov)
        dictMarkov.append([analyzed[-2],analyzed[-1],prepareChain.END])
        return dictMarkov


    def make(self):
        sentences = self._divide(self.text)
        dictionary = []
        for i in sentences:
            # print(i)
            words = self._extract_word(i)
            # print(words)
            dictionary.extend(self._make_dict(words))
            # print(dictionary)
        # print(words)
        return dictionary

    def save_to_DB(self,data):
        connection = sqlite3.connect(prepareChain.DB_PATH)
        with open(prepareChain.DB_SCHEMA_PATH, "r") as f:
                schema = f.read()
                connection.executescript(schema)
        statement = u"insert into chains (prefix1, prefix2, suffix) values (?, ?, ?)"
        print(data[0])
        datas = [(i[0],i[1],i[2]) for i in data]
        connection.executemany(statement,datas)
        connection.commit()
        connection.close()
class markov(object):
    def __init__(self,n):
        self.n = n

    def generateText(self,topic):
        if not os.path.exists(prepareChain.DB_PATH):
            raise IOError(u"DB File not found.")
        
        connect = sqlite3.connect(prepareChain.DB_PATH)
        connect.row_factory = sqlite3.Row
        generatedSentence = u""
        for i in range(self.n):
            text = self._generateSentence(connect,topic)
            generatedSentence += text
        connect.close()
        return generatedSentence

    def _generateSentence(self,connect,topic):
        sentences = []
        first_triplet = self._get_firstTriplet(connect,topic)
        if first_triplet==-1:
            return u""
        sentences.append(first_triplet[1])
        sentences.append(first_triplet[2])
        while sentences[-1] != prepareChain.END:
            prefix1 = sentences[-2]
            prefix2 = sentences[-1]
            triplet = self._getTriplet(connect,prefix1,prefix2)
            # print(triplet[2])
            sentences.append(triplet[2])
        result = "".join(sentences[:-1])

        return result

    def _get_firstTriplet(self,connect,topic):
        prefixes = (prepareChain.BEGIN,)
        chains = self._getChain(connect,prefixes)
        # print(num)
        # print(chains)
        keys = []
        for index,i in enumerate(chains):
            for key, value in i.items():
                if topic in value:
                    keys.append(index)
        if not keys:
            return -1
        num = random.choice(keys)
        triplet = chains[int(num)]
        print(triplet)
        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _getTriplet(self,connect,prefix1,prefix2):
        prefixes = (prefix1,prefix2)
        chains = self._getChain(connect,prefixes)
        num = generateUniqueRandomNumbers(len(chains)-1,1)
        # print(chains)
        # print(int(num[0]))
        triplet = chains[int(num[0])]
        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])
    
    def _getChain(self,connect,prefixes):
        sql = u"select prefix1, prefix2, suffix from chains where prefix1 = ?"
        if len(prefixes) == 2:
            sql += u" and prefix2 = ?"

        results = []

        cur = connect.execute(sql,prefixes)
        for row in cur:
            results.append(dict(row))
        return results
def generateUniqueRandomNumbers(max, num):
    return random.sample(range(max+1), num)
def main():
    a=input('> ')
    topics = getTopic.topicParser(a)
    if topics:
        topic = random.choice(topics)
        # print(topic)
        gen = markov(1)
        text = gen.generateText(topic)
        if text == u"":
            text = topic+"は何?"
    else:
        text = "は?"
    print('>>'+text)


def makeReply(sentence):
    topics = getTopic.topicParser(sentence)
    if topics:
        topic = random.choice(topics)
        # print(topic)
        gen = markov(1)
        text = gen.generateText(topic)
        if text == u"":
            text = topic + "は何?"
    else:
        text = "は?"
    # print('>>' + text)
    return text


if __name__ == "__main__":
    while True:
        main()
