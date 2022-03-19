from service.src.modules.search_engine.v1.entity_search import EntityExtractor
from service.src.modules.textextraction.v1.TextExtractor import TextExtractor
import re
from datetime import datetime


class Parser():

    def __init__(self):
        self.work_experiences = []
        self.educations = []
        self.summary = []
        self.personal_information = None
        self.projects = []
        self.skills = []
        self.soft_skills = []
        self.lang_skills = []
        self.work_experience_headers = ['experience',
                                        'workexperience',
                                        'employment',
                                        'history',
                                        'work',
                                        'workingexperience']
        self.education_headers = ["education", "academ"]
        self.project_headers = ['project']
        self.recent_job_title = ""
        self.recent_date = None

    def convert_to_dict(self):
        return {
                "personal_information": self.personal_information,
                "summary": self.summary,
                "education": self.educations,
                "work_experience": self.work_experiences,
                "projects": self.projects,
                "program_skill": [e.upper() for e in list(set([e.lower() for e in self.skills]))],
                "soft_skill": [e.upper() for e in list(set([e.lower() for e in self.soft_skills]))],
                "lang_skill": [e.upper() for e in list(set([e.lower() for e in self.lang_skills]))]
        }

    @staticmethod
    def diff_months(d2, d1):
        try:
            return (d1.year - d2.year) * 12 + d1.month - d2.month
        except:
            return 1


    def parse_experience(self, passage_index, entity_dict):

        duration_list = []
        job_title_list = []
        relevant_job_title_list = []
        du_to = None
        raw_duration = {
            "raw": None,
            "du_from": None,
            "du_to": None,
            "months": None,
            "years": None
        }
        for key, val in entity_dict.items():
            if key == "DURATION":
                duration = {
                    "raw": val,
                    "du_from": None,
                    "du_to": None,
                    "months": None,
                    "years": None
                }
                try:
                    du_from, du_to = EntityExtractor.parse_duration(val[0])
                    du_from = datetime.strptime(du_from, '%d-%m-%Y')
                    du_to = datetime.strptime(du_to, '%d-%m-%Y')
                    diff_months = Parser.diff_months(du_from, du_to)
                    duration['du_from'] = datetime.strftime(du_from, '%d-%m-%Y')
                    duration['du_to'] = datetime.strftime(du_to, '%d-%m-%Y')
                    duration['months'] = diff_months - 12*int(diff_months / 12)
                    duration["years"] = int(diff_months / 12)
                except:
                    pass
                duration_list.append(duration)

            if key == "JOB_TITLE":
                job_title_list.append(val)
            if key == "RELEVANT_JOB_TITLE":
                relevant_job_title_list.append(val)

        exp_dict = {
            "id": len(self.work_experiences),
            "passage_id": passage_index,
            "work_duration": duration_list[0] if duration_list else raw_duration,
            "job_title": job_title_list[0] if job_title_list else ["unknown"],
            "relevant_job_title": relevant_job_title_list[0] if relevant_job_title_list else ["unknown"]
        }

        if self.recent_date is None or Parser.diff_months(self.recent_date, du_to):
            self.recent_date = du_to
            self.recent_job_title = job_title_list[0][0] if job_title_list else ["Job Applicant"]

        self.work_experiences.append(exp_dict)

    def parse_project(self, passage_index, entity_dict):

        duration_list = []
        job_title_list = []
        relevant_job_title_list = []
        raw_duration = {
            "raw": None,
            "du_from": None,
            "du_to": None,
            "months": None,
            "years": None
        }

        for key, val in entity_dict.items():
            if key == "DURATION":
                duration = {
                    "raw": val,
                    "du_from": None,
                    "du_to": None,
                    "months": None,
                    "years": None
                }
                try:
                    du_from, du_to = EntityExtractor.parse_duration(val[0])
                    du_from = datetime.strptime(du_from, '%d-%m-%Y')
                    du_to = datetime.strptime(du_to, '%d-%m-%Y')
                    diff_months = Parser.diff_months(du_from, du_to)
                    duration['du_from'] = datetime.strftime(du_from, '%d-%m-%Y')
                    duration['du_to'] = datetime.strftime(du_to, '%d-%m-%Y')
                    duration['months'] = diff_months - 12 * int(diff_months / 12)
                    duration["years"] = int(diff_months / 12)
                except:
                    pass
                duration_list.append(duration)

            if key == "JOB_TITLE":
                job_title_list.append(val)

            if key == "RELEVANT_JOB_TITLE":
                relevant_job_title_list.append(val)

        project_dict = {
            "id": len(self.projects),
            "passage_id": passage_index,
            "work_duration": duration_list[0] if duration_list else raw_duration,
            "job_title": job_title_list[0] if job_title_list else ["Unknown"],
            "relevant_job_title": relevant_job_title_list[0] if relevant_job_title_list else ["unknown"]
        }

        self.projects.append(project_dict)

    def parse_education(self, passage_index, passage, entity_dict):

        duration_list = []
        raw_duration = {
            "raw": None,
            "du_from": None,
            "du_to": None,
            "months": None,
            "years": None
        }
        for key, val in entity_dict.items():
            if key == "DURATION":
                duration = {
                    "raw": val,
                    "du_from": None,
                    "du_to": None,
                    "months": None,
                    "years": None
                }
                try:
                    du_from, du_to = EntityExtractor.parse_duration(val[0])
                    du_from = datetime.strptime(du_from, '%d-%m-%Y')
                    du_to = datetime.strptime(du_to, '%d-%m-%Y')
                    diff_months = Parser.diff_months(du_from, du_to)
                    duration['du_from'] = datetime.strftime(du_from, '%d-%m-%Y')
                    duration['du_to'] = datetime.strftime(du_to, '%d-%m-%Y')
                    duration['months'] = diff_months - 12 * int(diff_months / 12)
                    duration["years"] = int(diff_months / 12)
                except:
                    pass
                duration_list.append(duration)

        edu_dict = {
            "id": len(self.educations),
            "passage_id": passage_index,
            "education_level": EntityExtractor.get_education_level(passage),
            "gpa": EntityExtractor.get_gpa(passage),
            "edu_duration": duration_list[0] if duration_list else raw_duration,
            "major":"unknown"
        }

        self.educations.append(edu_dict)

    def parse(self, passages, entities, block_types):

        # Parse Date
        today = datetime.today()

        # Parse name
        heading_patterns = TextExtractor.get_pattern_from_file()
        name_list = []
        email = []
        dob = []
        phone_number = []

        # Parse the skill information
        for index in range(len(passages)):
            entity = entities[index]
            block_type = block_types[index]
            passage_content = passages[index][0]

            for key, val in entity.items():
                if key == 'SKILL':
                    self.skills += val
                if key == 'SOFT_SKILL':
                    self.soft_skills += val
                if key == 'LANG_SKILL':
                    self.lang_skills += val
                if key == 'EMAIL':
                    email += val
                if key == 'PHONE_NUMBER':
                    phone_number += val
                if key == 'DATE_OF_BIRTH':
                    dob += val

            only_text_heading = ''.join([e for e in block_type if e.isalpha()])

            if re.search(heading_patterns, block_type.lower()) is None:
                if "-" in block_type:
                    block_type_list = block_type.split("-")
                elif "," in block_type:
                    block_type_list = block_type.split(",")
                else:
                    block_type_list = [block_type]
                name_list += block_type_list

            # Parse Work Experience
            if any([e for e in self.work_experience_headers if e in only_text_heading.lower()]):
                self.parse_experience(index, entity)
                continue

            # Parse Projects
            if any([e for e in self.project_headers if e in only_text_heading.lower()]):
                self.parse_project(index, entity)
                continue

            # Parse Education
            if any([e for e in self.education_headers if e in only_text_heading.lower()]):
                self.parse_education(index, passage_content, entity)
                continue

            if re.search("^summary", block_type):
                self.summary.append(index)

        self.personal_information = {
            "name": name_list[0] if name_list != [] else "Candidate" + str(today.strftime("%d%m%Y")),
            "dob": dob[0] if dob != [] else "",
            "email": email[0] if email else "",
            "phone_number": phone_number[0] if phone_number else "",
            "recent_job_title": self.recent_job_title,
            "year_of_experience": 1
        }
