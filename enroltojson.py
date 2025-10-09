#script to convert enrollment numbers to json schema, 
#for further push to mongodb

#name,image,college,course,batch,branch
#enrollment,elo,matches,gender
#--------------------------------
#elo is 1200 for all, gender None for now, matches 0 for all
#name : from scraped page, extract regex for name 
#image  : extract url
# course ,batch ,branch,enrollment,college  from csv

import json
import csv

from extract_student_image import extract_student_image_and_name    

with open('enrollments22.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        image,image = extract_student_image_and_name(row[0])
        college = row[3]
        course = row[1]
        batch = row[2]
        branch = row[4]
        enrollment = row[0]
        
    #append to json
        data = {
            "name": name,
            "image": image,
            "college": college,
            "course": course,
            "batch": batch,
            "branch": branch,
            "enrollment": enrollment,
            "elo": 1200,
            "matches": 0,
            "gender": None
        }
        with open('data.json', 'a') as f:
            json.dump(data, f)
            f.write('\n')
