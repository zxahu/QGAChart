__author__ = 'root'

from novaclient.v1_1 import client
from pymongo import MongoClient

user = 'admin'
password = 'ec@openstack'
tenant = 'admin'
auth_url = 'http://10.239.19.216:5000/v2.0/'

db_host = "10.239.20.217"
db_port = 27017
db_name = "qga_data"
collection_name = "q_g_a_data"

# monitoring number on vm, such as memory+ip+load = 3
monitors = 3

class vmInfo():

    hypervisors = []
    servers = []

    def __init__(self):
        self.nt = client.Client(user, password, tenant, auth_url)
        self.mt = MongoClient(db_host,db_port)
        self.db = self.mt[db_name]
        self.collection = self.db[collection_name]

    def getHosts(self):
        hlist = self.nt.hypervisors.list()
        for h in hlist:
            self.hypervisors.append(h.hypervisor_hostname)

    def get_vm(self):
        search_opts = {'all_tenants': '--all-tenants'}
        serversList = self.nt.servers.list(detailed=True, search_opts=search_opts)
        for server in serversList:
            hypervisor =getattr(server,'OS-EXT-SRV-ATTR:hypervisor_hostname')
            instance_name=getattr(server,'OS-EXT-SRV-ATTR:instance_name')
            self.servers.append({"id":server.id,"hypervisor":hypervisor,"instance":"org.qemu.guest_agent.0."+instance_name+".sock"})
        for server in self.servers:
            print server

    def get_vm_info(self,host):
        vms = []
        for server in self.servers:
            if server.hypervisor == host:
                vm = {}
                vm["name"]=server.instance_name
                # get all the monitoring data of the server
                infos = self.collection.find({"guest":server.instance_name}).sort({"timestamp":1}).limit(monitors)
                for info in infos:
                    # create all the monitoring info of a vm
                    vm[info["message"]["action"]] = info["message"]["content"]
                    vms.append(vm)
        # return all the vm info on the host
        return vms



if __name__ == '__main__':
    t = vmInfo()
    t.getHosts()
    t.get_vm()
