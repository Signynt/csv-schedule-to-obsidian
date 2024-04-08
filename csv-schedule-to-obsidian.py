import csv
import re
import os
from datetime import datetime
import json

class ImportCSV:

    def __init__(self):
        self.csvFiles:list= [] 

        for dirpath, dirnames, files in os.walk("."):
            # print(f"Found directory: {dirnames}, located here:{dirpath}")
            for file_name in files:
                if file_name.endswith(".csv"):
                    normalised_path = os.path.normpath(dirpath + "/" + file_name)
                    # append each found csv file to the list of csv files
                    self.csvFiles.append(normalised_path)

        if not self.csvFiles:
            print("No CSV files found!")
            exit()

        try:
            if not os.path.exists("./output/"):
                os.makedirs("./output/")
        except OSError:
            print ("Error: Creating directory.: ./output/")

        dictionary_titel_txt = './dictionaries/Titel.txt'
        dictionary_ort_txt = './dictionaries/Ort.txt'

        with open(dictionary_titel_txt) as f:
            titel_string = f.read()

        with open(dictionary_ort_txt) as f:
            ort_string = f.read()

        dictionary_titel = json.loads(titel_string)
        dictionary_ort = json.loads(ort_string)

        # dictionary for LV_ART
        dictionary_art = {"VO": "Vorlesung", "SE": "Seminar", "PR": "Praktikum", "FA": "Prüfung"}
        
        duplicate_orts = []

        with open(self.csvFiles[0], mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # skips the first line, since it's the header
            #next(csv_reader)

            for line in csv_reader:
                # reformat dates
                date = datetime.strptime(line['DATUM'], '%d.%m.%Y')
                line['DATUM'] = date.strftime('%Y-%m-%d')

                # splits lists of professors up by '/'
                prof_list = line['VORTRAGENDER_KONTAKTPERSON'].split("/")
                
                # function that reformats names from 'Lastname, Firstname; Doktortitel' to '" - [[Firstname Lastname]]"'
                def reformat_names(input):
                    return re.sub(r"\s?((.*),)\s?(.[^;]*)(.*)", r'\n  - "[[\3 \2]]"', input)

                # reformats name lists and combines them again
                reformated_prof_list = list(map(reformat_names, prof_list))
                professors = ''.join(reformated_prof_list)

                # replace LV_ART entries
                for entry in dictionary_art:
                    line['LV_ART'] = line['LV_ART'].replace(entry, dictionary_art[entry])

                for entry in dictionary_titel:
                    line['TITEL'] = line['TITEL'].replace(entry, dictionary_titel[entry])

                for entry in dictionary_ort:
                    if dictionary_ort[entry]:
                        line['ORT'] = line['ORT'].replace(entry, f"\"[[{dictionary_ort[entry]}]]\"")
                    else:
                        line['ORT'] = line['ORT'].replace(entry, "")

                if line['ORT'] == line['ORT']:
                    duplicate_orts.append(line['ORT'])

                line['ORT'] = re.sub(r"(.*siehe.*)", r"",line['ORT'])

                content = f"---\ntitle: {line['TITEL']}\nallDay: false\nstartTime: {line['VON']}\nendTime: {line['BIS']}\ndate: {line['DATUM']}\nclass-type: {line['LV_ART']}\nlocation: {line['ORT']}\nprofessor: {professors}\ntopic: {line['ANMERKUNG']}\nreviewed: no\n---\n\n"

                fileName = f"./output/{line['DATUM']} {line['TITEL']}.md"
                counter = 2
                while os.path.exists(fileName):
                    fileName = f"./output/{line['DATUM']} {line['TITEL']} {counter}.md"
                    counter += 1

                with open(fileName, "w", encoding='utf-8') as f:
                    f.write(content)

            # content_replaced = [substring.replace("VO", "Vorlesung") for substring in content]
            # print(content[2] + "\n" + fileName)
                
        # Filter the list for duplicates
        unique_orts = list(set(duplicate_orts))

        # Filter the list for entries already in the dictionary
        unique_orts = [ort for ort in unique_orts if ort.strip('"[[').strip(']]"') not in dictionary_ort.values()]

        unique_orts = '\n'.join(unique_orts)

        print(unique_orts)

startScript = ImportCSV()
