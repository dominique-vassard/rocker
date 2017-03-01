import requests


def get_catalog(url, auth_token):
    """Retrieve reporsitories list

    Arguments:
        url (str): Registry host
        auth_token (str): Authorization token

    Returns:
        (list): A list of repositories
    """
    response, _ = get_response(url + '/v2/_catalog', auth_token)
    result = response.get('repositories', [])
    return result


def get_tags_list(url, auth_token, repo_name):
    """Retrieve tags list for the given repository

    Arguments:
        url (str): Registry host
        auth_token (str): Authorization token
        repo_name: A valid repository name

    Returns:
        (list): A list of tags
    """
    response, _ = get_response(url + '/v2/' + repo_name + '/tags/list',
                               auth_token)
    result = response.get('tags', [])
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
        (Exception): If it's not possible to retrieve digest
    """

    # First, we need to get image digest
    add_headers = {
        'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
    }
    manifest_url = url + '/v2/' + repo_name + '/manifests/' + tag
    response, headers = get_response(manifest_url, auth_token,
                                     add_headers=add_headers, verb="HEAD")

    digest = headers.get('Docker-Content-Digest', False)
    if not digest:
        raise Exception('Unable to retrieve digest')

    # And ten delete the image with the retrieved manifest
    delete_url = url + '/v2/' + repo_name + '/manifests/' + digest
    del_response, _ = get_response(delete_url, auth_token, verb="DELETE",
                                   status_ok=202)

    if del_response.get('errors', False):
        errors = del_response.get('errors')
        raise Exception(errors.code + ' -> ' + errors.message)

    return True


def get_response(url, auth_token, add_headers=None, verb="GET", status_ok=200):
    """Calls url ans send json response aif avalaible and headers

    Arguments:
        url (str)- Registry host url
        auth_token (str): THe authorization token

    Keyword Arguments:
        add_headers (dict): Additianl headers (default: None)
        verb (str): The HTTP verb to use (default: "GET")
        status_ok (int): The valid status code (default: 200)

    Returns:
        (tuple): A tuple consisting of:
        ::
            (
                (dict): the json response,
                (dict): the response headers
            )

    Raises:
        (Exception): In case of unknwon verb
        (Exception): In case of bad response status
    """
    headers = {"Authorization": "Basic {}".format(auth_token)}
    if add_headers:
        headers.update(add_headers)

    if verb == "GET":
        response = requests.get(url, headers=headers)
    elif verb == "HEAD":
        response = requests.head(url, headers=headers)
    elif verb == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise Exception("Unknown verb [{}].".format(verb))

    if not response.status_code == status_ok:
        raise response.raise_for_status()

    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    return (resp_json, response.headers)
