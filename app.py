from chainlit_process.authentication import *
from chainlit_process.message import *
import alembic.config
from literalai import LiteralClient
from env import env
import subprocess

# init LiteralClient to monitoring and logging OpenAI API calls
client = LiteralClient(api_key=env.LITERAL_API_KEY)
client.instrument_openai() # theo dõi (monitoring) n logging API call to OpenAI ( xem the dashboard của Literal.ai)

# init RQ worker n scheduler to run background tasks and asynchronous operations
rq_command = ["rq", "worker", "--with-scheduler"]
rq_process = subprocess.Popen(
    rq_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

# migrate database with alembic to ensure database is up to date
alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
