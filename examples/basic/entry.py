import coinstac_computation.server as server

from local_pipeline import local
from remote_pipeline import remote

server.start(local.compute, remote.compute)
