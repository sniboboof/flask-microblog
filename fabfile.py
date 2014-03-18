from fabric.api import env
import boto.ec2
from fabric.api import prompt
from fabric.api import sudo
from fabric.api import execute
from fabric.contrib.project import rsync_project
import time
#most of this is taken from the james's fabfile in notetagger

env.hosts = ['localhost', ]

env.aws_region = 'us-west-2'

def new_conn():
    if 'ec2' not in env:
        conn = boto.ec2.connect_to_region(env.aws_region)
        if conn is not None:
            env.ec2 = conn
            print "Connected to ec2 on %s" % env.aws_region
        else:
            msg = 'Unable to connect'
            raise IOError(msg)
    return env.ec2

def new_inst(wait_for_running=True, timeout=60, interval=2):
    wait_val = int(interval)
    timeout_val = int(timeout)
    conn = new_conn()
    instance_type = 't1.micro'
    key_name = 'pk-aws'
    security_group = 'ssh-access'
    image_id = 'ami-c8bed2f8'

    reservations = conn.run_instances(
        image_id,
        key_name=key_name,
        instance_type=instance_type,
        security_groups=[security_group, ]
    )
    new_instances = [i for i in reservations.instances if i.state == u'pending']
    running_instance = []
    if wait_for_running:
        waited = 0
        while new_instances and (waited < timeout_val):
            time.sleep(wait_val)
            waited += int(wait_val)
            for instance in new_instances:
                state = instance.state
                print "Instance %s is %s" % (instance.id, state)
                if state == "running":
                    running_instance.append(
                        new_instances.pop(new_instances.index(i))
                    )
                instance.update()

def list_insts(verbose=False, state='all'):
    conn = new_conn()

    reservations = conn.get_all_reservations()
    instances = []
    for res in reservations:
        for instance in res.instances:
            if state == 'all' or instance.state == state:
                instance = {
                    'id': instance.id,
                    'type': instance.instance_type,
                    'image': instance.image_id,
                    'state': instance.state,
                    'instance': instance,
                }
                instances.append(instance)
    env.instances = instances
    if verbose:
        import pprint
        pprint.pprint(env.instances)


def select_instance(state='running'):
    if env.get('active_instance', False):
        return

    list_insts(state=state)

    prompt_text = "Please select from the following instances:\n"
    instance_template = " %(ct)d: %(state)s instance %(id)s\n"
    for idx, instance in enumerate(env.instances):
        ct = idx + 1
        args = {'ct': ct}
        args.update(instance)
        prompt_text += instance_template % args
    prompt_text += "Choose an instance: "

    def validation(input):
        choice = int(input)
        if not choice in range(1, len(env.instances) + 1):
            raise ValueError("%d is not a valid instance" % choice)
        return choice

    choice = prompt(prompt_text, validate=validation)
    env.active_instance = env.instances[choice - 1]['instance']

def run_command_on_selected_server(command):
    select_instance()
    selected_hosts = [
        'ubuntu@' + env.active_instance.public_dns_name
    ]
    execute(command, hosts=selected_hosts)

def write_nginxconf():
    select_instance()
    addr = env.active_instance.public_dns_name
    nginx_list = []
    nginx_list.append('server {')
    nginx_list.append('    listen 80;')
    nginx_list.append('    server_name ' + addr + ';')
    nginx_list.append('    access_log  /var/log/nginx/test.log;\n')
    nginx_list.append('    location /static/ {')
    nginx_list.append('    \troot /var/www/flask-microblog/;')
    nginx_list.append('    \tautoindex off;')
    nginx_list.append('    }\n')
    nginx_list.append('    location / {')
    nginx_list.append('    \tproxy_pass http://127.0.0.1:8000;')
    nginx_list.append('    \tproxy_set_header Host $host;')
    nginx_list.append('    \tproxy_set_header X-Real-IP $remote_addr;')
    nginx_list.append('    \tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;')
    nginx_list.append('    }')
    nginx_list.append('}')
    nginx_config = '\n'.join(nginx_list)
    with open('flask-microblog/server_config/simple_nginx_config', 'w') as outfile:
            outfile.write(nginx_config)

def _sync_it():
    rsync_project('/home/ubuntu/', 'flask-microblog')
    sudo('mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig')
    sudo('cp flask-microblog/server_config/simple_nginx_config /etc/nginx/sites-available/default')
    #sudo('cp flask-microblog/server_config/note_tagger_gun.conf /etc/supervisor/conf.d/')
    sudo('mkdir /var/www; mkdir /var/www/flask-microblog')
    # sudo('ln -s note-tagger_package/note_tagger/static /var/www/note-tagger/')
    # sudo('cp -r flask-microblog/note_tagger/static /var/www/flask-microblog/')
    # sudo('cd flask-microblog_package/ && python setup.py develop')
    sudo('pip install -r ~/flask-microblog/requirements.txt')

def sync_it():
    run_command_on_selected_server(_sync_it)

def _install_dep():
    sudo('apt-get -y install nginx')
    sudo('apt-get -y install supervisor')
    sudo('apt-get -y install gunicorn')
    sudo('apt-get -y install python-pip')
    sudo('apt-get update')
    sudo('apt-get -y install libpq-dev')
    sudo('apt-get -y install python-dev')
    sudo('apt-get -y install postgresql')
    sudo('apt-get -y upgrade gunicorn')

def install_dep():
    run_command_on_selected_server(_install_dep)

def _start_server():
    sudo('/etc/init.d/nginx start')
    sudo('unlink /run/supervisor.sock')
    sudo('service supervisor stop')
    sudo('service supervisor start')
    sudo('/etc/init.d/supervisor stop')
    sudo('/etc/init.d/supervisor start')

def start_server():
    run_command_on_selected_server(_start_server)

def deploy():
    new_inst()
    time.sleep(15)
    install_dep()
    sync_it()
    write_nginxconf()
    start_server()
    # get_info()

def deploy_existing():
    install_dep()
    sync_it()
    write_nginxconf()
    start_server

def get_info():
    select_instance()
    print(env.active_instance.public_dns_name)

    # path = str(env.active_instance.public_dns_name)
    # run('open http://' + path)

    # print(env.key_filename)


def stop_instance(interval='2'):
    select_instance()
    instance = env.active_instance
    instance.stop()
    wait_val = int(interval)
    while instance.state != 'stopped':
        time.sleep(wait_val)
        print "Instance %s is stopping" % instance.id
        instance.update()
    print "Instance %s is stopped" % instance.id


def terminate_instance(interval='2'):
    select_instance()
    instance = env.active_instance
    instance.terminate()
    # wait_val = int(interval)
    # while instance.state != 'terminated':
    #     time.sleep(wait_val)
    #     print "Instance %s is terminating" % instance.id
    instance.update()
    print(instance.state)
    print "Instance %s is terminated" % instance.id