#!/usr/bin/env python
import codecs
import os

import json
import urllib.parse
import urllib.request
import urllib.error
from ansible.plugins.action import ActionBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()


class ActionModule(ActionBase):
    """ Returns map of inventory hosts and their associated SCM hostIds """

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        script_path = os.path.dirname(os.path.realpath(__file__))
        default_menu_config_file = os.path.realpath(os.path.join(script_path,
                                                                 "../roles/raptor/templates/config-default.json.j2"))
        nacos_addr = self._task.args.get('nacos_addr')
        nacos_api_url = "http://%s/nacos/v1/cs/configs" % nacos_addr
        data_id = 'raptor'
        group = 'rdx'

        menu_type = self._task.args.get('menu_type', 'default')

        display.display("[%s] 1. Loading existing menu config" % nacos_addr)

        menu_config_url = self.get_config_url(nacos_api_url, data_id, group)

        current_config = self.get_current_config(menu_config_url, ignore_not_found=True)
        if current_config:
            display.display("[%s] 2. Update existing menu config, menu_type=%s" % (nacos_addr, menu_type))
            if menu_type == 'default':
                for module_name in ['comp', 'datahouse', 'dataportal', 'monitor']:
                    filtered_module = [module for module in current_config['moduleServices'] if
                                       module['module'] == module_name]
                    if len(filtered_module) == 0:
                        current_config['moduleServices'].append({"module": module_name})
            elif menu_type == 'datahub':
                if len([module for module in current_config['moduleServices'] if module['module'] == 'datahub']) == 0:
                    current_config['moduleServices'].append({"module": "datahub", "operatorTag": "datahub"})
            elif menu_type == 'metriccube':
                if len([module for module in current_config['moduleServices'] if module['module'] == 'metriccube']) == 0:
                    current_config['moduleServices'].append({"module": "metriccube", "operatorTag": "metriccube"})
            elif menu_type == 'rulecanvas':
                if len([module for module in current_config['moduleServices'] if module['module'] == 'rulecanvas']) == 0:
                    current_config['moduleServices'].append({"module": "rulecanvas", "operatorTag": "rulecanvas"})
            # elif menu_type == 'model':
            #     if len([module for module in current_config['moduleServices'] if module['module'] == 'model']) == 0:
            #         current_config['moduleServices'].append({"module": "model", "operatorTag": "modelware"})
        else:
            display.display("[%s] 2. Create default menu config: '%s'" % (nacos_addr, default_menu_config_file))
            with codecs.open(default_menu_config_file, encoding='utf8') as f:
                default_menu_config = json.load(f)
                current_config = default_menu_config
        # Run Upsert
        data = json.dumps(current_config, ensure_ascii=False).encode('utf-8')
        self.update_menu(nacos_api_url, data_id, group, data)

        # Check result
        display.display("[%s] 3. Check update result of menu config" % nacos_addr)
        current_config2 = None
        import time
        for i in range(10):
            # Wait for config saved...
            display.display("waiting for %s second(s)" % (i + 1))
            time.sleep(1)
            current_config2 = self.get_current_config(menu_config_url)
            if current_config2:
                break

        if not current_config2:
            display.error("[%s] no config found, url=%s" % (nacos_addr, menu_config_url))
            result.update(dict(failed=True))

        return result

    @staticmethod
    def get_config_url(nacos_api_url, data_id, group):
        query_args = dict(dataId=data_id, group=group)
        encoded_args = urllib.parse.urlencode(query_args)
        get_url = "%s?%s" % (nacos_api_url, encoded_args)
        return get_url

    @staticmethod
    def get_current_config(config_url, ignore_not_found=False):
        try:
            with urllib.request.urlopen(config_url) as response:
                menu_data_str = response.read()
                menu_data = json.loads(menu_data_str, encoding='utf-8')
                # print(menu_data)
                return menu_data
        except urllib.error.HTTPError as e:
            if e.code != 404 or (e.code == 404 and not ignore_not_found):
                print("\tThe server couldn't fulfill the request.")
                print('\tError code: ', e.code)
                print('\tResult: ', e.read())
        except urllib.error.URLError as e:
            print('\tWe failed to reach a server.')
            print('\tReason: ', e.reason)
        except Exception as e:
            print('\tUnknown error')
            print(e)

        return None

    @staticmethod
    def update_menu(url, data_id, group, content):
        # Fetch existing config
        query_args = dict(dataId=data_id,
                          group=group,
                          content=content,
                          type='json')
        data = urllib.parse.urlencode(query_args)
        data = data.encode('ascii')
        req = urllib.request.Request(url, data)
        try:
            with urllib.request.urlopen(req) as response:
                response.read()
                # result = response.read()
                # print(result)
                return True
        except urllib.error.HTTPError as e:
            print("\tThe server couldn't fulfill the request.")
            print('\tError code: ', e.code)
            print('\tResult: ', e.read())
        except urllib.error.URLError as e:
            print('\tWe failed to reach a server.')
            print('\tReason: ', e.reason)
        except Exception as e:
            print('\tUnknown error')
            print(e)
        return False
