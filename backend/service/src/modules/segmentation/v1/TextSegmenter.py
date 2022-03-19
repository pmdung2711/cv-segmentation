import tensorflow as tf
from service.src.modules.segmentation.v1.Segmenter import Segmenter
from nltk import sent_tokenize
import numpy as np
import re


class TextSegmenter():
    def __init__(self, model_weights, tf_hub_path, max_sentences=128):
        self.model = Segmenter(max_sentences, tf_hub_path)
        _ = self.model([['Sentence 0', 'sentence 1', 'sentence 3'], ['Sentence 0', 'sentence 1', 'sentence 3']],
                       prepare_inputs=True)
        self.model.load_weights(model_weights)
        self.ner_model = None

    def segment(self, text, heading, processed_headings, type='tokenize'):

        only_text_heading = ''.join([e for e in heading if e.isalpha()])

        if any([e for e in processed_headings if e in only_text_heading.lower()]):

            if type == 'tokenize':
                sentences = sent_tokenize(text)
            elif type == 'newline':
                sentences = text.split("\n")

            scores = self.model([[e +"." for e in sentences]], prepare_inputs=True).numpy()[0][:len(sentences)]
            results = list(np.argmax(scores, axis=-1))

            passages = []
            passage = ''
            for i, (sentence, result) in enumerate(zip(sentences, results)):

                if sentence.replace("\n", "").replace(".", "") == heading.replace("\n", "").replace(".", ""):
                    sentence = ""

                if i == 0:
                    passage = sentence
                    continue
                if result == 1:
                    passages.append(passage)
                    passage = sentence
                else:
                    passage += '\n' + sentence

            passages.append(passage)
            return passages, [heading] * len(passages)

        return [text], [heading]

    @staticmethod
    def _check_output(output_ner, target_ner=['DURATION']):

        intersection_list = list((set(output_ner) & set(target_ner)))

        if len(intersection_list) == 0:
            return [e for e in target_ner if e not in intersection_list]

        return []

    @staticmethod
    def merge_segments(passages, processed_headings, entities_list, entity_extractor):

        if_missing = []
        missing_list = []

        for index, passage in enumerate(passages):
            output = []
            index_list = []
            text = str(passage[0])
            heading = passage[1]
            only_text_heading = ''.join([e for e in heading if e.isalpha()])
            if any([e for e in processed_headings if e in only_text_heading.lower()]):
                for entity in entities_list:
                    ent_text = entity[2]
                    ent_tag = entity[0]
                    try:
                        # ent_index = text.index(ent_text)
                        ent_indices = [e.start() for e in re.finditer(ent_text.replace("|", ""), text)]
                        for ent_index in ent_indices:
                            if ent_index not in index_list:
                                output.append((ent_tag, ent_index, ent_text))
                                index_list.append(ent_index)
                    except:
                        continue

                output.sort(key=lambda x: (x[1], x[2]))
                output = entity_extractor.remove_duplication(output)
                miss_list = TextSegmenter._check_output([e[0] for e in output])
                if_missing.append(miss_list != [])
                missing_list.append(miss_list)

            else:
                if_missing.append(False)
                missing_list.append([])


        removed_list = []
        while True:
            for i in range(len(passages) - 2, -1, -1):
                if if_missing[i]:
                    if 'DURATION' in missing_list[i] \
                            and 'DURATION' not in missing_list[i + 1] \
                            and passages[i][1] == passages[i + 1][1]:
                        passages[i + 1] = tuple([passages[i ][0] + "\n" + passages[i + 1][0],
                                                 passages[i + 1][1]])
                        missing_list[i + 1] = list(set(missing_list[i + 1]).intersection(missing_list[i]))

                        if missing_list[i + 1] is None or len(missing_list[i + 1]) == 0:
                            if_missing[i + 1] = False

                        removed_list.append(i)

            if not removed_list:
                break

            for index in sorted(removed_list, reverse=True):
                del passages[index]
                del missing_list[index]
                del if_missing[index]

            removed_list = []

        removed_list = []
        while True:
            for i in range(len(passages) - 1, 0, -1):
                if if_missing[i]:
                    if 'DURATION' in missing_list[i] \
                            and 'DURATION' not in missing_list[i - 1] \
                            and passages[i][1] == passages[i - 1][1]:
                        passages[i - 1] = tuple([passages[i - 1][0] + "\n" + passages[i][0],
                                                 passages[i - 1][1]])
                        missing_list[i - 1] = list(set(missing_list[i - 1]).intersection(missing_list[i]))

                        if missing_list[i - 1] is None or len(missing_list[i - 1]) == 0:
                            if_missing[i - 1] = False

                        removed_list.append(i)

            if not removed_list:
                break

            for index in sorted(removed_list, reverse=True):
                del passages[index]
                del missing_list[index]
                del if_missing[index]

            removed_list = []

        return passages
