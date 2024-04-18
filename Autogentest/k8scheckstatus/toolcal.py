from langchain_core.tools import tool
from kubernetes import client, config

def podscheck()-> list:
    "kubernetes all pods status in namespace"
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    phases=[]
    for i in ret.items:
         phases.append([i.metadata.name,i.status.phase,])
    
    return phases

def nodescheck()-> list:
    "kubernetes all nodes status in namespace"
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ret = v1.list_node(watch=False)
    items=[]
    
    for i in ret.items:
       items.append([i.metadata.name])
       
    return items 

