from services.connector_service import get_data
from models.base_model import URL
from config.configuration import config
from services.logging_service import my_logger
import json

def get_account_groups(headers):

    status, account_groups = get_data(headers=headers, endp_url=URL.v7 + "account-groups", params={})

    if "accountGroups" in account_groups and status == 200:

        accounts = {}

        for acc in account_groups["accountGroups"]:

            if acc.get("organizationName") == config.org_name:

                accounts.update({acc.get("accountGroupName"): acc.get("aid")})

        return accounts

    else:

        return "any meel for the dog", False
    

def get_agents_from_label(accounts_names,acc_aids):

    
    labels ={}

    for account in accounts_names:

        #GET LABELS
        aid = acc_aids[account]
        url = f"{URL.v6}groups/agents.json?aid={aid}"
        status,get_labels = get_data(headers=config.headers, endp_url=url, params={})

        
        if status == 200:

            for group in get_labels['groups']:

                if group.get('builtin') == 0:  # Incluir solo si no es una etiqueta predeterminada
                    
                    group_name = group.get('name')
                    group_id = group.get('groupId')
                    group_info = { 
                        'name': group_name,
                        'groupId': group_id
                    }
                    labels[(group_info.get('name'), aid)] = group_info
                        
                    url = f"{URL.v6}groups/{group_id}.json?aid={aid}"
                    status, group_details = get_data(headers=config.headers, endp_url=url, params={})
                    
                    for detail in group_details['groups']:
                        
                        group_info['agents'] = [{'agentId': agent.get('agentId')} for agent in detail.get('agents', [])]


    return labels
