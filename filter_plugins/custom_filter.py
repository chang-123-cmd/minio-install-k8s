#!/usr/bin/env python
import json


class FilterModule(object):
    def filters(self):
        return {
            'cidr': self.cidr,
            'zk_info': self.zk_info,
            'server_list': self.server_list,
            'local_or_default': self.local_or_default,
            'json_result': self.json_result,
        }

    @staticmethod
    def cidr(ip, netmask):
        return ip + "/" + str(sum(bin(int(x)).count('1') for x in netmask.split('.')))

    @staticmethod
    def zk_info(zookeeper_nodes):
        zookeeper_info = []
        for index, inst in enumerate(zookeeper_nodes.split(',')):
            node_info = inst.split(':')
            zookeeper_info.append(dict(index=index + 1,
                                       host=node_info[0],
                                       port=node_info[1]))
        return zookeeper_info

    @staticmethod
    def server_list(ansible_context, group_name, prefer_ip=False):
        if group_name in ansible_context['groups'] and len(ansible_context['groups']) > 0:
            if prefer_ip:
                return [ip for ip in ansible_context['groups'][group_name]]
            return [ansible_context['hostvars'][ip]['ansible_fqdn'] if ip in ansible_context['hostvars'] else ip
                    for ip in ansible_context['groups'][group_name]]
        else:
            return []

    @staticmethod
    def local_or_default(ansible_context, group_name, prefer_ip=False):
        if group_name in ansible_context['group_names']:
            # Use localhost
            target_ip = ansible_context['inventory_hostname']
        elif group_name in ansible_context['groups'] and len(ansible_context['groups']) > 0:
            # Use first host in group
            target_ip = ansible_context['groups'][group_name][0]
        else:
            # Use inventory_hostname
            target_ip = ansible_context['inventory_hostname']
        if prefer_ip:
            return target_ip
        if not ansible_context['prefer_ip']:
            return ansible_context['hostvars'][target_ip]['ansible_fqdn'] if \
                target_ip in ansible_context['hostvars'] else target_ip
        return target_ip

    @staticmethod
    def json_result(json_str):
        json_result = {}
        try:
            json_result = json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return json_result
