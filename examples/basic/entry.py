import coinstac

from local_pipeline import local
from remote_pipeline import remote

coinstac.start(local, remote)
