import requests


def get_catalog(url, auth_token):
    """Retrieve reporsitories list

    Arguments:
        url (str): Registry host
        auth_token (str): Authorization token

    Returns:
        (list): A list of repositories

    Raises:
        (Exception): In case of bad response status
    """
    response = requests.get(url + '/v2/_catalog',
                            headers={'Authorization': 'Basic ' + auth_token})
    result = []

    if not response.status_code == requests.codes.ok:
        raise response.raise_for_status()

    if response.json().get('repositories'):
        result = response.json().get('repositories')
    return result


def get_tags_list(url, auth_token, repo_name):
    """Retrieve tags list for the given repository

    Arguments:
        url (str): Registry host
        auth_token (str): Authorization token
        repo_name: A valid repository name

    Returns:
        (list): A list of tags

    Raises:
        (Exception): In case of bad response status
    """
    response = requests.get(url + '/v2/' + repo_name + '/tags/list',
                            headers={'Authorization': 'Basic ' + auth_token})
    result = []

    if not response.status_code == requests.codes.ok:
        raise response.raise_for_status()

    if response.json().get('tags'):
        result = response.json().get('tags')
    return result


def delete_image(url, auth_token, repo_name, tag):
    """Delete given image

    Arguments:
        url (str): Registry host
        auth_token (str): Authorization token
        repo_name: A valid repository name
        tag: A valid tag

    Returns:
        (bool): True if success

    Raises:
        (Exception): In case of bad response status
                     If it's not possible to retrieve digest
    """
    headers = {
        'Authorization': 'Basic ' + auth_token,
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
    }
    manifest = requests.get(url + '/v2/' + repo_name + '/manifests/' + tag,
                            headers=headers)

    if not manifest.status_code == requests.codes.ok:
        raise manifest.raise_for_status()

    digest = manifest.headers['Docker-Content-Digest']
    if not digest:
        raise Exception('Unable to retrieve digest')

    delete = requests.delete(url + '/v2/' + repo_name + '/manifests/' + digest,
                             headers={'Authorization': 'Basic ' + auth_token})

    if not delete.status_code == 202:  # This the valid returned status code!
        raise delete.raise_for_status()

    if delete.json().get('errors'):
        errors = delete.json().get('errors')
        print errors
        raise Exception(errors.code + ' -> ' + errors.message)

    return True
