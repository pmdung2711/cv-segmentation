import fitz
import string
import re
from unidecode import unidecode
import pandas as pd
import numpy as np
import itertools
import base64
import os
from operator import itemgetter
from dateutil.parser import parse
import wordninja


class TextExtractor(object):
    bold_factor = 1

    def __init__(self):
        pass

    @staticmethod
    def convert_word_to_pattern(word: str):
        '''
        convert the word to regrex pattern
        Eg: work -> ^w[\s]*o[\s]*r[\s]*k[\s]*
        '''
        word_pattern = "[\s]*" + "[\s]*".join([e for e in word]) + "[\s]*"

        return word_pattern

    @staticmethod
    def get_pattern_from_file(folder_path: str = "service/src/modules/textextraction/v1/"):

        with open(folder_path + 'headings.txt') as file:
            lines = file.readlines()
            heading_pattern_list = [heading[0:len(heading) - 1] for heading in lines if
                                    (heading[0] != '#' and heading != '\n')]

        heading_pattern_list = [TextExtractor.convert_word_to_pattern(heading_pattern) for heading_pattern in
                                heading_pattern_list]
        heading_patterns = '|'.join(heading_pattern_list)

        return heading_patterns

    @staticmethod
    def is_valid_page(page):
        page_text = ""
        blocks = page.get_text("dict")['blocks']
        text_blocks = [block for block in blocks if block['type'] == 0]
        for block in text_blocks:
            for lines in text_blocks:
                for line in lines['lines']:
                    for span in line['spans']:
                        page_text += " " + span['text']
        invalid_text_list = ['top jobs for it people']
        invalid_list = [TextExtractor.convert_word_to_pattern(invalid_text) for invalid_text in invalid_text_list]
        invalid_pattern = '|'.join(invalid_list)
        match = re.search(invalid_pattern,
                          page_text.lower())
        if match:
            return False
        return True

    @staticmethod
    def get_block_dict(doc):
        page_num = 1
        block_dict = {}
        page_length = 0
        for page in doc:
            if TextExtractor.is_valid_page(page):
                file_dict = page.get_text('dict')
                page_length = file_dict['height']
                block = file_dict['blocks']
                block_dict[page_num] = block
                page_num += 1
        return block_dict, page_length

    @staticmethod
    def get_style(block_dict):
        style = {}
        for page_num, blocks in block_dict.items():
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            ind = "{0}_{1}_{2}_{3}_{4}_{5}".format(span['size'], span['flags'], span['font'],
                                                                   span['color'],
                                                                   'upper' if span['text'].isupper() else 'lower',
                                                                   'nl' if re.match('^[\s]+[\.]*[\n]*$',
                                                                                    span['text']) or re.match(
                                                                       '^[\s]*[\.]*[\n]+$', span['text']) else 'text')

                            style[ind] = {'size': span['size'], 'flags': span['flags'], 'font': span['font'],
                                          'color': span['color'],
                                          'count': style[ind].get('count') + 1 if style.get(ind, 0) != 0 else 1,
                                          'case': 'upper' if span['text'].isupper() else 'lower'}

        style = sorted(style.items(), key=lambda x: x[1]['count'], reverse=True)

        return style

    @staticmethod
    def get_tag(style, bold_factor=1, uppercase_factor=1):
        try:
            p_style = style[0][0]
        except:
            raise ValueError('Cannot read this cv file. Check if the cv is an image.')
        p_size = style[0][1]['size']

        sizes = []
        for s in style:
            size = s[1]['size']
            if s[0].split('_')[-1] == 'nl':
                sizes.append(size)
                continue
            if 'bold' in s[1]['font'].lower():
                size += bold_factor
            if s[1]['case'] == 'upper':
                size += uppercase_factor
            sizes.append(size)
        sizes = np.unique(sizes)
        sizes = sorted(sizes, reverse=True)
        idx = 0
        tag = {}
        for size in sizes:
            idx += 1
            if size == p_size:
                idx = 0
                tag[size] = 'p'
            if size > p_size:
                tag[size] = 'h{0}'.format(idx)
            if size < p_size:
                tag[size] = 's{0}'.format(idx)
        return tag

    @staticmethod
    def preprocess(text):
        punctuation = '!"#$%&\'*;<+=>?[\\]^_`{|}~'
        # text = text.translate(str.maketrans('', '', punctuation)).strip()
        text = re.sub(' +', ' ', text)
        text = re.sub('•', ' ', text)
        text = re.sub('●', ' \n', text)
        text = re.sub('^[\s]*[\n]*$', ' ', text)
        text = re.sub('[\.]+', '.', text)
        text = re.sub('[\n]+', '\n', text)
        # text = re.sub('[\.\n]+', '.\n', text)
        return text

    @staticmethod
    def process_spans(spans):
        for i in range(len(spans)):
            if 'DeviceRGB' in spans.text[i]:
                spans.drop([i], inplace=True)

        spans.reset_index(drop=True, inplace=True)
        for special_case in ['topcv', 'nen tang', 'pid', 'cv', 'resume', 'page', 'p a g e', 'vitae']:
            spans.drop(spans[spans['text'].str.lower().str.contains(special_case)].index, inplace=True)
        spans.drop(spans[spans['text'].str.len() < 3 & spans['text'].str.contains('!|"|#|$|%|&|\'|~')].index,
                   inplace=True)
        spans.drop(spans[spans['text'].str.match(pat='^[1-9][\.]*[.\n]*$')].index, inplace=True)
        spans.drop(spans[spans['text'].str.contains('Page') & spans['text'].str.contains('of')].index, inplace=True)
        spans.drop_duplicates(['ymin', 'text'], inplace=True)
        spans.reset_index(drop=True, inplace=True)
        return spans

    @staticmethod
    def get_spans(block_dict, page_length, style, tag, bold_factor=1, uppercase_factor=1):
        spans = pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'tag'])
        rows = []
        for page_num, blocks in block_dict.items():
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        prev_xmax = 0
                        prev_ymin = 0
                        prev_ymax = 0
                        for span in line['spans']:
                            text = unidecode(span['text'])
                            text = TextExtractor.preprocess(text)
                            xmin, ymin, xmax, ymax = list(span['bbox'])
                            # print(xmin, ymin, xmax, ymax)
                            ymin += (page_num - 1) * page_length
                            ymax += (page_num - 1) * page_length
                            if (abs(prev_xmax - xmin) < 0.5) and (abs(prev_ymin - ymin) < 5) and (
                                    abs(prev_ymax - ymax) < 5):
                                try:
                                    # print("rows:", rows)
                                    rows[-1][4] += text
                                    prev_xmax = xmax
                                    prev_ymin = ymin
                                    prev_ymax = ymax
                                    continue
                                except:
                                    pass
                            prev_xmax = xmax
                            prev_ymin = ymin
                            prev_ymax = ymax
                            if (len(text) == 0):
                                continue
                            tag_size = span['size']
                            if "bold" in span['font'].lower():
                                tag_size += bold_factor
                            if span['text'].isupper():
                                tag_size += uppercase_factor
                            if re.match('^[\s]+[\.]*[\n]*$', span['text']) or re.match('^[\s]*[\.]*[\n]+$',
                                                                                       span['text']):
                                rows.append([xmin, ymin, xmax, ymax, text, 'p'])
                            else:
                                rows.append([xmin, ymin, xmax, ymax, text, tag[tag_size]])
                    rows[-1][4] += '.\n'
        spans = spans.append(pd.DataFrame(rows, columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'tag']))
        spans = TextExtractor.process_spans(spans)
        spans = spans.sort_values(by=['ymin', 'xmin'], ascending=True).head(len(spans)).reset_index(drop=True)
        return spans

    @staticmethod
    def get_lines(spans):
        lines = []
        for idx, row in spans.iterrows():
            flat_lines = list(itertools.chain(*lines))
            if idx not in flat_lines:
                top_a = row['ymin']
                bottom_a = row['ymax']
                line = [idx]
                for idx_2, row_2 in spans.iterrows():
                    if idx_2 not in flat_lines:
                        if not idx == idx_2:
                            top_b = row_2['ymin']
                            bottom_b = row_2['ymax']
                            if (top_a <= bottom_b) and (bottom_a >= top_b):
                                line.append(idx_2)
                lines.append(line)
        lines_df = pd.DataFrame({'lines': lines, 'line_index': [x for x in range(1, len(lines) + 1)]})
        lines_df = lines_df.set_index('line_index').lines.apply(pd.Series).stack().reset_index(level=0).rename(
            columns={0: 'lines'})
        lines_df['lines'] = lines_df['lines'].astype('int')
        return lines_df

    @staticmethod
    def sort_by_lines(spans, lines):
        spans = spans.merge(lines, left_on=spans.index, right_on='lines')
        spans.drop('lines', axis=1, inplace=True)
        spans = spans.sort_values(by=['line_index', 'ymin'], ascending=True).head(len(spans)).reset_index(drop=True)
        spans = spans.sort_values(by=['ymin', 'xmin'], ascending=True)
        return spans

    @staticmethod
    def get_headings(spans, tag_list, heading_patterns):

        max_h = len([e for e in tag_list if 'h' in e])

        heading_tag_filter_2 = '|'.join(tag_list[i] for i in range(min(1, max_h)))
        heading_tag_filter_1 = '|'.join(tag_list[i] for i in range(max(min(2, max_h), int(0.8 * len(tag_list)))))
        heading_tag_filter_3 = '|'.join(tag_list[i] for i in range(max(min(2, max_h), int(0.4 * len(tag_list)))))

        headings_3 = headings_4 = headings_1 = spans[
            spans['text'].str.lower().str.replace(" ", "", regex=True).str.contains(pat=heading_patterns)]

        headings_1 = headings_1[headings_1['text'].str.replace(" ", "", regex=True).str.len() < 30]
        headings_1 = headings_1[headings_1['text'].str.replace(" ", "", regex=True).str.len() > 5]

        headings_1 = headings_1[headings_1['tag'].str.contains(heading_tag_filter_1)]

        headings_2 = spans[spans['text'].str.isupper() | spans['text'].str.istitle()]
        headings_2 = headings_2[headings_2['text'].str.replace(" ", "").str.len() < 30]
        headings_2 = headings_2[headings_2['text'].str.replace(" ", "").str.len() > 5]
        headings_2 = headings_2[headings_2['tag'].str.fullmatch(heading_tag_filter_2)]

        headings_4 = headings_4[headings_4['text'].str.isupper() | headings_4['text'].str.istitle()]
        headings_4 = headings_4[headings_4['text'].str.len() < 30]
        headings_4 = headings_4[headings_4['text'].str.len() > 5]
        headings_4 = headings_4[headings_4['tag'].str.fullmatch(heading_tag_filter_3)]

        headings_3 = headings_3[headings_3['text'].str.isupper()]
        headings_3 = headings_3[headings_3['text'].str.len() < 30]
        headings_3 = headings_3[headings_3['text'].str.len() > 5]

        # headings_3 = headings_3[headings_3['text'].str.replace(".", " ", regex=True).str.replace("\n",
        # "").str.split().str.len() < 3]

        headings = headings_1.append(headings_2)
        headings = headings.append(headings_3)
        headings = headings[~headings['text'].str.lower().str.contains('project|^at$', regex=True)]
        headings = headings.append(headings_4)

        headings = headings.drop_duplicates()
        headings = headings[~headings['text'].str.match(pat='^[\.]*[\n]+$')]
        headings = headings[
            ~headings['text'].str.replace("\n", "", regex=True).str.replace(".", "", regex=True).str.strip().str[
             :-1].str.contains(':|,', regex=True)]
        headings_extra = headings
        headings = headings[
            ~headings['text'].str.replace("\n", "", regex=True).str.replace(".", "", regex=True).str.strip().str[
             0:].str.contains("\d", regex=True)]
        headings_extra = headings_extra[headings_extra['text'].str.lower().str.contains('work|experience')]
        headings = headings.append(headings_extra)
        headings = headings.drop_duplicates()
        headings = headings[~headings['text'].str.islower()]

        return headings

    @staticmethod
    def get_heading_region(spans, headings, heading, heading_index, page_length):
        """
        Params:
        - spans
        - headings - list of headings in the CV
        - heading_index - the heading of text block
        Return:
        - right_border: the biggest xmax value inside the text block (include the heading)
        - left_border: the smallest xmin value insde the text block (include the heading)
        """
        right_border = heading.xmax
        left_border = heading.xmin

        if heading.ymin > page_length:
            return left_border, right_border

        heading_index_list = headings[headings.index != heading_index].index.values.tolist()
        heading_position = 0

        for i in range(len(spans)):
            if spans.index[i] == heading_index:
                heading_position = i
                break

        next_span = spans.iloc[heading_position]
        next_span_index = spans.index[heading_position]

        while not next_span_index in heading_index_list:

            if TextExtractor.is_overlap(heading.xmin, heading.xmax, next_span.xmin, next_span.xmax,
                                        threshold=10):

                if next_span.xmin < left_border:
                    left_border = next_span.xmin

                if next_span.xmax > right_border:
                    right_border = next_span.xmax

            if heading_position == spans.shape[0] - 1:
                break

            heading_position += 1
            next_span = spans.iloc[heading_position]
            next_span_index = spans.index[heading_position]

        return left_border, right_border

    @staticmethod
    def is_overlap(a_left, a_right, b_left, b_right, threshold=50):
        """
        Argument:
        - a_left, a_right: the x-coordinate of the first text block's left and right border
        - b_left, b_right: the second text block
        Return:
        - True:
            1. If two text block area overlap more than threshold (default: 50 pixel)
            2. If one of two text block is inside another
        - Fasle
        """
        result = (max(0, min(a_right, b_right) - max(a_left, b_left)) > threshold)
        result = ((a_left > b_left) and (a_right < b_right)) or result
        result = ((b_left > a_left) and (b_right < a_right)) or result

        return result

    @staticmethod
    def check_columns(spans, headings):
        heading_filter = '|'.join(heading for heading, tag in zip(headings['text'], headings['tag']))
        spans['xmid'] = (spans['xmin'] + spans['xmax']) / 2
        heading_xmin = np.array(spans[spans['text'].str.contains(heading_filter)]['xmin'])
        heading_xmax = np.array(spans[spans['text'].str.contains(heading_filter)]['xmax'])
        heading_xmid = np.array(spans[spans['text'].str.contains(heading_filter)]['xmid'])
        if np.min(heading_xmax) < np.max(heading_xmid):
            # print('cv have 2 columns')
            return True
        return False

    @staticmethod
    def split_col(spans, headings, heading_patterns, page_length, threshold=120):
        # spans = spans[~spans['tag'].str.contains('s')].copy()
        avg_xmid = 0
        diff_xmin = 0
        heading_max_xmin = None
        heading_min_xmin = None
        label = 1

        headings = headings.sort_values(by=['ymin'], ascending=True)

        if headings.empty:
            columns = np.ones(len(spans), dtype=bool)
            spans['column'] = columns
            label = 1
        else:

            # Get the border of each heading
            left_border = []
            right_border = []

            for i, (index, row) in enumerate(headings.iterrows()):
                left, right = TextExtractor.get_heading_region(spans, headings, row, index, page_length)
                left_border.append(left)
                right_border.append(right)

            headings['left_border'] = left_border
            headings['right_border'] = right_border
            heading_filter = '|'.join(heading for heading in headings['text'])

            spans['xmid'] = (spans['xmin'] + spans['xmax']) / 2

            heading_xmid = headings['xmid']

            max_xmid = np.max(heading_xmid)
            min_xmid = np.min(heading_xmid)

            # Get the left most and right most heading
            heading_xmin = headings.xmin.values.tolist()
            max_xmin = np.max(heading_xmin).item()
            min_xmin = np.min(heading_xmin).item()

            heading_max_xmin = headings[headings['xmin'] == max_xmin].iloc[0]
            left_headings = headings[abs(headings['xmin'] - min_xmin) < 20]
            match = re.search(heading_patterns, left_headings.iloc[0]['text'].lower())

            if left_headings.shape[0] > 1 and not match:
                heading_min_xmin = headings.loc[left_headings[1:]['right_border'].idxmax()]
            else:
                heading_min_xmin = headings.loc[left_headings['right_border'].idxmax()]

            diff_xmin = abs((max_xmin - min_xmin))
            # print("Heading min:", heading_min_xmin)
            # print("Heading max:", heading_max_xmin)

            # avg_xmid = ((np.max(heading_xmid)+np.min(heading_xmid))/2 + np.max(heading_xmid))/2
            avg_xmid = (heading_max_xmin.left_border + heading_min_xmin.right_border) / 2

            if not TextExtractor.is_overlap(heading_max_xmin.left_border, heading_max_xmin.right_border,
                                            heading_min_xmin.left_border,
                                            heading_min_xmin.right_border) and diff_xmin > threshold:
                label = 2
                # print("2 col")
                columns = []
                columns = (spans['xmid'] < avg_xmid)
                spans['column'] = columns
                spans['column'] = spans['column'].replace({True: 1, False: 2})
            else:
                # print("1 col")
                columns = np.ones(len(spans), dtype=bool)
                spans['column'] = columns

        spans = spans.sort_values(by=['column', 'ymin'], ascending=True)
        # spans = TextExtractor.postprocess_spans(spans, headings, ner_model)
        return spans, label, avg_xmid

    @staticmethod
    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        # print('start checking')
        for ele in ['present', 'now', 'current']:
            if ele in string.lower():
                if len(string.split()) == 1:
                    return True
        try:
            # print('String: ',string)
            parse(string, fuzzy=fuzzy)
            # print('ok')
            return True
        except:
            return False

    @staticmethod
    def checkDuration(cv):
        temp_date = ''  # chau
        i = 1  # chau
        numOfRows = 0  # chau
        for row in cv:
            if TextExtractor.is_date(row) or 'present' in row.lower():
                if i % 2 == 1:
                    numOfRows = 0  # chau
                else:
                    if numOfRows <= 3:
                        return True
                i += 1
            numOfRows += 1
        return False

    @staticmethod
    def postprocess(text):
        text = re.sub('[\.]+', '.', text)
        text = re.sub('[\n]+', '\n', text)
        text = re.sub('[\.]+[\n]+', '.\n', text)
        text = re.sub('[\.\n]+[\s]+[\.\n]+', '.\n', text)
        return text

    @staticmethod
    def join_date(spans, threshold=3):

        index_list = []
        previous_date_index = 0
        current_date_index = 0

        # print(spans['text'])

        for index, row in spans.iterrows():

            current_text = row['text'].replace("\n", "").strip()
            current_tag = row['tag']
            current_xmid = row['xmid']
            current_ymin = row['ymin']

            previous_ymin = spans['ymin'][previous_date_index]
            previous_text = spans['text'][previous_date_index]
            previous_tag = spans['tag'][previous_date_index]
            previous_xmid = spans['xmid'][previous_date_index]

            if TextExtractor.is_date(current_text) and len(current_text.strip()) < 20:

                if (
                        index - previous_date_index <= threshold) and previous_date_index != 0 and current_tag == previous_tag and (
                        abs(current_xmid - previous_xmid) < 5 or abs(current_ymin - previous_ymin) < 5):
                    spans.at[previous_date_index, 'text'] = spans['text'][previous_date_index].replace(".\n",
                                                                                                       "").replace("-",
                                                                                                                   "") \
                                                            + ' - ' + spans['text'][index]
                    previous_date_index = 0
                    index_list.append(index)
                else:
                    previous_date_index = index

        spans.drop(index_list, inplace=True)
        spans.reset_index(drop=True, inplace=True)

        return spans

    @staticmethod
    def join_sentence(spans):

        index_list = []
        previous_date_index = 0
        current_date_index = 0

        for index in range(len(spans) - 1, 0, -1):

            current_text = spans['text'][index].strip()
            current_tag = spans['tag'][index]
            current_first_word = current_text.split()[0]

            previous_text = spans['text'][index - 1].strip()
            previous_tag = spans['tag'][index - 1]
            previous_last_word = previous_text.split()[-1].replace("\n", "").replace(".", "")

            if previous_tag == current_tag and current_first_word.islower():

                while previous_text[-1] in ['.', '\n']:
                    previous_text = previous_text[:-1]

                spans.at[index - 1, 'text'] = previous_text + " " + current_text
                index_list.append(index)

        spans.drop(index_list, inplace=True)
        spans.reset_index(drop=True, inplace=True)

        return spans

    @staticmethod
    def merge_textblock(texts, headings, heading_patterns):
        index_list = []
        new_text_block = ""
        new_special_text_block = ""
        special_heading = None
        for index, (text_block, heading) in enumerate(zip(texts, headings)):
            if not re.search(heading_patterns, heading.lower()):
                heading = heading.replace("\n", "").replace(".", "")
                if heading != '' and len(heading.split()) > 1:
                    if special_heading is None:
                        special_heading = heading.replace("\n", "").replace(".", "").strip()
                    new_special_text_block = new_special_text_block + text_block
                    index_list.append(index)
                else:
                    new_text_block += text_block
                    index_list.append(index)

        for index in sorted(index_list, reverse=True):
            del texts[index]
            del headings[index]

        new_text_block = new_special_text_block + new_text_block

        if special_heading is None:
            new_heading = new_text_block.split(".\n")[0]
            if len(new_heading.split()) < 5:
                special_heading = new_heading
            else:
                special_heading = "ADDITIONAL PERSONAL INFORMATION"
        texts = [((new_text_block))] + texts
        headings = [(special_heading)] + headings
        return texts, headings

    @staticmethod
    def get_text(pdf_file=None, pdf_path=None, pattern_path="service/src/modules/textextraction/v1/"):

        # Step 1
        if pdf_file is not None:
            doc = fitz.open(stream=pdf_file, filetype="pdf")
        else:
            doc = fitz.open(pdf_path)
        block_dict, page_length = TextExtractor.get_block_dict(doc)

        # Step 2
        style = TextExtractor.get_style(block_dict)
        tag = TextExtractor.get_tag(style)
        heading_patterns = TextExtractor.get_pattern_from_file(pattern_path)

        size_list = sorted(list(tag.keys()))
        for i in range(1, len(size_list)):
            if abs(size_list[i] - size_list[i - 1]) < 0.3:
                if tag[size_list[i - 1]] != 'p' and tag[size_list[i]] != 'p':
                    tag[size_list[i]] = tag[size_list[i - 1]]

        spans = TextExtractor.get_spans(block_dict, page_length, style, tag)
        spans = spans[
            spans['text'].str.replace("\n", "", regex=True).str.replace(".", "", regex=True).str.strip().str.len() > 2]
        spans.reset_index(drop=True, inplace=True)

        # Step 3
        tag_reverse = {v: k for k, v in tag.items()}
        tag_list = sorted(np.unique(spans['tag']), key=lambda x: tag_reverse[x], reverse=True)
        lines = TextExtractor.get_lines(spans)
        spans = TextExtractor.sort_by_lines(spans, lines)
        spans.reset_index(drop=True, inplace=True)

        # Step 4
        spans['xmid'] = (spans['xmin'] + spans['xmax']) / 2
        headings = TextExtractor.get_headings(spans, tag_list, heading_patterns)

        # Step 5
        spans, label, avg_xmid = TextExtractor.split_col(spans, headings, heading_patterns, page_length)
        spans.reset_index(drop=True, inplace=True)

        spans = TextExtractor.join_date(spans)
        spans = TextExtractor.join_sentence(spans)

        # step 6
        cols = sorted(spans.column.unique(), reverse=False)
        texts = []
        types = []
        heading_list = [e.replace("\n", "").replace(".", "").replace(" ", "") for e in list(headings['text'].values)]

        heading = ''
        for col in cols:
            tmp = ''
            col_df = spans[spans['column'] == col]
            temp_date = ''  # chau
            duration = []  # chau
            i = 1  # chau
            numOfRows = 0  # chau
            if TextExtractor.checkDuration(col_df['text'].values):
                heading = ''
                for row in col_df['text'].values:

                    if TextExtractor.is_date(row) and len(row.rstrip()) <= 20:
                        if i % 2 == 1:
                            temp_date = row.rstrip()  # .replace('-', '')
                            numOfRows = 0  # chau
                            i += 1
                        else:
                            if 'present' in row.lower():
                                temp_date += ' Present' + '.\n'
                            else:
                                if 'now' in row.lower():
                                    temp_date += ' Now' + '.\n'
                                else:
                                    if 'current' in row.lower():
                                        temp_date += ' Current' + '.\n'
                                    else:
                                        temp_date += ' ' + row + '.\n'
                            if numOfRows <= 3:
                                tmp += temp_date.replace('.', '') + '.\n'
                                duration.append(temp_date.replace('.', ''))
                            i += 1
                    if row.replace("\n", "").replace(".", "").replace(" ", "") in heading_list:
                        if re.search(heading_patterns, row.replace("\n", "").replace(".", "").replace(" ", "").lower()):
                            row = ' '.join(wordninja.split(row.replace("\n", "").replace(".", "").replace(" ", "")))
                        types.append(heading)
                        texts.append(tmp)
                        tmp = row + '.\n'
                        heading = row
                    else:
                        if not TextExtractor.is_date(row):
                            tmp += row + '.\n'
                    numOfRows += 1
            else:
                heading = ''
                for row in col_df['text'].values:
                    if row.replace("\n", "").replace(".", "").replace(" ", "") in heading_list:
                        if re.search(heading_patterns, row.replace("\n", "").replace(".", "").replace(" ", "").lower()):
                            row = ' '.join(wordninja.split(row.replace("\n", "").replace(".", "").replace(" ", "")))
                        types.append(heading)
                        texts.append(tmp)
                        tmp = row + '.\n'
                        heading = row
                    else:
                        tmp += row + '.\n'
            types.append(heading)
            texts.append(tmp)

        for i in range(len(texts)):
            texts[i] = TextExtractor.postprocess(texts[i])

        for i in range(len(texts) - 1, -1, -1):
            texts[i] = re.sub('^[\s]+[\.]*$', '', texts[i])
            if len(texts[i]) == 0:
                del texts[i]
                del types[i]

        assert len(texts) == len(types)

        texts = [e.replace("\n.", ".\n").replace("(.\n", " .\n") for e in texts]
        texts, types = TextExtractor.merge_textblock(texts, types, heading_patterns)
        return texts, types, label
