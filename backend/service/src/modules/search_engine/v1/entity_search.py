import os
import re
import dateparser
import datetime
from service.src.modules.search_engine.v1.elastic_search import ElasticSearch


class EntityExtractor():

    @staticmethod
    def get_entity_position(entity: str, text: str, index_type='exact'):
        if index_type == 'exact':
            return text.lower().index(entity.lower())
        if index_type == 'relevant':
            for smaller_ent in entity.split():
                if 'skill' not in smaller_ent:
                    try:
                        return text.lower().index(smaller_ent.lower())
                    except:
                        continue
        return 1e8

    # Get duration by regex
    @staticmethod
    def get_duration(text: str):
        # Sep 2015 - July 2017
        format1 = '(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct' \
                  '|October|Nov|November|Dec|December)\s[\d]{4}\s-\s(' \
                  'Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct' \
                  '|October|Nov|November|Dec|December)\s[\d]{4}'
        # 2012 - 2016
        format2 = '[\d]{4}\s-\s[\d]{4}'
        # Jan-2019 - Present
        format3 = '(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct' \
                  '|October|Nov|November|Dec|December)-[\d]{4}\s-\s[A-Z|a-z]{7}|(' \
                  'Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct' \
                  '|October|Nov|November|Dec|December)\s[\d]{4}\s-\s(present|now|current)'
        # 2014 – present
        format4 = '[\d]{4}\s-\s(present|now|current)'
        # 2021
        format5 = '(19|20)[\d]{2}'
        # 3/2012 - 2/2016
        format6 = '([\d]{1,2}[/])*[\d]{4}\s-\s([\d]{1,2}[/])*[\d]{4}'
        # 3/2012 - present, now
        format7 = '([\d]{1,2}[/])*[\d]{4}\s-\s(present|now|current)'

        date = re.compile(
            format1 + '|' + format2 + '|' + format3 + '|' + format4 + '|' + format5 + '|' + format6 + '|' + format7,
            re.IGNORECASE)
        duration = date.finditer(text)
        return [x.group() for x in duration]

    @staticmethod
    def get_email(text: str):
        email = ''
        email_regex = re.compile(
            r'''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])''',
            re.IGNORECASE)
        groups = email_regex.findall(text)
        for g in groups:
            email = ("".join(g))
        return email

    @staticmethod
    def get_dob(text: str):
        text = text.replace('\n', " ").replace(',', " ").replace('-', " ").replace('/', " ")
        date_of_birth = ''
        dob = re.compile(
            r'(?:\bbirth\b|\bbirth|\bdob\b|\bdob(?:day|date)).{0,20}\n? \b((?:(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?\s+(?:of\s+)' \
            + r'?(?:jan\.?|january|1|01|feb\.?|february|2|02|mar\.?|march|3|03|apr\.?|april|4|04|may|5|05|jun\.?|june|6|06|jul\.?|july|7|07|aug\.?|august|8|08|sep\.?|september|9|09|oct\.?|october|10|nov\.?|november|11|dec\.?|december|12)' \
            + r'|(?:jan\.?|january|1|01|feb\.?|february|2|02|mar\.?|march|3|03|apr\.?|april|4|04|may|5|05|jun\.?|june|6|06|jul\.?|july|7|07|aug\.?|august|8|08|sep\.?|september|9|09|oct\.?|october|10|nov\.?|november|11|dec\.?|december|12)' \
            + r'\s+(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?)(?:\,)?\s*(?:\d{4})?|\b[0-3]?\d[-\./][0-3]?\d[-\./]\d{2,4})\b',
            re.IGNORECASE | re.MULTILINE)
        ls = dob.findall(text)
        for l in ls:
            date_of_birth = ("".join(l))
            try:
                date_of_birth = dateparser.parse(date_of_birth, settings={'DATE_ORDER': 'DMY'}).strftime("%d-%m-%Y")
            except:
                date_of_birth = dateparser.parse(date_of_birth, settings={'DATE_ORDER': 'MDY'}).strftime("%m-%d-%Y")
        if date_of_birth != "":
            try:
                date_time_obj = datetime.strptime(date_of_birth, '%d-%m-%Y')
                date_of_birth = datetime.strftime(date_time_obj, "%Y-%m-%d")
            except:
                pass
        return date_of_birth

    @staticmethod
    def get_phone_number(text: str):
        text = text.replace('\n', ".").replace(' ', "").replace('-', " ").replace('(', "").replace(')', "").replace('.',
                                                                                                                    "").replace(
            ':', " ")
        text = re.sub(r'(19|20)([0-9][0-9])?(.|-|\s)?(.|-|\s)?(.|-|\s)(19[0-9][0-9]|20[0-9][0-9])', '', text)
        text = re.sub("[A-Za-z]+", lambda ele: f' {ele[0]} ', text)
        phone_number = ''
        phone_regex = re.compile(r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}")
        groups = phone_regex.findall(text)
        for g in groups:
            phone_number = ("".join(g))
        return phone_number

    @staticmethod
    def get_education_level(text: str):

        edulevel = ''
        edulevel_regex = re.compile(
            r'\b(Associate\'?[sd ]|Master\'?[s ]|Bachelor\'?[s ]|Ph\. ?D|Doctora[TE|L]|Doctor|B\.?[ES]|M\.?[ES]|B\.?TECH|M\.?TECH|SSC|HSC|CBSE|ICSE)',
            re.IGNORECASE | re.MULTILINE)
        groups = edulevel_regex.findall(text)
        for g in groups:
            edulevel = ("".join(g))
        edulevel = edulevel.replace(' ', '')
        return edulevel

    @staticmethod
    def get_gpa(text: str):
        gpa = ''
        gpa_regex = re.compile(r'(\bgpa[ :]+)?(\d+(?:\.\d+)?)?(\/)(\d+(?:\.\d+)?)(?(1)| *gpa\b)', re.I)
        gpa_regex_1 = re.compile(r'(\bgpa[ :]+)?(\d+(?:\.\d+)?)[/\.\d+ ]{0,6}(?(1)| *gpa\b)', re.I)
        groups = gpa_regex.findall(text)
        for g in groups:
            gpa = ("".join(g))
        gpa = ''.join(char for char in gpa if char.isdigit() or char == '.' or char == ',' or char == '/')
        if not gpa:
            groups_1 = gpa_regex_1.findall(text)
            for g in groups_1:
                gpa = ("".join(g))
            gpa = ''.join(char for char in gpa if char.isdigit() or char == '.' or char == ',' or char == '/')
        return gpa

    @staticmethod
    def parse_duration(text: str):
        duration = text.lower()
        duration = duration.replace(str('from'), '').replace(':', '')
        duration = re.sub('[to]', '-', duration)
        duration_json = {
            '-c--ber': 'october',
            '-c-': 'oct',
            'augus-': 'august',
            'sep-ember': 'september',
            'n-v': 'nov',
            'n-vember': 'november',
            'n-w': 'now',
            'presen-': 'present',
            'recen-': 'recent',
            '-ill': '',
            'un-il': '-',
            '--': '-'
        }
        for k, v in duration_json.items():
            if k in duration:
                duration = duration.replace(k, v).replace(str('--'), '-')

        duration = duration.split('-')
        if len(duration) == 2:
            duration_from = duration[0].strip()
            try:
                duration_to = duration[1].strip().lower()
            except:
                duration_to = ''
        elif len(duration) == 3:
            duration_from = duration[0].strip()
            duration_from = duration_from + duration[1]
            try:
                duration_to = duration[2].strip().lower()
            except:
                duration_to = ''
        elif len(duration) == 4:
            duration_from = duration[0].strip()
            duration_from = duration_from + duration[1]
            try:
                duration_to = duration[2].strip().lower()
                duration_to = duration_to + duration[3]
            except:
                duration_to = ''
        else:
            duration_from = duration[0].strip()
            try:
                duration_to = duration[1].strip().lower()
            except:
                duration_to = ''
        duration_to_fix = ''
        if duration_to in ['present', 'recent']:
            duration_to_fix = 'now'
            final_from = dateparser.parse(duration_from,
                                          settings={'DATE_ORDER': 'DMY', 'PREFER_DAY_OF_MONTH': 'first'}).strftime(
                "%d-%m-%Y")
            final_to = dateparser.parse(duration_to_fix,
                                        settings={'DATE_ORDER': 'DMY', 'PREFER_DAY_OF_MONTH': 'last'}).strftime(
                "%d-%m-%Y")
        else:
            final_from = dateparser.parse(duration_from,
                                          settings={'DATE_ORDER': 'DMY', 'PREFER_DAY_OF_MONTH': 'first'}).strftime(
                "%d-%m-%Y")
            try:
                final_to = dateparser.parse(duration_to,
                                            settings={'DATE_ORDER': 'DMY', 'PREFER_DAY_OF_MONTH': 'last'}).strftime(
                    "%d-%m-%Y")
            except:
                final_to = ''

        return final_from, final_to

    @staticmethod
    def get_dob(text: str):
        text = text.replace('\n', " ").replace(',', " ").replace('-', " ").replace('/', " ")
        date_of_birth = ''
        dob = re.compile(
            r'(?:\bbirth\b|\bbirth|\bdob\b|\bdob(?:day|date)).{0,20}\n? \b((?:(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?\s+(?:of\s+)' \
            + r'?(?:jan\.?|january|1|01|feb\.?|february|2|02|mar\.?|march|3|03|apr\.?|april|4|04|may|5|05|jun\.?|june|6|06|jul\.?|july|7|07|aug\.?|august|8|08|sep\.?|september|9|09|oct\.?|october|10|nov\.?|november|11|dec\.?|december|12)' \
            + r'|(?:jan\.?|january|1|01|feb\.?|february|2|02|mar\.?|march|3|03|apr\.?|april|4|04|may|5|05|jun\.?|june|6|06|jul\.?|july|7|07|aug\.?|august|8|08|sep\.?|september|9|09|oct\.?|october|10|nov\.?|november|11|dec\.?|december|12)' \
            + r'\s+(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?)(?:\,)?\s*(?:\d{4})?|\b[0-3]?\d[-\./][0-3]?\d[-\./]\d{2,4})\b',
            re.IGNORECASE | re.MULTILINE)
        ls = dob.findall(text)
        for l in ls:
            date_of_birth = ("".join(l))
            try:
                date_of_birth = dateparser.parse(date_of_birth, settings={'DATE_ORDER': 'DMY'}).strftime("%d-%m-%Y")
            except:
                date_of_birth = dateparser.parse(date_of_birth, settings={'DATE_ORDER': 'MDY'}).strftime("%m-%d-%Y")
        if date_of_birth != "":
            try:
                date_time_obj = datetime.strptime(date_of_birth, '%d-%m-%Y')
                date_of_birth = datetime.strftime(date_time_obj, "%Y-%m-%d")
            except:
                pass
        return date_of_birth

    @staticmethod
    def remove_duplication(entities_list: list):
        """
        Remove the duplicated entities or entities that are inside other
        Params:
            - entities_list: list of entities extracted
        Return:
            - new_output: cleaned list of entities
        """

        # Create a copy of entities list
        output = entities_list
        new_output = []

        # Remove duplicate entities in the list
        # Create list of removed items
        removed_list = []

        for current_index in range(len(output)):
            for index in range(len(output)):
                if index != current_index:
                    if index not in removed_list:
                        current_text = output[current_index][2]
                        text = output[index][2]
                        if output[index][0] == output[current_index][0]:
                            if current_text in text \
                                    and output[current_index][1] >= output[index][1] \
                                    and output[current_index][1] + len(current_text) \
                                    <= output[index][1] + len(text):
                                removed_list.append(current_index)

        for index in range(len(output)):
            if index not in removed_list:
                new_output.append(output[index])

        new_output.sort(key=lambda x: (x[1], x[2]))

        return new_output

    def extract_entities_by_regex(text):
        """
        Extract entities only using Regex
        Params:
            - text: input text need extracting entities
        Return:
            - list of entities
            - For each entity, return a tuple containing type of entity, position in the
            original text, and the name of entity.
        """
        # Create an empty list to store the entities
        output = []

        # Get duration by regex
        duration_list = EntityExtractor.get_duration(text)
        for duration in duration_list:
            du_start_char = EntityExtractor.get_entity_position(duration, text)
            output.append(('DURATION', du_start_char, duration.replace("\n", " ").strip()))

        email = EntityExtractor.get_email(text.replace("\n", " ").replace(".\n", "  "))
        phone_number = EntityExtractor.get_phone_number(text.replace("\n", " ").replace(".\n", "  "))
        dob = EntityExtractor.get_dob(text.replace("\n", " ").replace(".\n", "  "))
        if email != '':
            output.append(("EMAIL", 0, email))
        if phone_number != '':
            output.append(("PHONE_NUMBER", 0, phone_number))
        if dob != '':
            output.append(("DATE_OF_BIRTH", 0, dob))

        # Sort the output by position order
        output.sort(key=lambda x: x[1])

        return output

    # Extract the entities only using Elastic Search + Regex
    @staticmethod
    def extract_entities_by_elastic(text, extract_relevant=True):
        """
        Extract entities only using ElasticSearch
        Params:
            - text: input text needs extracting entities
        Return:
            - list of entities
            - for each entity, return a tuple containing type of entity, position in the
            original text, and the name of entity.
        """

        # Create an empty list to contain entities
        output = []

        # Extract Hard / Programming / Computer Skills
        skill_list = ElasticSearch.get_skill(text)
        if skill_list:
            skill_list = list(set(skill_list))
            for skill in skill_list:
                try:
                    output.append(('SKILL', EntityExtractor.get_entity_position(skill, text), skill))
                except ValueError:
                    if extract_relevant:
                        output.append(
                            ('RELEVANT_SKILL', EntityExtractor.get_entity_position(skill, text, index_type='relevant'),
                             skill))
                    else:
                        continue

        # Extract Soft Skills
        soft_skill_list = ElasticSearch.get_softskill(text)
        if soft_skill_list:
            soft_skill_list = list(set(soft_skill_list))
            for skill in soft_skill_list:
                try:
                    output.append(('SOFT_SKILL',
                                   EntityExtractor.get_entity_position(skill, text),
                                   skill))
                except ValueError:
                    if extract_relevant:
                        output.append(('RELEVANT_SOFT_SKILL',
                                       EntityExtractor.get_entity_position(skill, text, index_type='relevant'), skill))
                    else:
                        continue

        # Extract Language Skills
        language_skill = ElasticSearch.get_languageskill(text)
        if language_skill:
            language_skill = list(set(language_skill))
            for skill in language_skill:
                try:
                    output.append(('LANG_SKILL',
                                   EntityExtractor.get_entity_position(skill, text), skill))
                except ValueError:
                    if extract_relevant:
                        output.append(('RELEVANT_LANG_SKILL',
                                       EntityExtractor.get_entity_position(skill, text, index_type='relevant'), skill))
                    else:
                        continue

        # Extract Language Skills
        job_title = ElasticSearch.get_jobtitle(text)
        if job_title:
            job_title = list(set(job_title))
            for job in job_title:
                try:
                    output.append(('JOB_TITLE',
                                   EntityExtractor.get_entity_position(job, text), job))
                except ValueError:
                    if extract_relevant:
                        output.append(('RELEVANT_JOB_TITLE',
                                       EntityExtractor.get_entity_position(job, job, index_type='relevant'),
                                       job))
                    else:
                        continue

        output.sort(key=lambda x: x[1])

        return output

    # Extract the entities by combining the NER model + ElasticSearch + Regex
    @staticmethod
    def extract_entities(text, heading='default', extract_relevant=True):
        """
        Extract entities from text using all methods
        Params:
            - text: the input text needs extracting the entities
        Return:
            - A list of entities
            - For each entity, return a tuple containing type of entity, the position in
            the original text, and the name of entity.
        """
        # Create an empty input
        output = []

        # Extract the entities using regex
        output += EntityExtractor.extract_entities_by_regex(text)


        # Extract the entities using elastic
        # output += self.extract_entities_by_elastic(text, extract_relevant)

        # Sort the list of output in position order
        output.sort(key=lambda x: (x[1], x[2]))
        for i in range(len(output) - 1, 0, -1):
            if output[i][0] == output[i - 1][0] \
                    and output[i][1] == output[i - 1][1] + len(output[i - 1][2]):
                output[i - 1] = (output[i - 1][0], output[i - 1][1], output[i - 1][2] + output[i][2])

        # Remove duplication
        output = EntityExtractor.remove_duplication(output)

        # Sort the list of output in position order
        output.sort(key=lambda x: (x[1], x[2]))

        return output

    @staticmethod
    def extract(segment: tuple, entities_list=None):
        """
        Default method to extract the entities
        Params:
            - segment: (tuple) the text block needs extracting entities
            - entities_list: list of important entities
        Return:
            - entities: a dictionary contains all of entities found in the segment
        """

        if entities_list is None:
            entities_list = []

        # Get the string from segment
        text = str(segment[0])
        entities = {}

        # Create an empty list to contain entities
        output = []
        index_list = []

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

        output += EntityExtractor.extract_entities(text)
        output.sort(key=lambda x: (x[1], x[2]))
        output = EntityExtractor.remove_duplication(output)

        output += EntityExtractor.extract_entities_by_elastic(text)

        for item in output:
            key = item[0]
            val = item[2]
            entities[key] = entities.get(key, []) + [val]

        return entities, segment[1]
