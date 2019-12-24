import random
import csv
import os
import random
import sendgrid
import json
from sendgrid.helpers.mail import *
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

sg = sendgrid.SendGridAPIClient('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')
santa_email = 'secretSanta4real@3dx.com'

def html(boy, santa):
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    return j2_env.get_template('mailtemplate.html').render(boy=boy, santa=santa)

def sendEmail(santa, boy, email_map):
    from_email = Email(santa_email)
    to_email = Email(email_map[santa])
    subject = 'Secret Santa 3dx. The Legit One'

    mail_body = html(boy, santa)
    content = Content('text/html', mail_body)
    mail = Mail(from_email=santa_email, to_emails=email_map[santa], subject=subject, html_content=content)

    santa_temp = santa.replace(" ", "_")
    file = open(santa_temp+".html", "w")
    file.write(mail_body)
    file.close()

    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

    return

def initialize_dicts(full_list):
    candidates = {}

    previous_pairs = {
        "sandeep":["abel", "kataria"],
        "abel":["sandeep", "tabish"],
        "kartik": ["adit"],
        "adit": ["sandeep"],
        "tabish": ["cheriano", "hari"],
        "cheriano": ["kataria", "ashik"],
        "kataria":["aman"],
        "aman": ["shyam", "blessen"],
        "shyam": ["blessen", "cheriano"],
        "blessen": ["david", "sidhant"],
        "david": ["hari", "kartik"],
        "hari": ["rameez", "anoop"],
        "rameez": ["arjun", "sai"],
        "arjun": ["anoop", "shyam"],
        "anoop": ["sidhant", "rameez"],
        "sidhant": ["ashik", "abel"],
        "ashik": ["sai", "arjun"],
        "sai": ["tabish", "david"],
        
    }

    previous_pairs1 = {}

    for k, v in previous_pairs.items():
        current_name = [name for name in full_list if k in name.lower()][0]
        previous_pairs1[current_name] = []
        for name in v:
            temp1 = [full_name for full_name in full_list if name in full_name.lower()]
            assert(len(temp1) <= 1)
            if (temp1):
                previous_pairs1[current_name].append(temp1[0])

    #print(previous_pairs1)

    for lad3d in full_list:
        #print(lad3d)
        candidates[lad3d] = [name for name in full_list if (name != lad3d and name not in previous_pairs1[lad3d])]

    return candidates

def secret_santa(full_list, potentials):
    ss_map = {}

    for i in range(len(potentials.keys())):
        #print(i)
        #print(potentials)
        lad = random.choice(list(potentials.keys()))
        #print(lad)
        ss_map[lad] = random.choice(potentials[lad])
        #print(ss_map[lad])
        del potentials[lad]
        potentials = {k: [name for name in v if (name != ss_map[lad])] for k, v in potentials.items()}
        if ss_map[lad] in potentials:
            potentials[ss_map[lad]] = [name for name in potentials[ss_map[lad]] if name != lad]
        #for k, v in potentials.items():
        #    print(k + " " + str(v))
        if(any([len(l) == 0 for l in potentials.keys()])):
            return {}

        #print("")

    return ss_map
    

def main():

    email_map = {}

    with open("data.csv") as f:
        csv_data = csv.reader(f, delimiter=",")
        for row in csv_data:
            email_map[row[0]] = row[2]

    #print(email_map)
            
    full_list = email_map.keys()


    potentials = initialize_dicts(full_list)

    ss_map = secret_santa(full_list, potentials)
    while(not ss_map):
        potentials = initialize_dicts(full_list)
        ss_map = secret_santa(full_list, potentials)

    with open("santa_results.json", "w") as santa_json:
        json.dump(ss_map, santa_json)
    #print(ss_map)
    assert(len(list(ss_map.keys())) == 18)

    for gifter, giftee in ss_map.items():
        sendEmail(gifter, giftee, email_map)

if __name__ == "__main__":
    main()
