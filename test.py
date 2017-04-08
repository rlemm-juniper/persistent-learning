#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import getpass
import time
import argparse
import yaml
import json
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
import traceback
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
import traceback
from jnpr.junos import Device
from jnpr.junos.exception import RpcError
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.exception import RpcError
from jnpr.junos.factory.factory_loader import FactoryLoader

macaddr = 'b8:27:eb:5b:95:96'
dev = Device('192.168.0.126', user='root', password='C0rv3tt3')
dev.open()
print json.dumps(dev.facts)
# dev.rpc.clear_ethernet_switching_table_persistent_learning_mac(address=macaddr)
