import json
from pprint import pprint

class Course:

    def __init__(self, course_name):
        # Time slots for each meeting section
        self.meeting_sections_slots = []
        # Section code for each meeting section
        self.meeting_sections_codes = []
        # Exclusive sets, each subset will contain many sections but only one should be picked
        self.meeting_sections_sets = [[] for _ in range(4)] # 0:LEC 1:TUT 2:PRA 3:UNKNOWN

        course = json.load(open('course_data/' + course_name + '.json'))
        # Course code
        self.course_code = course['code']
        # Total number of sections
        self.meeting_sections_count = len(course['meeting_sections'])
        for i in range(self.meeting_sections_count):
            section_set_index = self.convert_section_type_to_num(course['meeting_sections'][i]['code'][:1]) # Get first character of the section code
            self.meeting_sections_sets[section_set_index].append(i)
            times_count = len(course['meeting_sections'][i]['times'])
            time_slots = []
            for j in range(times_count):
                temp = course['meeting_sections'][i]['times'][j]
                time_slots.append((self.convert_day_to_num(temp['day']), self.convert_time_range_to_slot_nums(temp['start'], temp['end'])))
            self.meeting_sections_slots.append(time_slots)
            self.meeting_sections_codes.append(course['meeting_sections'][i]['code'])

    def convert_day_to_num(self, day):
        switcher = {
            "MONDAY" : 0,
            "TUESDAY" : 1,
            "WEDNESDAY" : 2,
            "THURSDAY" : 3,
            "FRIDAY" : 4,
        }
        if day in switcher:
            return switcher[day]
        else:
            raise SystemExit

    def convert_time_range_to_slot_nums(self, start, end):
        slots = []
        slots.extend(list(range(int(start/3600), int(end/3600))))
        return slots

    def convert_section_type_to_num(self, first_char):
        switcher = {
            "L" : 0,
            "T" : 1,
            "P" : 2,
        }
        return switcher.get(first_char, 3)
