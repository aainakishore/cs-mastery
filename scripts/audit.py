import json, os
base = '/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics'
files_needing_work = [
    ('cloud-devops','aws-mastery.json'),('cloud-devops','aws-practitioner.json'),
    ('cloud-devops','aws-sqs.json'),('cloud-devops','cicd-pipelines.json'),
    ('cloud-devops','cloud-fundamentals.json'),('cloud-devops','docker.json'),
    ('cloud-devops','kubernetes.json'),('cloud-devops','pycharm.json'),
    ('cloud-devops','serverless-patterns.json'),
    ('networking','firewalls.json'),('networking','ftp.json'),
    ('networking','kafka.json'),('networking','load-balancing.json'),
    ('networking','long-polling.json'),('networking','proxies.json'),
    ('networking','rabbitmq.json'),('networking','rate-limiting.json'),
    ('networking','rpc.json'),('networking','websockets.json'),
    ('scaling','caching.json'),('scaling','embedded-databases.json'),
    ('scaling','error-logging.json'),('scaling','partitioning.json'),
    ('scaling','qps-capacity.json'),('scaling','relational-databases.json'),
    ('scaling','sharding.json'),
    ('finance','fin-macroeconomics.json'),('finance','leverage-strategies.json'),
]
for folder, fname in files_needing_work:
    path = f'{base}/{folder}/{fname}'
    if not os.path.exists(path):
        print(f'MISSING: {fname}')
        continue
    d = json.load(open(path))
    ids = [q['id'] for q in d.get('questions',[])]
    fc_ids = [fc['id'] for fc in d.get('flashcards',[])]
    print(f'{fname}: q={ids}, fc={fc_ids}')

