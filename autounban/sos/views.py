from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import os, stat, glob, errno
import time
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django.conf import settings
from pathlib import Path
from sos import models as M
import re
from nslookup import Nslookup
import logging, validators

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
__homepath__ = str(Path.home())

ssh_query = r'ssh admin@192.168.88.1 /ip route add dst-address={} gateway=LD8 distance=1 comment=\"{} via autounban\"'
# ssh_query = "echo {} {} > /dev/null"
logging.basicConfig(filename=os.path.join(__location__, '../access.log'), filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
url_regexp = re.compile("(\w+\.)+.\w+")

@login_required
def index(request):
    form = M.ScriptForm(request.POST)
    return render(request, 'sos/index.html', {'form': form})

@login_required
def add(request):
    data = {}
    if request.method == 'POST':
        form = M.ScriptForm(request.POST)
        if form.is_valid():
            ok = True
            journal = ''
            url = form.cleaned_data.get("url")
            m = url_regexp.fullmatch(url)
            valid=validators.url('http://'+url)
            if m is None or not valid:
                ok = False
                journal += f'invalid url: {url}\n'
                data["message"] = 'Invalid URL'
                data["url"] = url
                data["ips"] = []
                data["journal"] = journal
                data["ok"] = False
                logging.info('Invalid URL %s', url)
            else:
                dns_query = Nslookup(dns_servers=["8.8.8.8", "1.1.1.1"])
                ips_record = dns_query.dns_lookup(url)
                ips = ips_record.answer
                for ip in ips:
                    query = ssh_query.format(ip, url)
                    process = subprocess.Popen(query, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    output = process.stdout.readlines()
                    err = process.stderr.readlines()
                    log = b"".join(bytes(x) for x in output)
                    log.strip()
                    log = log.decode('ascii')
                    err_log = b"".join(bytes(x) for x in err)
                    err_log.strip()
                    err_log = err_log.decode('ascii')
                    print(log, err_log)
                    if len(log) != 0 or len(err_log) != 0:
                        ok = False
                        journal += 'ERROR for IP {}\n'.format(ip)
                        journal += log + '\n'
                        journal += err_log + '\n'
                        break
                if ok:
                    data["message"] = 'Success!'
                    data["url"] = url
                    data["ips"] = ips
                    data["ok"] = True
                    ips_str =''.join(str(elem)+' ' for elem in ips)
                    logging.info('added hostname %s with IPs %s', url, ips_str)
                else:
                    data["message"] = 'ERROR!'
                    data["url"] = url
                    data["ips"] = ips
                    data["journal"] = journal
                    data["ok"] = False
                    ips_str =''.join(str(elem)+' ' for elem in ips)
                    logging.info('tried to add hostname %s with IPs %s, err: %s', url, ips_str, log+'\n'+err_log)

    return render(request, 'sos/index.html', {'form': form, 'data': data})

@login_required
def logs(request):
    with open(os.path.join(__location__, '../autounban.log'), 'r') as f:
        logs = f.readlines()
    logs = [x.strip() for x in logs]
    return render(request, 'sos/logs.html', {'logs': logs})
    