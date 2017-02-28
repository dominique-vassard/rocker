# Rocker, the commmand line tool for your Docker registry

rocker is a command line tool that allow to use a private registry via CLI instead of using Docker Registry API.

It is based on [Docker Registry API V2] (https://docs.docker.com/registry/spec/api/)

## Minimum wanted features
- [X] rocker login -> Log into registry (requires docker?)
- [X] rocker logout -> Logout from registry
- [X] option to save credentials
- [ ] rocker ping -> Ping the registry
- [X] rocker catalog -> Return repositories list
- [X] rocker tags <repo_name> -> List all tags of a given repository
- [ ] rocker manifest <repo_name>:<tag> -> get the manifest of a given repository:tag
- [X] rocker delete  <repo_name>:<tag> -> delete the given repository:tag
- [ ] tests
- [ ] Refactor: I have to be clever!