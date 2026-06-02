# Get familiar with the configuration of different layers of the stack.

In this session, the goal is to go through the main configuration files and log files of the integration stack.

## Spank plugin

In our case there (meaning the `pasqal-local` qrmi implementation), there not much to configure or mess-up. 

The only parameter that this qrmi implementation need is the address of Warden's API:

```json
{
  "resources": [
    {
      "name": "PASQAL_LOCAL",
      "type": "pasqal-local",
      "environment": {
        "QRMI_URL": "http://localhost:8006"
      }
    }
  ]
}
```

And as a reminder, since the spank plugin is loaded by `slurmstepd` which is spawned by `slurmd` when launching a job step, the spank plugin is going to try to acquire the QPU resources from Warden by running the QRMI api from the compute node.

The Spank plugin fails to acquire the resources from Warden because:
- We fail to setup the right `QRMI_URL` parameter
- Warden API is down
- The job is not running on the QAN where Warden is running (`c1`)

We can simulate this scenario by 
- Modifying the `qrmi_conf.json` file to point `QRMI_URL` to a wrong value
- Running a quantum job like `test_pulser_qrmi.py`

We get the following logs from `slurmd.log`:

```
[2026-06-02T13:45:58.017] [8.batch] error: spank_qrmi, PASQAL_LOCAL is not accessible. error sending request for url (http://localhost:8007/accessible)

Caused by:
    0: client error (Connect)
    1: tcp connect error
    2: Connection refused (os error 111)
[2026-06-02T13:45:58.018] [8.batch] error: spank_qrmi, failed to acquire resource: PASQAL_LOCAL
[2026-06-02T13:45:58.018] [8.batch] error: spank_qrmi, No QPU resource available
```

The QRMI used by the spank plugin is failing to access the configured 

Which is the same error that is going to be raised by the QRMI in the user script:

```
Traceback (most recent call last):
  File "/home/slurmuser/scripts/test_pulser_qrmi.py", line 24, in <module>
    qrmi_conn = PulserQRMIConnection()
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 75, in __init__
    self._qrmi = qrmi or self._resolve_single_resource()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 88, in _resolve_single_resource
    resources = QRMIService().resources()
                ^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/service.py", line 32, in __init__
    raise RuntimeError(plugin_error)
RuntimeError: error sending request for url (http://localhost:8007/accessible)

Caused by:
    0: client error (Connect)
    1: tcp connect error
    2: Connection refused (os error 111)
```

## Warden

Warden is the main point of interaction with cluster administrators for the integration stack. 

There are 2 ways to admin Warden:
- Through the `config.yaml` file 
- With admin `make` targets provided in the `Makefile` located at the root of the Warden installation


### Configuration

When Warden is installed, a `config.yaml` file is created at the root of the installation dir. Each parameter is described and explained by comments.

Any change to the config file requires admins to **restart** Warden to take effect.

There are 5 main sections:
- `api`: configures bind address and host as well as users authorized to call the Warden API (auth managed by munge)
- `database`: configures the Warden DB
- `scheduler`: configures the policies for polling the QPU status and job execution
- `qpu`: defines the QPU API endpoint and retry policy for calls to the API
- `logging`: logging configuration for Python. The configuration is passed as-is to python for logging configuration. Refer to the official [python documentation](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema)

Every parameter in the configuration can be overriden by env variables. For example the `api.port` parameter in `config.yaml` can be overriden by the `WARDEN_API_PORT` env variable. 

So we can set the api port at launch time like:
```
WARDEN_API_PORT=8008 make run
```

#### Set `authorized_users` parameters

The `api` section contains a `authorized_users` parameter. It is a list of user uids authorized to create a new Warden session (meaning "acquiring the QPU resource" for the QRMI lingo)

When it is empty, every user is authorized.

Change it to `[0]` in `config.yaml` to authorize only the root user and restart warden.

Launch a job running the `test_pulser_qrmi.py` script for example as the `slurmuser` user:

```
./login.sh
sbatch scripts/job.sh
```

The job will fail:

```
Traceback (most recent call last):
  File "/home/slurmuser/scripts/test_pulser_qrmi.py", line 15, in <module>
    qrmi_conn = PulserQRMIConnection()
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 75, in __init__
    self._qrmi = qrmi or self._resolve_single_resource()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 88, in _resolve_single_resource
    resources = QRMIService().resources()
                ^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/service.py", line 32, in __init__
    raise RuntimeError(plugin_error)
RuntimeError: Status: 403 Forbidden, Fail {"detail":"User ID not authorized."}
```

And in the Warden logs:

```
INFO warden.api.routes.sessions: Unauthorized user: 1000 attempting to create a session.
```

Now try running the same job as root user with `sudo`:

```
sudo sbatch scripts/jobs.sh
```

And everything goes okay !

| Note: the `authorized_users` parameters is one way to restrict user access to the QPU. We would recommend that user access to the QPU is managed with standard Slurm accounting mechanisms dependending on the solution chosed by the cluster administrators for the QAN setup like GRES or License resources

#### QPU timeout / polling

You can set the parameters for polling and timeout of:
- The status of the QPU before launching a job (is it "UP" ?)
- The status of the job currently running on the QPU

We can try to set the `scheduler.job_polling_timeout_s` parameter to 0 and run a job:

Restart warden with:

```bash
make run
```

Launch a job:

```bash 
sbatch scripts/job.sh
```

The job will fail to fetch the results:

```
Traceback (most recent call last):
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/pulser/backend/remote.py", line 146, in __getattr__
    self._connection._fetch_result(
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 149, in _fetch_result
    raise RemoteResultsError(f"No results found for job {job_id}.")
pulser.backend.remote.RemoteResultsError: No results found for job 4.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/slurmuser/scripts/test_pulser_qrmi.py", line 43, in <module>
    print("results", result.results)
                     ^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/pulser/backend/remote.py", line 102, in results
    return self._results_seq
           ^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/pulser/backend/remote.py", line 152, in __getattr__
    raise RemoteResultsError(
pulser.backend.remote.RemoteResultsError: Results are not available for all jobs. Use the `get_available_results` method to retrieve partial results.
```

| Note: we are currently working on better ways to forward job status and failures from Warden to the user

And in the Warden logs:

```
WARNING warden.scheduler.worker: Job timed out (max 0.0 s). Terminating its associated QPU job 3.
INFO warden.scheduler.worker: Job cancellation done
INFO warden.scheduler: Job 4 ended with status: CANCELED
```


### Admin commands

Warden's makefile provide a single useful administrative command for the moment:
- `set-accessibility`

#### Cut all access to the QPU through Warden

One way to disable all access to the QPU is to set its "accessibility" to false. This can be particularly useful to cut access in case of QPU maintenance.

This will return false everytime a QRMI instance calls the `is_accessible` interface on the `PasqalLocal` resource. 

At the root of the Warden installation (i.e. `$HOME/warden`), run the following command:

```bash
sudo make set-accessible IS_ACCESSIBLE=false MESSAGE="QPU maintenance"
```

Each time you update Warden's accessibility, the value and the message are stored in the `accessibility_settings` table of the db

| Only the root user (admin) is allowed to set the accessibility status of warden. UID is verified by munge. Try to run the command without the sudo

If we try to submit a job to the QPU afterwards, you'll notice that the user script fails to find any QRMI resource as the spank plugin was unable to acquire the QPU:

From the user script output:

```
2026-06-02 14:49:36,677 [DEBUG] qrmi: qpus:
2026-06-02 14:49:36,677 [DEBUG] qrmi: qpu types:
Traceback (most recent call last):
  File "/home/slurmuser/scripts/test_pulser_qrmi.py", line 15, in <module>
    qrmi_conn = PulserQRMIConnection()
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 75, in __init__
    self._qrmi = qrmi or self._resolve_single_resource()
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/slurmuser/venv/lib64/python3.12/site-packages/qrmi/pulser/connection.py", line 92, in _resolve_single_resource
    raise RuntimeError(
RuntimeError: No accessible QRMI resource found. Specify one explicitly with PulserQRMIConnection(qrmi=...).
```

From the `slurmd` logs on `c1`:

```
error: spank_qrmi, PASQAL_LOCAL is not accessible. (null)
error: spank_qrmi, failed to acquire resource: PASQAL_LOCAL
error: spank_qrmi, No QPU resource available
```

### DB

We can also vizualize some data from the Warden DB with the `sqlite-utils` python cli tool:

```bash
source /home/slurmuser/venv/activate
pip install sqlite-utils
```

Checkout the table names:
```
sqlite-utils tables /path/to/warden/warden.db
```

Checkout the sessions table: 
```
sqlite-utils rows /path/to/warden/warden.db sessions
```

Checkout a job in DB:

```
sqlite-utils query /path/to/warden/warden.db "SELECT id, status, started_at, ended_at, results from jobs WHERE id = 1" --fmt table
```

Example output:

```
  id  status    started_at                  ended_at                    results
----  --------  --------------------------  --------------------------  ----------------------------------------------------------------------
   1  DONE      2026-06-01 12:57:26.198493  2026-06-01 12:57:32.149640  {"counter": {"0000": 471, "0100": 9, "0010": 6, "1000": 8, "0001": 6}}
```

